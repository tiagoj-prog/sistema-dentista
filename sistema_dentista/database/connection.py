import os
import sqlite3

from ..config import DATABASE_PATH

BASE_DIR = os.path.abspath(os.path.dirname(str(DATABASE_PATH)))
DB_NAME = str(DATABASE_PATH)


def conectar():
    conexao = sqlite3.connect(
        DB_NAME,
        timeout=30
    )

    conexao.row_factory = sqlite3.Row

    conexao.execute(
        "PRAGMA foreign_keys = ON"
    )

    conexao.execute(
        "PRAGMA busy_timeout = 30000"
    )

    conexao.execute(
        "PRAGMA journal_mode = WAL"
    )

    return conexao

def adicionar_coluna_se_nao_existir(cursor, tabela, coluna, definicao):
    colunas = cursor.execute(f"PRAGMA table_info({tabela})").fetchall()
    nomes = [coluna_db[1] for coluna_db in colunas]

    if coluna not in nomes:
        cursor.execute(
            f"ALTER TABLE {tabela} ADD COLUMN {coluna} {definicao}"
        )


def criar_banco():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT NOT NULL,
            ativo INTEGER NOT NULL DEFAULT 1
        )
    """)

    adicionar_coluna_se_nao_existir(
        cursor, "pacientes", "prontuario", "TEXT DEFAULT ''"
    )
    adicionar_coluna_se_nao_existir(
        cursor, "pacientes", "anamnese", "TEXT DEFAULT ''"
    )
    adicionar_coluna_se_nao_existir(
        cursor, "pacientes", "endereco", "TEXT DEFAULT ''"
    )
    adicionar_coluna_se_nao_existir(
        cursor, "pacientes", "cpf", "TEXT DEFAULT ''"
    )
    adicionar_coluna_se_nao_existir(
        cursor, "pacientes", "rg", "TEXT DEFAULT ''"
    )
    adicionar_coluna_se_nao_existir(
        cursor, "pacientes", "data_nascimento", "TEXT DEFAULT ''"
    )
    adicionar_coluna_se_nao_existir(
        cursor, "pacientes", "tem_responsavel", "INTEGER NOT NULL DEFAULT 0"
    )
    adicionar_coluna_se_nao_existir(
        cursor, "pacientes", "responsavel_nome", "TEXT DEFAULT ''"
    )
    adicionar_coluna_se_nao_existir(
        cursor, "pacientes", "responsavel_cpf", "TEXT DEFAULT ''"
    )
    adicionar_coluna_se_nao_existir(
        cursor, "pacientes", "responsavel_relacao", "TEXT DEFAULT ''"
    )

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS consultas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER NOT NULL,
            data TEXT NOT NULL,
            horario TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Aguardando',
            mensagem_enviada INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (paciente_id) REFERENCES pacientes(id)
        )
    """)

    adicionar_coluna_se_nao_existir(
        cursor, "consultas", "mensagem_enviada",
        "INTEGER NOT NULL DEFAULT 0"
    )

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS odontograma (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER NOT NULL,
            dente TEXT NOT NULL,
            arcada TEXT NOT NULL,
            estado TEXT NOT NULL DEFAULT 'Saudável',
            observacao TEXT DEFAULT '',
            atualizado_em TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(paciente_id, dente),
            FOREIGN KEY (paciente_id) REFERENCES pacientes(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orcamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER NOT NULL,
            categoria TEXT NOT NULL,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL DEFAULT 0,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (paciente_id) REFERENCES pacientes(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contas_receber (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL DEFAULT 0,
            vencimento TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pendente',
            FOREIGN KEY (paciente_id) REFERENCES pacientes(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contas_pagar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            fornecedor TEXT DEFAULT '',
            valor REAL NOT NULL DEFAULT 0,
            vencimento TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pendente'
        )
    """)

    # Colunas que ligam contas a pagar às despesas recorrentes.
    # São adicionadas também em bancos já existentes.
    adicionar_coluna_se_nao_existir(
        cursor, "contas_pagar", "recorrencia_id", "INTEGER"
    )
    adicionar_coluna_se_nao_existir(
        cursor, "contas_pagar", "competencia", "TEXT"
    )

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS despesas_recorrentes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            fornecedor TEXT DEFAULT '',
            categoria TEXT DEFAULT 'Outros',
            valor REAL NOT NULL DEFAULT 0,
            recorrencia TEXT NOT NULL,
            dia_vencimento INTEGER NOT NULL,
            mes_vencimento INTEGER,
            ativa INTEGER NOT NULL DEFAULT 1,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movimentacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            tipo TEXT NOT NULL,
            valor REAL NOT NULL DEFAULT 0,
            data TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS boletos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER,
            conta_receber_id INTEGER,
            valor REAL NOT NULL DEFAULT 0,
            vencimento TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pendente',
            FOREIGN KEY (paciente_id) REFERENCES pacientes(id),
            FOREIGN KEY (conta_receber_id) REFERENCES contas_receber(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notas_fiscais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'Pendente',
            FOREIGN KEY (paciente_id) REFERENCES pacientes(id)
        )
    """)

    conexao.commit()
    conexao.close()
