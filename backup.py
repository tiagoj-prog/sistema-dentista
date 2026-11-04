"""Compatibilidade com a localização antiga de backup.py.

A implementação real está em sistema_dentista.services.backup_service.
"""

from sistema_dentista.services.backup_service import (
    PASTA_BACKUPS,
    _caminho_absoluto_banco,
    _caminho_pasta_backups,
    nome_backup_mes,
    caminho_backup_mes,
    backup_mensal_ja_existe,
    criar_backup_mensal,
    verificar_backup_mensal,
)

__all__ = [
    "PASTA_BACKUPS",
    "_caminho_absoluto_banco",
    "_caminho_pasta_backups",
    "nome_backup_mes",
    "caminho_backup_mes",
    "backup_mensal_ja_existe",
    "criar_backup_mensal",
    "verificar_backup_mensal",
]