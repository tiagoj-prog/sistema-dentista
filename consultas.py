"""Compatibilidade com a localização antiga de consultas.py."""

from sistema_dentista.repositories.appointments_repository import (
    cadastrar_consulta,
    listar_consultas,
    alterar_status,
    obter_consulta,
    marcar_mensagem_enviada,
)

__all__ = [
    "cadastrar_consulta",
    "listar_consultas",
    "alterar_status",
    "obter_consulta",
    "marcar_mensagem_enviada",
]