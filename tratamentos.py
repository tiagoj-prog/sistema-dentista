"""Compatibilidade com a localização antiga de tratamentos.py."""

from sistema_dentista.repositories.treatments_repository import (
    STATUS_TRATAMENTO,
    criar_tabela_tratamentos,
    listar_tratamentos,
    adicionar_tratamento,
    alterar_status_tratamento,
    excluir_tratamento,
)

__all__ = [
    "STATUS_TRATAMENTO",
    "criar_tabela_tratamentos",
    "listar_tratamentos",
    "adicionar_tratamento",
    "alterar_status_tratamento",
    "excluir_tratamento",
]