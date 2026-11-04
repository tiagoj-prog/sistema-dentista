import os
import shutil
import sqlite3
from datetime import date, datetime

from sistema_dentista.config import (
    DATABASE_PATH,
    BACKUP_DIR,
)

PASTA_BACKUPS = "backups"


# =========================================================
# VALIDAÇÃO DE BACKUP
# =========================================================

# Tabelas essenciais do esquema atual. A listagem não exige dados mínimos:
# tabelas legítimamente vazias continuam sendo válidas.
TABELAS_BACKUP_ESSENCIAIS = [
    "pacientes",
    "consultas",
    "agenda_eventos",
    "odontograma",
    "odontograma_faces",
    "odontograma_procedimentos",
    "orcamentos",
    "contas_receber",
    "contas_pagar",
    "movimentacoes",
    "contas_orcamento",
    "itens_conta_orcamento",
    "pagamentos_conta_orcamento",
    "contas_paciente",
    "pagamentos_paciente",
    "quitacoes_paciente",
    "orcamentos_transferidos",
    "boletos",
    "notas_fiscais",
    "despesas_recorrentes",
    "tratamentos",
    "migracoes_sistema",
]


def backup_arquivo_valido(caminho):
    """
    Valida um arquivo como backup utilizável.

    Um arquivo válido deve existir, não estar vazio, abrir como SQLite,
    passar integridade e foreign keys e conter as tabelas essenciais.
    """
    if not isinstance(caminho, (str, bytes, os.PathLike)):
        return False

    if not os.path.exists(caminho):
        return False

    if not os.path.isfile(caminho):
        return False

    try:
        if os.path.getsize(caminho) <= 0:
            return False
    except OSError:
        return False

    try:
        conexao = sqlite3.connect(f"file:{caminho}?mode=ro", uri=True)
    except sqlite3.Error:
        return False

    try:
        integração = conexao.execute("PRAGMA integrity_check").fetchone()
        if not integração or integração[0] != "ok":
            return False

        foreign_keys = conexao.execute("PRAGMA foreign_key_check").fetchall()
        if foreign_keys:
            return False

        tabelas = {
            row[0]
            for row in conexao.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                """
            ).fetchall()
        }

        if not all(tabela in tabelas for tabela in TABELAS_BACKUP_ESSENCIAIS):
            return False

        return True
    except (sqlite3.Error, OSError):
        return False
    finally:
        try:
            conexao.close()
        except Exception:
            pass


def _caminho_absoluto_banco():
    return os.path.abspath(str(DATABASE_PATH))


def _caminho_pasta_backups():
    pasta = os.path.abspath(str(BACKUP_DIR))

    os.makedirs(
        pasta,
        exist_ok=True,
    )

    return pasta


# =========================================================
# NOME E CAMINHO DO BACKUP
# =========================================================

def nome_backup_mes(data_referencia=None):
    hoje = data_referencia or date.today()

    return (
        f"dentista_"
        f"{hoje.year:04d}-"
        f"{hoje.month:02d}.db"
    )


def caminho_backup_mes(data_referencia=None):
    return os.path.join(
        _caminho_pasta_backups(),
        nome_backup_mes(data_referencia),
    )


def backup_mensal_ja_existe(data_referencia=None):
    return backup_arquivo_valido(
        caminho_backup_mes(data_referencia)
    )


def _quarentena_backup(caminho_invalido):
    """
    Preserva um backup inválido antes de substituí-lo.
    """
    base = os.path.splitext(caminho_invalido)[0]
    extensao = os.path.splitext(caminho_invalido)[1] or ".db"
    momento = datetime.now().strftime("%Y%m%d_%H%M%S")

    for tentativa in range(100):
        sufixo = momento if tentativa == 0 else f"{momento}_{tentativa}"
        candidato = f"{base}.invalido_{sufixo}{extensao}"
        if not os.path.exists(candidato):
            os.replace(caminho_invalido, candidato)
            return candidato

    raise RuntimeError("Não foi possível criar arquivo de quarentena para backup inválido.")


def _temporario_backup():
    pasta = _caminho_pasta_backups()
    momento = datetime.now().strftime("%Y%m%d_%H%M%S%f")
    return os.path.join(
        pasta,
        f"dentista_temp_{momento}.db",
    )


def criar_backup_mensal(forcar=False):
    origem = _caminho_absoluto_banco()
    destino = caminho_backup_mes()

    if not os.path.exists(origem):
        return {
            "criado": False,
            "arquivo": destino,
            "mensagem": "Banco de dados ainda não existe.",
        }

    if forcar is False and backup_arquivo_valido(destino):
        return {
            "criado": False,
            "arquivo": destino,
            "mensagem": "Backup deste mês já existe e é válido.",
        }

    os.makedirs(
        os.path.dirname(destino),
        exist_ok=True,
    )

    # Se o arquivo mensal existe mas não é utilizável, preserva-o em
    # quarentena antes de substituí-lo. Nunca substitui um backup válido.
    if os.path.exists(destino) and not backup_arquivo_valido(destino):
        _quarentena_backup(destino)

    temporario = _temporario_backup()
    temporario_existe = False

    try:
        origem_db = sqlite3.connect(
            origem,
            timeout=30,
        )

        try:
            destino_db = sqlite3.connect(
                temporario,
                timeout=30,
            )
            temporario_existe = True

            try:
                origem_db.backup(destino_db)
                destino_db.commit()
            finally:
                destino_db.close()
        finally:
            origem_db.close()

        if not backup_arquivo_valido(temporario):
            raise RuntimeError("O backup temporário gerado não é válido.")

        if os.path.exists(destino):
            os.remove(destino)

        os.replace(temporario, destino)
        temporario_existe = False

        return {
            "criado": True,
            "arquivo": destino,
            "mensagem": "Backup mensal criado com sucesso.",
        }

    except Exception:
        for _arquivo_temporario in (temporario, temporario + "-wal", temporario + "-shm", temporario + "-journal"):
            if os.path.exists(_arquivo_temporario):
                try:
                    os.remove(_arquivo_temporario)
                except OSError:
                    pass
        raise

    finally:
        for _arquivo_temporario in (temporario, temporario + "-wal", temporario + "-shm", temporario + "-journal"):
            if os.path.exists(_arquivo_temporario):
                try:
                    os.remove(_arquivo_temporario)
                except OSError:
                    pass


def verificar_backup_mensal():
    return criar_backup_mensal(
        forcar=False,
    )