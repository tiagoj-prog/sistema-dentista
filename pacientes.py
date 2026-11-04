"""Compatibilidade com a localização antiga de pacientes.py."""

from sistema_dentista.repositories.patients_repository import (
    _garantir_campos_identificacao,
    cadastrar_paciente,
    listar_pacientes,
    listar_todos_pacientes,
    obter_paciente,
    atualizar_paciente,
    desativar_paciente,
    ativar_paciente,
    excluir_paciente_permanentemente,
)

__all__ = [
    "_garantir_campos_identificacao",
    "cadastrar_paciente",
    "listar_pacientes",
    "listar_todos_pacientes",
    "obter_paciente",
    "atualizar_paciente",
    "desativar_paciente",
    "ativar_paciente",
    "excluir_paciente_permanentemente",
]
