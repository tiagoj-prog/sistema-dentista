"""Conexão e estrutura do banco de dados do Sistema Dentista."""

from .connection import (
    BASE_DIR,
    DB_NAME,
    conectar,
    adicionar_coluna_se_nao_existir,
    criar_banco,
)

__all__ = [
    "BASE_DIR",
    "DB_NAME",
    "conectar",
    "adicionar_coluna_se_nao_existir",
    "criar_banco",
]
