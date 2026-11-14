import os
import shutil
from pathlib import Path

from ..database.connection import conectar
from ..config import PROJECT_ROOT

PASTA_UPLOADS = PROJECT_ROOT / "uploads"


def _garantir_pasta():
    PASTA_UPLOADS.mkdir(parents=True, exist_ok=True)


def listar_anexos(paciente_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, paciente_id, nome_original, nome_arquivo, tipo, tamanho, criado_em
        FROM anexos
        WHERE paciente_id = ?
        ORDER BY criado_em DESC, id DESC
    """, (paciente_id,))

    registros = cursor.fetchall()
    conexao.close()
    return registros


def adicionar_anexo(paciente_id, nome_original, nome_arquivo, tipo="", tamanho=0):
    _garantir_pasta()

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO anexos (paciente_id, nome_original, nome_arquivo, tipo, tamanho)
        VALUES (?, ?, ?, ?, ?)
    """, (paciente_id, nome_original, nome_arquivo, tipo, tamanho))

    conexao.commit()
    conexao.close()


def excluir_anexo(anexo_id, paciente_id):
    conexao = conectar()
    cursor = conexao.cursor()

    registro = cursor.execute("""
        SELECT nome_arquivo
        FROM anexos
        WHERE id = ? AND paciente_id = ?
    """, (anexo_id, paciente_id)).fetchone()

    if registro is None:
        conexao.close()
        raise ValueError("Anexo não encontrado.")

    nome_arquivo = registro["nome_arquivo"]

    cursor.execute("""
        DELETE FROM anexos
        WHERE id = ? AND paciente_id = ?
    """, (anexo_id, paciente_id))

    conexao.commit()
    conexao.close()

    caminho = PASTA_UPLOADS / nome_arquivo
    try:
        if caminho.exists():
            caminho.unlink()
    except OSError:
        pass


def caminho_anexo(nome_arquivo):
    return PASTA_UPLOADS / nome_arquivo
