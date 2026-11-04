"""Compatibilidade com a localização antiga de banco.py.

A implementação real está em sistema_dentista.database.connection.
"""

from sistema_dentista.database import (
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