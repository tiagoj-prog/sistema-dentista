"""Compatibilidade com a localização antiga de agenda_visual.py."""

from sistema_dentista.repositories.agenda_repository import (
    CORES_VALIDAS,
    STATUS_VALIDOS,
    criar_tabela_agenda_visual,
    _segunda_feira,
    _horarios,
    listar_eventos_periodo,
    preparar_agenda_semana,
    adicionar_evento,
    alterar_status_evento,
    obter_evento,
    excluir_evento,
)

__all__ = [
    "CORES_VALIDAS",
    "STATUS_VALIDOS",
    "criar_tabela_agenda_visual",
    "_segunda_feira",
    "_horarios",
    "listar_eventos_periodo",
    "preparar_agenda_semana",
    "adicionar_evento",
    "alterar_status_evento",
    "obter_evento",
    "excluir_evento",
]