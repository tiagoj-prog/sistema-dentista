"""Cálculos e montagem de resumos financeiros.

Este serviço centraliza apenas agregações que estavam nas rotas. Ele não
altera dados, não acessa o banco diretamente e não duplica os cálculos na
camada de apresentação.
"""

from datetime import date

from ..repositories.appointments_repository import listar_consultas
from ..repositories.financial_repository import (
    listar_anos_gastos,
    listar_contas_pagar,
    listar_contas_receber,
    listar_despesas_recorrentes,
    listar_movimentacoes_mes,
    resumo_gastos_anuais,
    resumo_gastos_mensais,
)
from ..repositories.patients_repository import listar_pacientes


def _float(valor):
    try:
        return float(str(valor).replace(",", "."))
    except (ValueError, TypeError):
        return 0.0


def calcular_resumo_dashboard():
    consultas = listar_consultas()
    pacientes = listar_pacientes()

    receber = listar_contas_receber()
    pagar = listar_contas_pagar()

    total = len(consultas)
    confirmadas = sum(
        1
        for consulta in consultas
        if consulta["status"] == "Confirmada"
    )
    aguardando = sum(
        1
        for consulta in consultas
        if consulta["status"] == "Aguardando"
    )
    canceladas = sum(
        1
        for consulta in consultas
        if consulta["status"] == "Cancelada"
    )

    total_receber = sum(
        conta["valor"]
        for conta in receber
        if conta["status"] != "Pago"
    )

    total_pagar = sum(
        conta["valor"]
        for conta in pagar
        if conta["status"] != "Pago"
    )

    return {
        "total": total,
        "confirmadas": confirmadas,
        "aguardando": aguardando,
        "canceladas": canceladas,
        "total_pacientes": len(pacientes),
        "total_receber": total_receber,
        "total_pagar": total_pagar,
    }


def carregar_dados_financeiros(ano_solicitado=None):
    hoje_data = date.today()

    receber = listar_contas_receber()
    pagar = listar_contas_pagar()

    movimentacoes = listar_movimentacoes_mes(
        hoje_data.year,
        hoje_data.month,
    )

    despesas_recorrentes = listar_despesas_recorrentes()
    pacientes = listar_pacientes()

    total_receber = sum(
        _float(item["valor"] or 0)
        for item in receber
        if item["status"] != "Pago"
    )

    total_pagar = sum(
        _float(item["valor"] or 0)
        for item in pagar
        if item["status"] != "Pago"
    )

    entradas = sum(
        _float(item["valor"] or 0)
        for item in movimentacoes
        if item["tipo"] == "Entrada"
    )

    saidas = sum(
        _float(item["valor"] or 0)
        for item in movimentacoes
        if item["tipo"] == "Saída"
    )

    saldo = entradas - saidas

    anos_gastos = listar_anos_gastos()

    try:
        ano_selecionado = int(
            ano_solicitado
            if ano_solicitado is not None
            else hoje_data.year
        )
    except (TypeError, ValueError):
        ano_selecionado = hoje_data.year

    if ano_selecionado not in anos_gastos:
        anos_gastos.append(ano_selecionado)
        anos_gastos = sorted(
            set(anos_gastos),
            reverse=True,
        )

    gastos_mensais = resumo_gastos_mensais(
        ano_selecionado
    )

    gastos_anuais = resumo_gastos_anuais()

    total_gastos_ano = sum(
        item["total"]
        for item in gastos_mensais
    )

    total_gastos_ano_pago = sum(
        item["pago"]
        for item in gastos_mensais
    )

    total_gastos_ano_pendente = sum(
        item["pendente"]
        for item in gastos_mensais
    )

    total_entradas_ano = sum(
        item["entradas"]
        for item in gastos_mensais
    )

    total_saidas_ano = sum(
        item["saidas"]
        for item in gastos_mensais
    )

    saldo_fluxo_ano = (
        total_entradas_ano
        - total_saidas_ano
    )

    return {
        "receber": receber,
        "pagar": pagar,
        "movimentacoes": movimentacoes,
        "despesas_recorrentes": despesas_recorrentes,
        "pacientes": pacientes,
        "total_receber": total_receber,
        "total_pagar": total_pagar,
        "entradas": entradas,
        "saidas": saidas,
        "saldo": saldo,
        "anos_gastos": anos_gastos,
        "ano_selecionado": ano_selecionado,
        "gastos_mensais": gastos_mensais,
        "gastos_anuais": gastos_anuais,
        "total_gastos_ano": total_gastos_ano,
        "total_gastos_ano_pago": total_gastos_ano_pago,
        "total_gastos_ano_pendente": total_gastos_ano_pendente,
        "total_entradas_ano": total_entradas_ano,
        "total_saidas_ano": total_saidas_ano,
        "saldo_fluxo_ano": saldo_fluxo_ano,
        "hoje_data": hoje_data,
    }