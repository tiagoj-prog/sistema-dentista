"""Validações de dados do Sistema Dentista."""

import re


def _somente_digitos(valor):
    return re.sub(r"\D", "", valor or "")


def validar_cpf(cpf):
    """Valida um CPF brasileiro (dígitos verificadores).

    Aceita com ou sem máscara. CPF vazio é considerado válido
    (campo opcional).
    """
    digitos = _somente_digitos(cpf)

    if not digitos:
        return True

    if len(digitos) != 11:
        return False

    # Rejeita CPFs com todos os dígitos iguais.
    if len(set(digitos)) == 1:
        return False

    # Primeiro dígito verificador.
    soma = sum(int(digitos[i]) * (10 - i) for i in range(9))
    resto = (soma * 10) % 11
    if resto == 10:
        resto = 0
    if resto != int(digitos[9]):
        return False

    # Segundo dígito verificador.
    soma = sum(int(digitos[i]) * (11 - i) for i in range(10))
    resto = (soma * 10) % 11
    if resto == 10:
        resto = 0
    if resto != int(digitos[10]):
        return False

    return True


def validar_telefone(telefone):
    """Valida um telefone brasileiro.

    Aceita formatos com ou sem máscara. Telefone vazio é inválido
    (campo obrigatório).
    """
    digitos = _somente_digitos(telefone)

    if not digitos:
        return False

    # DDD (2 dígitos) + número (8 ou 9 dígitos).
    if len(digitos) not in (10, 11):
        return False

    ddd = int(digitos[:2])
    if ddd < 11 or ddd > 99:
        return False

    # Celular começa com 9 (9 dígitos após DDD).
    if len(digitos) == 11 and digitos[2] != "9":
        return False

    return True


def formatar_cpf(cpf):
    """Remove máscara e retorna apenas os dígitos."""
    return _somente_digitos(cpf)


def formatar_telefone(telefone):
    """Remove máscara e retorna apenas os dígitos."""
    return _somente_digitos(telefone)
