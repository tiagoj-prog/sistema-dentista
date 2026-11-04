"""Compatibilidade com a localização antiga de odontograma.py."""

from sistema_dentista.repositories.odontogram_repository import (
    ESTADOS_VALIDOS,
    formatar_data_local,
    criar_tabela_odontograma,
    _arcada_do_dente,
    listar_odontograma,
    salvar_dente,
    listar_faces_odontograma,
    salvar_face_odontograma,
    listar_procedimentos_odontograma,
    adicionar_procedimento_odontograma,
    excluir_procedimento_odontograma,
)

__all__ = [
    "ESTADOS_VALIDOS",
    "formatar_data_local",
    "criar_tabela_odontograma",
    "_arcada_do_dente",
    "listar_odontograma",
    "salvar_dente",
    "listar_faces_odontograma",
    "salvar_face_odontograma",
    "listar_procedimentos_odontograma",
    "adicionar_procedimento_odontograma",
    "excluir_procedimento_odontograma",
]
