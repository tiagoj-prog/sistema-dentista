from ..database.connection import conectar


def _float(valor):
    try:
        return float(str(valor).replace(",", "."))
    except (ValueError, TypeError):
        return 0.0


# -------------------------
# ORÇAMENTOS
# -------------------------

def listar_orcamentos(paciente_id=None):
    conexao = conectar()
    cursor = conexao.cursor()

    if paciente_id:
        cursor.execute("""
            SELECT
                orcamentos.*,
                pacientes.nome AS paciente_nome
            FROM orcamentos
            INNER JOIN pacientes
                ON pacientes.id = orcamentos.paciente_id
            WHERE orcamentos.paciente_id = ?
            ORDER BY orcamentos.id DESC
        """, (paciente_id,))
    else:
        cursor.execute("""
            SELECT
                orcamentos.*,
                pacientes.nome AS paciente_nome
            FROM orcamentos
            INNER JOIN pacientes
                ON pacientes.id = orcamentos.paciente_id
            ORDER BY orcamentos.id DESC
        """)

    registros = cursor.fetchall()
    conexao.close()
    return registros


def adicionar_orcamento(paciente_id, categoria, descricao, valor):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO orcamentos
        (paciente_id, categoria, descricao, valor)
        VALUES (?, ?, ?, ?)
    """, (
        paciente_id,
        categoria,
        descricao,
        _float(valor)
    ))

    conexao.commit()
    conexao.close()


def excluir_orcamento(orcamento_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        DELETE FROM orcamentos
        WHERE id = ?
    """, (orcamento_id,))

    conexao.commit()
    conexao.close()


# -------------------------
# CONTAS A RECEBER
# -------------------------

def listar_contas_receber():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            contas_receber.*,
            pacientes.nome AS paciente_nome
        FROM contas_receber
        LEFT JOIN pacientes
            ON pacientes.id = contas_receber.paciente_id
        WHERE contas_receber.status != 'Pago'
          AND contas_receber.valor > 0.000001
        ORDER BY contas_receber.vencimento, contas_receber.id DESC
    """)

    registros = cursor.fetchall()
    conexao.close()
    return registros


def adicionar_conta_receber(paciente_id, descricao, valor, vencimento):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO contas_receber
        (paciente_id, descricao, valor, vencimento, status)
        VALUES (?, ?, ?, ?, 'Pendente')
    """, (
        paciente_id or None,
        descricao,
        _float(valor),
        vencimento
    ))

    conexao.commit()
    conexao.close()


def marcar_receber_pago(conta_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE contas_receber
        SET status = 'Pago'
        WHERE id = ?
    """, (conta_id,))

    conexao.commit()
    conexao.close()


def excluir_conta_receber(conta_id):
    conexao = conectar()
    cursor = conexao.cursor()

    # Se existir boleto ligado à conta, preserva o boleto e remove apenas o vínculo.
    cursor.execute("""
        UPDATE boletos
        SET conta_receber_id = NULL
        WHERE conta_receber_id = ?
    """, (conta_id,))

    cursor.execute("""
        DELETE FROM contas_receber
        WHERE id = ?
    """, (conta_id,))

    conexao.commit()
    conexao.close()


# -------------------------
# CONTAS A PAGAR
# -------------------------

def listar_contas_pagar():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT *
        FROM contas_pagar
        ORDER BY vencimento, id DESC
    """)

    registros = cursor.fetchall()
    conexao.close()
    return registros


def adicionar_conta_pagar(descricao, fornecedor, valor, vencimento):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO contas_pagar
        (descricao, fornecedor, valor, vencimento, status)
        VALUES (?, ?, ?, ?, 'Pendente')
    """, (
        descricao,
        fornecedor,
        _float(valor),
        vencimento
    ))

    conexao.commit()
    conexao.close()


def marcar_pagar_pago(conta_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE contas_pagar
        SET status = 'Pago'
        WHERE id = ?
    """, (conta_id,))

    conexao.commit()
    conexao.close()


def excluir_conta_pagar(conta_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        DELETE FROM contas_pagar
        WHERE id = ?
    """, (conta_id,))

    conexao.commit()
    conexao.close()


# -------------------------
# FLUXO DE CAIXA
# -------------------------

def listar_movimentacoes():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT *
        FROM movimentacoes
        ORDER BY data DESC, id DESC
    """)

    registros = cursor.fetchall()
    conexao.close()
    return registros


def listar_movimentacoes_mes(ano=None, mes=None):
    """
    Retorna apenas as movimentações do mês informado.

    Se ano/mes não forem passados, usa o mês atual.
    Isso faz a Visão geral "zerar" automaticamente no dia 1,
    sem apagar nenhum registro do banco.
    """
    hoje = date.today()

    try:
        ano = int(ano) if ano is not None else hoje.year
        mes = int(mes) if mes is not None else hoje.month
    except (TypeError, ValueError):
        ano = hoje.year
        mes = hoje.month

    if mes < 1 or mes > 12:
        mes = hoje.month

    prefixo = f"{ano:04d}-{mes:02d}"

    conexao = conectar()
    cursor = conexao.cursor()

    registros = cursor.execute("""
        SELECT *
        FROM movimentacoes
        WHERE substr(data, 1, 7) = ?
        ORDER BY data DESC, id DESC
    """, (prefixo,)).fetchall()

    conexao.close()
    return registros


def adicionar_movimentacao(descricao, tipo, valor, data):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO movimentacoes
        (descricao, tipo, valor, data)
        VALUES (?, ?, ?, ?)
    """, (
        descricao,
        tipo,
        _float(valor),
        data
    ))

    conexao.commit()
    conexao.close()


def excluir_movimentacao(movimentacao_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        DELETE FROM movimentacoes
        WHERE id = ?
    """, (movimentacao_id,))

    conexao.commit()
    conexao.close()


# -------------------------
# BOLETOS / NOTAS
# -------------------------

def listar_boletos():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            boletos.*,
            pacientes.nome AS paciente_nome
        FROM boletos
        LEFT JOIN pacientes
            ON pacientes.id = boletos.paciente_id
        ORDER BY boletos.id DESC
    """)

    registros = cursor.fetchall()
    conexao.close()
    return registros


def registrar_boleto(paciente_id, conta_receber_id, valor, vencimento):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO boletos
        (paciente_id, conta_receber_id, valor, vencimento, status)
        VALUES (?, ?, ?, ?, 'Pendente')
    """, (
        paciente_id or None,
        conta_receber_id or None,
        _float(valor),
        vencimento
    ))

    conexao.commit()
    conexao.close()


def excluir_boleto(boleto_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        DELETE FROM boletos
        WHERE id = ?
    """, (boleto_id,))

    conexao.commit()
    conexao.close()


def listar_notas_fiscais():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            notas_fiscais.*,
            pacientes.nome AS paciente_nome
        FROM notas_fiscais
        LEFT JOIN pacientes
            ON pacientes.id = notas_fiscais.paciente_id
        ORDER BY notas_fiscais.id DESC
    """)

    registros = cursor.fetchall()
    conexao.close()
    return registros


def registrar_nota_fiscal(paciente_id, descricao, valor):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO notas_fiscais
        (paciente_id, descricao, valor, status)
        VALUES (?, ?, ?, 'Pendente')
    """, (
        paciente_id or None,
        descricao,
        _float(valor)
    ))

    conexao.commit()
    conexao.close()


def excluir_nota_fiscal(nota_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        DELETE FROM notas_fiscais
        WHERE id = ?
    """, (nota_id,))

    conexao.commit()
    conexao.close()

# -------------------------
# DESPESAS RECORRENTES
# -------------------------

from calendar import monthrange
from datetime import date


def listar_despesas_recorrentes():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT *
        FROM despesas_recorrentes
        ORDER BY ativa DESC, recorrencia, descricao
    """)

    registros = cursor.fetchall()
    conexao.close()
    return registros


def adicionar_despesa_recorrente(
    descricao,
    fornecedor,
    categoria,
    valor,
    recorrencia,
    dia_vencimento,
    mes_vencimento=None
):
    recorrencia = (recorrencia or "").strip().capitalize()

    if recorrencia not in ["Mensal", "Anual"]:
        raise ValueError("Recorrência inválida.")

    try:
        dia_vencimento = int(dia_vencimento)
    except (TypeError, ValueError):
        raise ValueError("Dia de vencimento inválido.")

    if dia_vencimento < 1 or dia_vencimento > 31:
        raise ValueError("O dia de vencimento deve estar entre 1 e 31.")

    if recorrencia == "Anual":
        try:
            mes_vencimento = int(mes_vencimento)
        except (TypeError, ValueError):
            raise ValueError("Mês de vencimento inválido.")

        if mes_vencimento < 1 or mes_vencimento > 12:
            raise ValueError("O mês de vencimento deve estar entre 1 e 12.")
    else:
        mes_vencimento = None

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO despesas_recorrentes
        (
            descricao,
            fornecedor,
            categoria,
            valor,
            recorrencia,
            dia_vencimento,
            mes_vencimento,
            ativa
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, 1)
    """, (
        descricao,
        fornecedor,
        categoria,
        _float(valor),
        recorrencia,
        dia_vencimento,
        mes_vencimento
    ))

    conexao.commit()
    conexao.close()


def alterar_status_despesa_recorrente(despesa_id, ativa):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE despesas_recorrentes
        SET ativa = ?
        WHERE id = ?
    """, (1 if ativa else 0, despesa_id))

    conexao.commit()
    conexao.close()


def excluir_despesa_recorrente(despesa_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        DELETE FROM despesas_recorrentes
        WHERE id = ?
    """, (despesa_id,))

    conexao.commit()
    conexao.close()


def _data_vencimento_segura(ano, mes, dia):
    ultimo_dia = monthrange(ano, mes)[1]
    return date(ano, mes, min(dia, ultimo_dia))


def sincronizar_despesas_recorrentes(data_referencia=None):
    """
    Gera automaticamente em contas_pagar a despesa referente ao ciclo atual.
    Não duplica lançamentos porque usa recorrencia_id + competencia.
    """
    hoje = data_referencia or date.today()
    conexao = conectar()
    cursor = conexao.cursor()

    despesas = cursor.execute("""
        SELECT *
        FROM despesas_recorrentes
        WHERE ativa = 1
    """).fetchall()

    geradas = 0

    for despesa in despesas:
        recorrencia = despesa["recorrencia"]
        dia = int(despesa["dia_vencimento"])

        if recorrencia == "Mensal":
            mes = hoje.month
            ano = hoje.year
            competencia = f"{ano:04d}-{mes:02d}"
            vencimento = _data_vencimento_segura(ano, mes, dia)

        elif recorrencia == "Anual":
            mes = int(despesa["mes_vencimento"])
            ano = hoje.year
            competencia = f"{ano:04d}"
            vencimento = _data_vencimento_segura(ano, mes, dia)

        else:
            continue

        existe = cursor.execute("""
            SELECT id
            FROM contas_pagar
            WHERE recorrencia_id = ?
              AND competencia = ?
            LIMIT 1
        """, (
            despesa["id"],
            competencia
        )).fetchone()

        if existe:
            continue

        cursor.execute("""
            INSERT INTO contas_pagar
            (
                descricao,
                fornecedor,
                valor,
                vencimento,
                status,
                recorrencia_id,
                competencia
            )
            VALUES (?, ?, ?, ?, 'Pendente', ?, ?)
        """, (
            despesa["descricao"],
            despesa["fornecedor"],
            despesa["valor"],
            vencimento.isoformat(),
            despesa["id"],
            competencia
        ))

        geradas += 1

    conexao.commit()
    conexao.close()
    return geradas

# =========================================================
# CONTA INDIVIDUAL DO PACIENTE / PAGAMENTOS PARCIAIS
# =========================================================

def _coluna_existe(cursor, tabela, coluna):
    colunas = cursor.execute(
        f"PRAGMA table_info({tabela})"
    ).fetchall()

    return coluna in [item[1] for item in colunas]


def criar_tabelas_conta_paciente():
    """
    Cria a conta consolidada de cada paciente, o histórico de pagamentos
    e o controle dos itens de orçamento já enviados para a conta.
    """
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contas_paciente (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER NOT NULL UNIQUE,
            valor_total REAL NOT NULL DEFAULT 0,
            saldo REAL NOT NULL DEFAULT 0,
            conta_receber_id INTEGER,
            vencimento TEXT DEFAULT '',
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
            atualizado_em TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (paciente_id) REFERENCES pacientes(id),
            FOREIGN KEY (conta_receber_id) REFERENCES contas_receber(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pagamentos_paciente (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conta_paciente_id INTEGER NOT NULL,
            paciente_id INTEGER NOT NULL,
            valor REAL NOT NULL,
            data_pagamento TEXT NOT NULL,
            observacao TEXT DEFAULT '',
            movimentacao_id INTEGER,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conta_paciente_id) REFERENCES contas_paciente(id),
            FOREIGN KEY (paciente_id) REFERENCES pacientes(id),
            FOREIGN KEY (movimentacao_id) REFERENCES movimentacoes(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orcamentos_transferidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            orcamento_id INTEGER NOT NULL UNIQUE,
            conta_paciente_id INTEGER NOT NULL,
            valor_transferido REAL NOT NULL,
            data_transferencia TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conta_paciente_id) REFERENCES contas_paciente(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quitacoes_paciente (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conta_paciente_id INTEGER NOT NULL,
            paciente_id INTEGER NOT NULL,
            valor_quitado REAL NOT NULL DEFAULT 0,
            data_quitacao TEXT NOT NULL,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conta_paciente_id) REFERENCES contas_paciente(id),
            FOREIGN KEY (paciente_id) REFERENCES pacientes(id)
        )
    """)

    # Migração simples: se já existia uma conta totalmente paga antes
    # desta atualização, usa a data do último pagamento como quitação.
    contas_antigas = cursor.execute("""
        SELECT
            cp.id,
            cp.paciente_id,
            cp.valor_total,
            cp.saldo,
            MAX(pp.data_pagamento) AS ultima_data
        FROM contas_paciente cp
        LEFT JOIN pagamentos_paciente pp
            ON pp.conta_paciente_id = cp.id
        WHERE cp.saldo <= 0.000001
        GROUP BY cp.id
    """).fetchall()

    for conta_antiga in contas_antigas:
        if not conta_antiga["ultima_data"]:
            continue

        ja_existe = cursor.execute("""
            SELECT id
            FROM quitacoes_paciente
            WHERE conta_paciente_id = ?
            LIMIT 1
        """, (
            conta_antiga["id"],
        )).fetchone()

        if not ja_existe:
            cursor.execute("""
                INSERT INTO quitacoes_paciente
                (
                    conta_paciente_id,
                    paciente_id,
                    valor_quitado,
                    data_quitacao
                )
                VALUES (?, ?, ?, ?)
            """, (
                conta_antiga["id"],
                conta_antiga["paciente_id"],
                float(conta_antiga["valor_total"] or 0),
                conta_antiga["ultima_data"]
            ))

    conexao.commit()
    conexao.close()


def listar_orcamentos_com_status(paciente_id):
    """
    Lista o orçamento do paciente indicando se cada item já foi enviado
    para a conta a receber.
    """
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            orcamentos.*,
            pacientes.nome AS paciente_nome,
            CASE
                WHEN orcamentos_transferidos.id IS NULL THEN 0
                ELSE 1
            END AS transferido
        FROM orcamentos
        INNER JOIN pacientes
            ON pacientes.id = orcamentos.paciente_id
        LEFT JOIN orcamentos_transferidos
            ON orcamentos_transferidos.orcamento_id = orcamentos.id
        WHERE orcamentos.paciente_id = ?
        ORDER BY orcamentos.id DESC
    """, (paciente_id,))

    registros = cursor.fetchall()
    conexao.close()
    return registros


def obter_conta_paciente(paciente_id):
    conexao = conectar()
    cursor = conexao.cursor()

    conta = cursor.execute("""
        SELECT *
        FROM contas_paciente
        WHERE paciente_id = ?
        LIMIT 1
    """, (paciente_id,)).fetchone()

    conexao.close()
    return conta


def listar_pagamentos_paciente(paciente_id):
    conexao = conectar()
    cursor = conexao.cursor()

    registros = cursor.execute("""
        SELECT *
        FROM pagamentos_paciente
        WHERE paciente_id = ?
        ORDER BY data_pagamento DESC, id DESC
    """, (paciente_id,)).fetchall()

    conexao.close()
    return registros


def listar_quitacoes_paciente(paciente_id):
    conexao = conectar()
    cursor = conexao.cursor()

    registros = cursor.execute("""
        SELECT *
        FROM quitacoes_paciente
        WHERE paciente_id = ?
        ORDER BY data_quitacao DESC, id DESC
    """, (paciente_id,)).fetchall()

    conexao.close()
    return registros


def total_orcamento_nao_transferido(paciente_id):
    conexao = conectar()
    cursor = conexao.cursor()

    registro = cursor.execute("""
        SELECT
            COALESCE(SUM(orcamentos.valor), 0) AS total
        FROM orcamentos
        LEFT JOIN orcamentos_transferidos
            ON orcamentos_transferidos.orcamento_id = orcamentos.id
        WHERE orcamentos.paciente_id = ?
          AND orcamentos_transferidos.id IS NULL
    """, (paciente_id,)).fetchone()

    conexao.close()
    return float(registro["total"] or 0)


def _obter_nome_paciente(cursor, paciente_id):
    paciente = cursor.execute("""
        SELECT nome
        FROM pacientes
        WHERE id = ?
    """, (paciente_id,)).fetchone()

    return paciente["nome"] if paciente else f"Paciente #{paciente_id}"


def _sincronizar_conta_receber(
    cursor,
    paciente_id,
    conta_paciente_id,
    saldo,
    vencimento
):
    """
    Mantém no Financeiro somente contas que ainda têm saldo.

    Se o saldo chegar a zero, a linha de contas_receber é removida.
    O histórico da quitação fica apenas no perfil do paciente.
    """
    conta = cursor.execute("""
        SELECT conta_receber_id
        FROM contas_paciente
        WHERE id = ?
    """, (conta_paciente_id,)).fetchone()

    conta_receber_id = (
        conta["conta_receber_id"]
        if conta
        else None
    )

    saldo = max(0.0, float(saldo))

    # Totalmente pago: some do "A receber" do Financeiro.
    if saldo <= 0.000001:
        if conta_receber_id:
            try:
                cursor.execute("""
                    UPDATE boletos
                    SET conta_receber_id = NULL
                    WHERE conta_receber_id = ?
                """, (
                    conta_receber_id,
                ))
            except Exception:
                pass

            cursor.execute("""
                UPDATE contas_paciente
                SET conta_receber_id = NULL
                WHERE id = ?
            """, (
                conta_paciente_id,
            ))

            cursor.execute("""
                DELETE FROM contas_receber
                WHERE id = ?
            """, (
                conta_receber_id,
            ))

        return None

    nome = _obter_nome_paciente(
        cursor,
        paciente_id
    )

    descricao = f"Conta do paciente - {nome}"

    registro_receber = None

    if conta_receber_id:
        registro_receber = cursor.execute("""
            SELECT id
            FROM contas_receber
            WHERE id = ?
        """, (
            conta_receber_id,
        )).fetchone()

    if registro_receber:
        cursor.execute("""
            UPDATE contas_receber
            SET
                paciente_id = ?,
                descricao = ?,
                valor = ?,
                vencimento = ?,
                status = 'Pendente'
            WHERE id = ?
        """, (
            paciente_id,
            descricao,
            saldo,
            vencimento,
            conta_receber_id
        ))
    else:
        cursor.execute("""
            INSERT INTO contas_receber
            (
                paciente_id,
                descricao,
                valor,
                vencimento,
                status
            )
            VALUES (?, ?, ?, ?, 'Pendente')
        """, (
            paciente_id,
            descricao,
            saldo,
            vencimento
        ))

        conta_receber_id = cursor.lastrowid

        cursor.execute("""
            UPDATE contas_paciente
            SET conta_receber_id = ?
            WHERE id = ?
        """, (
            conta_receber_id,
            conta_paciente_id
        ))

    return conta_receber_id


def passar_orcamento_para_receber(
    paciente_id,
    vencimento
):
    """
    Transfere somente os itens do orçamento que ainda não foram passados.
    Se o paciente já possui uma conta, soma os novos itens à mesma conta.
    """
    vencimento = (vencimento or "").strip()

    if not vencimento:
        raise ValueError("Informe o vencimento da conta.")

    conexao = conectar()
    cursor = conexao.cursor()

    itens = cursor.execute("""
        SELECT
            orcamentos.id,
            orcamentos.valor
        FROM orcamentos
        LEFT JOIN orcamentos_transferidos
            ON orcamentos_transferidos.orcamento_id = orcamentos.id
        WHERE orcamentos.paciente_id = ?
          AND orcamentos_transferidos.id IS NULL
        ORDER BY orcamentos.id
    """, (paciente_id,)).fetchall()

    if not itens:
        conexao.close()
        raise ValueError(
            "Não há novos itens de orçamento para passar ao A receber."
        )

    valor_novo = sum(
        float(item["valor"] or 0)
        for item in itens
    )

    if valor_novo <= 0:
        conexao.close()
        raise ValueError(
            "O valor do orçamento precisa ser maior que zero."
        )

    conta = cursor.execute("""
        SELECT *
        FROM contas_paciente
        WHERE paciente_id = ?
        LIMIT 1
    """, (paciente_id,)).fetchone()

    if conta:
        conta_id = conta["id"]
        novo_total = float(conta["valor_total"] or 0) + valor_novo
        novo_saldo = float(conta["saldo"] or 0) + valor_novo

        cursor.execute("""
            UPDATE contas_paciente
            SET
                valor_total = ?,
                saldo = ?,
                vencimento = ?,
                atualizado_em = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            novo_total,
            novo_saldo,
            vencimento,
            conta_id
        ))
    else:
        cursor.execute("""
            INSERT INTO contas_paciente
            (
                paciente_id,
                valor_total,
                saldo,
                vencimento
            )
            VALUES (?, ?, ?, ?)
        """, (
            paciente_id,
            valor_novo,
            valor_novo,
            vencimento
        ))

        conta_id = cursor.lastrowid
        novo_total = valor_novo
        novo_saldo = valor_novo

    for item in itens:
        cursor.execute("""
            INSERT INTO orcamentos_transferidos
            (
                orcamento_id,
                conta_paciente_id,
                valor_transferido
            )
            VALUES (?, ?, ?)
        """, (
            item["id"],
            conta_id,
            float(item["valor"] or 0)
        ))

    _sincronizar_conta_receber(
        cursor,
        paciente_id,
        conta_id,
        novo_saldo,
        vencimento
    )

    conexao.commit()
    conexao.close()

    return valor_novo


def registrar_pagamento_paciente(
    paciente_id,
    valor,
    data_pagamento,
    observacao=""
):
    valor = _float(valor)
    data_pagamento = (data_pagamento or "").strip()
    observacao = (observacao or "").strip()

    if valor <= 0:
        raise ValueError(
            "O valor do pagamento precisa ser maior que zero."
        )

    if not data_pagamento:
        raise ValueError(
            "Informe a data do pagamento."
        )

    conexao = conectar()

    try:
        cursor = conexao.cursor()
        cursor.execute("BEGIN IMMEDIATE")

        conta = cursor.execute("""
            SELECT *
            FROM contas_paciente
            WHERE paciente_id = ?
            LIMIT 1
        """, (
            paciente_id,
        )).fetchone()

        if not conta:
            raise ValueError(
                "Este paciente ainda não possui uma conta a receber."
            )

        saldo_atual = float(
            conta["saldo"] or 0
        )

        if saldo_atual <= 0.000001:
            raise ValueError(
                "A conta deste paciente já está totalmente paga."
            )

        if valor > saldo_atual + 0.000001:
            raise ValueError(
                f"O pagamento não pode ser maior que o saldo de R$ {saldo_atual:.2f}."
            )

        novo_saldo = max(
            0.0,
            round(
                saldo_atual - valor,
                2
            )
        )

        nome = _obter_nome_paciente(
            cursor,
            paciente_id
        )

        # Mantém a entrada no fluxo de caixa, pois o dinheiro realmente entrou.
        cursor.execute("""
            INSERT INTO movimentacoes
            (
                descricao,
                tipo,
                valor,
                data
            )
            VALUES (?, 'Entrada', ?, ?)
        """, (
            f"Pagamento de {nome}",
            valor,
            data_pagamento
        ))

        movimentacao_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO pagamentos_paciente
            (
                conta_paciente_id,
                paciente_id,
                valor,
                data_pagamento,
                observacao,
                movimentacao_id
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            conta["id"],
            paciente_id,
            valor,
            data_pagamento,
            observacao,
            movimentacao_id
        ))

        cursor.execute("""
            UPDATE contas_paciente
            SET
                saldo = ?,
                atualizado_em = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            novo_saldo,
            conta["id"]
        ))

        # Ao zerar, registra a quitação no perfil do paciente.
        if novo_saldo <= 0.000001:
            total_ja_quitado = cursor.execute("""
                SELECT COALESCE(
                    SUM(valor_quitado),
                    0
                ) AS total
                FROM quitacoes_paciente
                WHERE conta_paciente_id = ?
            """, (
                conta["id"],
            )).fetchone()

            valor_quitado_anterior = float(
                total_ja_quitado["total"] or 0
            )

            valor_deste_ciclo = max(
                0.0,
                round(
                    float(conta["valor_total"] or 0)
                    - valor_quitado_anterior,
                    2
                )
            )

            if valor_deste_ciclo > 0.000001:
                cursor.execute("""
                    INSERT INTO quitacoes_paciente
                    (
                        conta_paciente_id,
                        paciente_id,
                        valor_quitado,
                        data_quitacao
                    )
                    VALUES (?, ?, ?, ?)
                """, (
                    conta["id"],
                    paciente_id,
                    valor_deste_ciclo,
                    data_pagamento
                ))

        _sincronizar_conta_receber(
            cursor,
            paciente_id,
            conta["id"],
            novo_saldo,
            conta["vencimento"] or data_pagamento
        )

        conexao.commit()
        return novo_saldo

    except Exception:
        conexao.rollback()
        raise

    finally:
        conexao.close()


def excluir_pagamento_paciente(
    pagamento_id,
    paciente_id
):
    """
    Corrige um pagamento lançado por engano.
    O valor volta para o saldo e a Entrada correspondente é retirada
    do Fluxo de Caixa.

    A transação é feita em uma única conexão e sempre é encerrada,
    inclusive se ocorrer erro, evitando deixar o SQLite bloqueado.
    """
    conexao = conectar()

    try:
        cursor = conexao.cursor()

        # Reserva a escrita antes de começar as alterações.
        # Se outra operação estiver usando o banco, o busy_timeout
        # configurado em banco.py aguardará a liberação.
        cursor.execute("BEGIN IMMEDIATE")

        pagamento = cursor.execute("""
            SELECT *
            FROM pagamentos_paciente
            WHERE id = ?
              AND paciente_id = ?
            LIMIT 1
        """, (
            pagamento_id,
            paciente_id
        )).fetchone()

        if not pagamento:
            raise ValueError(
                "Pagamento não encontrado."
            )

        conta = cursor.execute("""
            SELECT *
            FROM contas_paciente
            WHERE id = ?
            LIMIT 1
        """, (
            pagamento["conta_paciente_id"],
        )).fetchone()

        if not conta:
            raise ValueError(
                "Conta do paciente não encontrada."
            )

        saldo_antes_da_exclusao = float(
            conta["saldo"] or 0
        )

        novo_saldo = min(
            float(conta["valor_total"] or 0),
            round(
                saldo_antes_da_exclusao
                + float(pagamento["valor"] or 0),
                2
            )
        )

        # Se a conta estava quitada e este pagamento a reabre,
        # remove a última quitação registrada no perfil.
        if saldo_antes_da_exclusao <= 0.000001:
            ultima_quitacao = cursor.execute("""
                SELECT id
                FROM quitacoes_paciente
                WHERE conta_paciente_id = ?
                ORDER BY data_quitacao DESC, id DESC
                LIMIT 1
            """, (
                conta["id"],
            )).fetchone()

            if ultima_quitacao:
                cursor.execute("""
                    DELETE FROM quitacoes_paciente
                    WHERE id = ?
                """, (
                    ultima_quitacao["id"],
                ))

        # Primeiro apaga o pagamento que referencia a movimentação.
        # Depois a movimentação pode ser removida sem risco de FK.
        cursor.execute("""
            DELETE FROM pagamentos_paciente
            WHERE id = ?
        """, (
            pagamento_id,
        ))

        if pagamento["movimentacao_id"]:
            cursor.execute("""
                DELETE FROM movimentacoes
                WHERE id = ?
            """, (
                pagamento["movimentacao_id"],
            ))

        cursor.execute("""
            UPDATE contas_paciente
            SET
                saldo = ?,
                atualizado_em = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            novo_saldo,
            conta["id"]
        ))

        _sincronizar_conta_receber(
            cursor,
            paciente_id,
            conta["id"],
            novo_saldo,
            conta["vencimento"] or pagamento["data_pagamento"]
        )

        conexao.commit()
        return novo_saldo

    except Exception:
        conexao.rollback()
        raise

    finally:
        conexao.close()


def resumo_conta_paciente(paciente_id):
    conta = obter_conta_paciente(paciente_id)

    if not conta:
        return {
            "existe": False,
            "valor_total": 0.0,
            "total_pago": 0.0,
            "saldo": 0.0,
            "status": "Sem conta",
            "percentual_pago": 0.0,
            "vencimento": ""
        }

    valor_total = float(conta["valor_total"] or 0)
    saldo = max(0.0, float(conta["saldo"] or 0))
    total_pago = max(
        0.0,
        round(valor_total - saldo, 2)
    )

    percentual = 0.0

    if valor_total > 0:
        percentual = min(
            100.0,
            max(
                0.0,
                (total_pago / valor_total) * 100
            )
        )

    return {
        "existe": True,
        "id": conta["id"],
        "valor_total": valor_total,
        "total_pago": total_pago,
        "saldo": saldo,
        "status": "Pago" if saldo <= 0.000001 else "Pendente",
        "percentual_pago": percentual,
        "vencimento": conta["vencimento"] or ""
    }

# =========================================================
# RESUMO DE GASTOS MENSAIS E ANUAIS
# =========================================================

MESES_PT = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Março",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro",
}


def listar_anos_gastos():
    """
    Retorna anos existentes tanto nas contas a pagar
    quanto no fluxo de caixa.
    """
    conexao = conectar()
    cursor = conexao.cursor()

    registros = cursor.execute("""
        SELECT ano
        FROM (
            SELECT DISTINCT substr(vencimento, 1, 4) AS ano
            FROM contas_pagar
            WHERE vencimento IS NOT NULL
              AND length(vencimento) >= 4
              AND substr(vencimento, 1, 4)
                  GLOB '[0-9][0-9][0-9][0-9]'

            UNION

            SELECT DISTINCT substr(data, 1, 4) AS ano
            FROM movimentacoes
            WHERE data IS NOT NULL
              AND length(data) >= 4
              AND substr(data, 1, 4)
                  GLOB '[0-9][0-9][0-9][0-9]'
        )
        WHERE ano IS NOT NULL
        ORDER BY ano DESC
    """).fetchall()

    conexao.close()

    anos = []

    for registro in registros:
        try:
            anos.append(int(registro["ano"]))
        except (TypeError, ValueError):
            pass

    ano_atual = date.today().year

    if ano_atual not in anos:
        anos.append(ano_atual)

    return sorted(set(anos), reverse=True)


def resumo_gastos_mensais(ano):
    """
    Resumo mensal completo:
    - despesas / contas a pagar;
    - pago e pendente;
    - entradas;
    - saídas;
    - saldo do fluxo.
    """
    try:
        ano = int(ano)
    except (TypeError, ValueError):
        ano = date.today().year

    conexao = conectar()
    cursor = conexao.cursor()

    despesas = cursor.execute("""
        SELECT
            CAST(substr(vencimento, 6, 2) AS INTEGER) AS mes,
            COALESCE(SUM(valor), 0) AS total,
            COALESCE(SUM(
                CASE
                    WHEN status = 'Pago' THEN valor
                    ELSE 0
                END
            ), 0) AS pago,
            COALESCE(SUM(
                CASE
                    WHEN status != 'Pago' THEN valor
                    ELSE 0
                END
            ), 0) AS pendente,
            COUNT(*) AS quantidade
        FROM contas_pagar
        WHERE substr(vencimento, 1, 4) = ?
        GROUP BY substr(vencimento, 6, 2)
        ORDER BY mes
    """, (str(ano),)).fetchall()

    fluxo = cursor.execute("""
        SELECT
            CAST(substr(data, 6, 2) AS INTEGER) AS mes,
            COALESCE(SUM(
                CASE
                    WHEN tipo = 'Entrada' THEN valor
                    ELSE 0
                END
            ), 0) AS entradas,
            COALESCE(SUM(
                CASE
                    WHEN tipo = 'Saída' THEN valor
                    ELSE 0
                END
            ), 0) AS saidas,
            COUNT(*) AS quantidade_fluxo
        FROM movimentacoes
        WHERE substr(data, 1, 4) = ?
        GROUP BY substr(data, 6, 2)
        ORDER BY mes
    """, (str(ano),)).fetchall()

    conexao.close()

    despesas_por_mes = {
        int(item["mes"]): item
        for item in despesas
        if item["mes"]
    }

    fluxo_por_mes = {
        int(item["mes"]): item
        for item in fluxo
        if item["mes"]
    }

    resumo = []

    for mes in range(1, 13):
        despesa = despesas_por_mes.get(mes)
        caixa = fluxo_por_mes.get(mes)

        entradas = float(caixa["entradas"]) if caixa else 0.0
        saidas = float(caixa["saidas"]) if caixa else 0.0

        resumo.append({
            "mes": mes,
            "mes_nome": MESES_PT[mes],

            "total": float(despesa["total"]) if despesa else 0.0,
            "pago": float(despesa["pago"]) if despesa else 0.0,
            "pendente": float(despesa["pendente"]) if despesa else 0.0,
            "quantidade": int(despesa["quantidade"]) if despesa else 0,

            "entradas": entradas,
            "saidas": saidas,
            "saldo": entradas - saidas,
            "quantidade_fluxo": (
                int(caixa["quantidade_fluxo"])
                if caixa else 0
            ),
        })

    return resumo


def resumo_gastos_anuais():
    """
    Resumo anual completo:
    despesas, pago, pendente, entradas, saídas e saldo.
    """
    conexao = conectar()
    cursor = conexao.cursor()

    anos = cursor.execute("""
        SELECT ano
        FROM (
            SELECT DISTINCT substr(vencimento, 1, 4) AS ano
            FROM contas_pagar
            WHERE vencimento IS NOT NULL
              AND length(vencimento) >= 4
              AND substr(vencimento, 1, 4)
                  GLOB '[0-9][0-9][0-9][0-9]'

            UNION

            SELECT DISTINCT substr(data, 1, 4) AS ano
            FROM movimentacoes
            WHERE data IS NOT NULL
              AND length(data) >= 4
              AND substr(data, 1, 4)
                  GLOB '[0-9][0-9][0-9][0-9]'
        )
        WHERE ano IS NOT NULL
        ORDER BY ano DESC
    """).fetchall()

    resumo = []

    for linha_ano in anos:
        ano = str(linha_ano["ano"])

        despesa = cursor.execute("""
            SELECT
                COALESCE(SUM(valor), 0) AS total,
                COALESCE(SUM(
                    CASE
                        WHEN status = 'Pago' THEN valor
                        ELSE 0
                    END
                ), 0) AS pago,
                COALESCE(SUM(
                    CASE
                        WHEN status != 'Pago' THEN valor
                        ELSE 0
                    END
                ), 0) AS pendente,
                COUNT(*) AS quantidade
            FROM contas_pagar
            WHERE substr(vencimento, 1, 4) = ?
        """, (ano,)).fetchone()

        caixa = cursor.execute("""
            SELECT
                COALESCE(SUM(
                    CASE
                        WHEN tipo = 'Entrada' THEN valor
                        ELSE 0
                    END
                ), 0) AS entradas,
                COALESCE(SUM(
                    CASE
                        WHEN tipo = 'Saída' THEN valor
                        ELSE 0
                    END
                ), 0) AS saidas,
                COUNT(*) AS quantidade_fluxo
            FROM movimentacoes
            WHERE substr(data, 1, 4) = ?
        """, (ano,)).fetchone()

        entradas = float(caixa["entradas"] or 0)
        saidas = float(caixa["saidas"] or 0)

        resumo.append({
            "ano": int(ano),

            "total": float(despesa["total"] or 0),
            "pago": float(despesa["pago"] or 0),
            "pendente": float(despesa["pendente"] or 0),
            "quantidade": int(despesa["quantidade"] or 0),

            "entradas": entradas,
            "saidas": saidas,
            "saldo": entradas - saidas,
            "quantidade_fluxo": int(
                caixa["quantidade_fluxo"] or 0
            ),
        })

    conexao.close()
    return resumo


def listar_gastos_mes(ano, mes):
    """
    Lista detalhadamente as contas a pagar de um mês específico.
    """
    try:
        ano = int(ano)
        mes = int(mes)
    except (TypeError, ValueError):
        return []

    if mes < 1 or mes > 12:
        return []

    prefixo = f"{ano:04d}-{mes:02d}"

    conexao = conectar()
    cursor = conexao.cursor()

    registros = cursor.execute("""
        SELECT *
        FROM contas_pagar
        WHERE substr(vencimento, 1, 7) = ?
        ORDER BY vencimento, id DESC
    """, (prefixo,)).fetchall()

    conexao.close()
    return registros

def excluir_conta_paciente(paciente_id):
    """
    Exclui a conta 'A receber' individual do paciente.

    Remove:
    - a conta consolidada do paciente;
    - o histórico de pagamentos dessa conta;
    - o registro sincronizado em contas_receber;
    - os marcadores que diziam que itens do orçamento já foram transferidos.

    O orçamento original NÃO é apagado.
    As movimentações de caixa dos pagamentos já recebidos são preservadas.
    """
    conexao = conectar()
    cursor = conexao.cursor()

    conta = cursor.execute("""
        SELECT *
        FROM contas_paciente
        WHERE paciente_id = ?
        LIMIT 1
    """, (paciente_id,)).fetchone()

    if not conta:
        conexao.close()
        raise ValueError(
            "Este paciente não possui uma conta a receber."
        )

    cursor.execute("""
        DELETE FROM pagamentos_paciente
        WHERE conta_paciente_id = ?
    """, (
        conta["id"],
    ))

    cursor.execute("""
        DELETE FROM quitacoes_paciente
        WHERE conta_paciente_id = ?
    """, (
        conta["id"],
    ))

    cursor.execute("""
        DELETE FROM orcamentos_transferidos
        WHERE conta_paciente_id = ?
    """, (
        conta["id"],
    ))

    if conta["conta_receber_id"]:
        # Primeiro removemos a referência da própria contas_paciente.
        # Sem isso, o SQLite impede apagar contas_receber por causa da FK.
        cursor.execute("""
            UPDATE contas_paciente
            SET conta_receber_id = NULL
            WHERE id = ?
        """, (
            conta["id"],
        ))

        # Se a tabela antiga de boletos ainda existir,
        # também removemos o vínculo com contas_receber.
        try:
            cursor.execute("""
                UPDATE boletos
                SET conta_receber_id = NULL
                WHERE conta_receber_id = ?
            """, (
                conta["conta_receber_id"],
            ))
        except Exception:
            pass

        cursor.execute("""
            DELETE FROM contas_receber
            WHERE id = ?
        """, (
            conta["conta_receber_id"],
        ))

    cursor.execute("""
        DELETE FROM contas_paciente
        WHERE id = ?
    """, (
        conta["id"],
    ))

    conexao.commit()
    conexao.close()

# =========================================================
# CONTAS INDIVIDUAIS POR ORÇAMENTO
# =========================================================
#
# A partir desta versão, cada vez que os itens NOVOS do orçamento
# são enviados para "A receber", é criada uma conta separada.
# Um orçamento novo não é somado ao que o paciente já fez antes.
#
# As tabelas antigas são mantidas por compatibilidade, mas as
# funções abaixo passam a ser a fonte principal do perfil.
# =========================================================

def criar_tabelas_contas_individuais():
    conexao = conectar()

    try:
        cursor = conexao.cursor()
        cursor.execute("BEGIN IMMEDIATE")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contas_orcamento (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paciente_id INTEGER NOT NULL,
                valor_total REAL NOT NULL DEFAULT 0,
                saldo REAL NOT NULL DEFAULT 0,
                vencimento TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pendente',
                conta_receber_id INTEGER,
                data_quitacao TEXT,
                criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
                atualizado_em TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (paciente_id) REFERENCES pacientes(id),
                FOREIGN KEY (conta_receber_id) REFERENCES contas_receber(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS itens_conta_orcamento (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conta_orcamento_id INTEGER NOT NULL,
                orcamento_id INTEGER,
                categoria TEXT DEFAULT '',
                descricao TEXT NOT NULL,
                valor REAL NOT NULL DEFAULT 0,
                criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(orcamento_id),
                FOREIGN KEY (conta_orcamento_id)
                    REFERENCES contas_orcamento(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pagamentos_conta_orcamento (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conta_orcamento_id INTEGER NOT NULL,
                paciente_id INTEGER NOT NULL,
                valor REAL NOT NULL,
                data_pagamento TEXT NOT NULL,
                observacao TEXT DEFAULT '',
                movimentacao_id INTEGER,
                criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conta_orcamento_id)
                    REFERENCES contas_orcamento(id),
                FOREIGN KEY (paciente_id)
                    REFERENCES pacientes(id),
                FOREIGN KEY (movimentacao_id)
                    REFERENCES movimentacoes(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS migracoes_sistema (
                chave TEXT PRIMARY KEY,
                executada_em TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        migrado = cursor.execute("""
            SELECT chave
            FROM migracoes_sistema
            WHERE chave = 'contas_orcamento_v2'
            LIMIT 1
        """).fetchone()

        if not migrado:
            _migrar_contas_antigas_para_contas_individuais(
                cursor
            )

            cursor.execute("""
                INSERT INTO migracoes_sistema (chave)
                VALUES ('contas_orcamento_v2')
            """)

        conexao.commit()

    except Exception:
        conexao.rollback()
        raise

    finally:
        conexao.close()


def _tabela_existe(cursor, tabela):
    registro = cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name = ?
        LIMIT 1
    """, (tabela,)).fetchone()

    return registro is not None


def _migrar_contas_antigas_para_contas_individuais(cursor):
    """
    Migra a conta consolidada antiga para uma única conta "legada"
    por paciente, apenas para não perder o histórico já existente.

    Depois da migração, novos orçamentos são sempre contas separadas.
    """
    if not _tabela_existe(cursor, "contas_paciente"):
        return

    contas_antigas = cursor.execute("""
        SELECT *
        FROM contas_paciente
        ORDER BY id
    """).fetchall()

    for conta_antiga in contas_antigas:
        paciente_id = conta_antiga["paciente_id"]
        valor_total = float(
            conta_antiga["valor_total"] or 0
        )
        saldo = float(
            conta_antiga["saldo"] or 0
        )
        vencimento = (
            conta_antiga["vencimento"]
            or date.today().isoformat()
        )
        conta_receber_id = conta_antiga[
            "conta_receber_id"
        ]

        ultima_data = None

        if _tabela_existe(
            cursor,
            "pagamentos_paciente"
        ):
            ultimo = cursor.execute("""
                SELECT MAX(data_pagamento) AS data
                FROM pagamentos_paciente
                WHERE conta_paciente_id = ?
            """, (
                conta_antiga["id"],
            )).fetchone()

            if ultimo:
                ultima_data = ultimo["data"]

        status = (
            "Pago"
            if saldo <= 0.000001
            else "Pendente"
        )

        data_quitacao = (
            ultima_data
            if status == "Pago"
            else None
        )

        cursor.execute("""
            INSERT INTO contas_orcamento
            (
                paciente_id,
                valor_total,
                saldo,
                vencimento,
                status,
                conta_receber_id,
                data_quitacao
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            paciente_id,
            valor_total,
            saldo,
            vencimento,
            status,
            conta_receber_id,
            data_quitacao
        ))

        nova_conta_id = cursor.lastrowid

        # Copia os itens antigos do orçamento como snapshot.
        if (
            _tabela_existe(
                cursor,
                "orcamentos_transferidos"
            )
            and _tabela_existe(
                cursor,
                "orcamentos"
            )
        ):
            itens = cursor.execute("""
                SELECT
                    ot.orcamento_id,
                    o.categoria,
                    o.descricao,
                    ot.valor_transferido AS valor
                FROM orcamentos_transferidos ot
                LEFT JOIN orcamentos o
                    ON o.id = ot.orcamento_id
                WHERE ot.conta_paciente_id = ?
            """, (
                conta_antiga["id"],
            )).fetchall()

            for item in itens:
                cursor.execute("""
                    INSERT OR IGNORE INTO itens_conta_orcamento
                    (
                        conta_orcamento_id,
                        orcamento_id,
                        categoria,
                        descricao,
                        valor
                    )
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    nova_conta_id,
                    item["orcamento_id"],
                    item["categoria"] or "Anterior",
                    item["descricao"] or "Orçamento anterior",
                    float(item["valor"] or 0)
                ))

        # Se não conseguiu recuperar itens, cria um item legado.
        tem_item = cursor.execute("""
            SELECT id
            FROM itens_conta_orcamento
            WHERE conta_orcamento_id = ?
            LIMIT 1
        """, (
            nova_conta_id,
        )).fetchone()

        if not tem_item and valor_total > 0:
            cursor.execute("""
                INSERT INTO itens_conta_orcamento
                (
                    conta_orcamento_id,
                    orcamento_id,
                    categoria,
                    descricao,
                    valor
                )
                VALUES (?, NULL, 'Anterior', 'Conta anterior', ?)
            """, (
                nova_conta_id,
                valor_total
            ))

        # Copia pagamentos antigos.
        if _tabela_existe(
            cursor,
            "pagamentos_paciente"
        ):
            pagamentos = cursor.execute("""
                SELECT *
                FROM pagamentos_paciente
                WHERE conta_paciente_id = ?
                ORDER BY id
            """, (
                conta_antiga["id"],
            )).fetchall()

            for pagamento in pagamentos:
                cursor.execute("""
                    INSERT INTO pagamentos_conta_orcamento
                    (
                        conta_orcamento_id,
                        paciente_id,
                        valor,
                        data_pagamento,
                        observacao,
                        movimentacao_id
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    nova_conta_id,
                    paciente_id,
                    float(pagamento["valor"] or 0),
                    pagamento["data_pagamento"],
                    pagamento["observacao"] or "",
                    pagamento["movimentacao_id"]
                ))

        # Libera a FK antiga de contas_receber.
        if conta_receber_id:
            cursor.execute("""
                UPDATE contas_paciente
                SET conta_receber_id = NULL
                WHERE id = ?
            """, (
                conta_antiga["id"],
            ))

    # Remove os registros antigos DEPOIS que tudo foi migrado.
    # As tabelas continuam existindo para não quebrar versões antigas.
    if _tabela_existe(cursor, "quitacoes_paciente"):
        cursor.execute(
            "DELETE FROM quitacoes_paciente"
        )

    if _tabela_existe(cursor, "orcamentos_transferidos"):
        cursor.execute(
            "DELETE FROM orcamentos_transferidos"
        )

    if _tabela_existe(cursor, "pagamentos_paciente"):
        cursor.execute(
            "DELETE FROM pagamentos_paciente"
        )

    cursor.execute(
        "DELETE FROM contas_paciente"
    )


def listar_orcamentos_com_status_individual(
    paciente_id
):
    """
    Lista todos os itens do orçamento e informa se já pertencem
    a alguma conta individual.
    """
    conexao = conectar()
    cursor = conexao.cursor()

    registros = cursor.execute("""
        SELECT
            o.*,
            p.nome AS paciente_nome,
            CASE
                WHEN ico.id IS NULL THEN 0
                ELSE 1
            END AS transferido,
            ico.conta_orcamento_id AS conta_id
        FROM orcamentos o
        INNER JOIN pacientes p
            ON p.id = o.paciente_id
        LEFT JOIN itens_conta_orcamento ico
            ON ico.orcamento_id = o.id
        WHERE o.paciente_id = ?
        ORDER BY o.id DESC
    """, (
        paciente_id,
    )).fetchall()

    conexao.close()
    return registros


def total_orcamento_nao_transferido_individual(
    paciente_id
):
    conexao = conectar()
    cursor = conexao.cursor()

    registro = cursor.execute("""
        SELECT
            COALESCE(
                SUM(o.valor),
                0
            ) AS total
        FROM orcamentos o
        LEFT JOIN itens_conta_orcamento ico
            ON ico.orcamento_id = o.id
        WHERE o.paciente_id = ?
          AND ico.id IS NULL
    """, (
        paciente_id,
    )).fetchone()

    conexao.close()

    return float(
        registro["total"] or 0
    )


def passar_orcamento_para_receber_individual(
    paciente_id,
    vencimento
):
    """
    Cria UMA NOVA CONTA somente com os itens de orçamento
    que ainda não foram enviados para A receber.

    Nunca soma com uma conta antiga.
    """
    vencimento = (
        vencimento or ""
    ).strip()

    if not vencimento:
        raise ValueError(
            "Informe o vencimento da conta."
        )

    conexao = conectar()

    try:
        cursor = conexao.cursor()
        cursor.execute(
            "BEGIN IMMEDIATE"
        )

        itens = cursor.execute("""
            SELECT
                o.id,
                o.categoria,
                o.descricao,
                o.valor
            FROM orcamentos o
            LEFT JOIN itens_conta_orcamento ico
                ON ico.orcamento_id = o.id
            WHERE o.paciente_id = ?
              AND ico.id IS NULL
            ORDER BY o.id
        """, (
            paciente_id,
        )).fetchall()

        if not itens:
            raise ValueError(
                "Não há novos itens de orçamento para passar ao A receber."
            )

        valor_total = sum(
            float(item["valor"] or 0)
            for item in itens
        )

        if valor_total <= 0:
            raise ValueError(
                "O orçamento precisa ter valor maior que zero."
            )

        cursor.execute("""
            INSERT INTO contas_orcamento
            (
                paciente_id,
                valor_total,
                saldo,
                vencimento,
                status
            )
            VALUES (?, ?, ?, ?, 'Pendente')
        """, (
            paciente_id,
            valor_total,
            valor_total,
            vencimento
        ))

        conta_id = cursor.lastrowid

        for item in itens:
            cursor.execute("""
                INSERT INTO itens_conta_orcamento
                (
                    conta_orcamento_id,
                    orcamento_id,
                    categoria,
                    descricao,
                    valor
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                conta_id,
                item["id"],
                item["categoria"] or "",
                item["descricao"],
                float(item["valor"] or 0)
            ))

        nome = _obter_nome_paciente(
            cursor,
            paciente_id
        )

        descricao = (
            f"Orçamento #{conta_id} - {nome}"
        )

        cursor.execute("""
            INSERT INTO contas_receber
            (
                paciente_id,
                descricao,
                valor,
                vencimento,
                status
            )
            VALUES (?, ?, ?, ?, 'Pendente')
        """, (
            paciente_id,
            descricao,
            valor_total,
            vencimento
        ))

        conta_receber_id = cursor.lastrowid

        cursor.execute("""
            UPDATE contas_orcamento
            SET conta_receber_id = ?
            WHERE id = ?
        """, (
            conta_receber_id,
            conta_id
        ))

        conexao.commit()

        return {
            "conta_id": conta_id,
            "valor": valor_total
        }

    except Exception:
        conexao.rollback()
        raise

    finally:
        conexao.close()


def _montar_conta_individual(
    cursor,
    conta
):
    conta_id = conta["id"]

    pagamentos = cursor.execute("""
        SELECT *
        FROM pagamentos_conta_orcamento
        WHERE conta_orcamento_id = ?
        ORDER BY data_pagamento DESC, id DESC
    """, (
        conta_id,
    )).fetchall()

    itens = cursor.execute("""
        SELECT *
        FROM itens_conta_orcamento
        WHERE conta_orcamento_id = ?
        ORDER BY id
    """, (
        conta_id,
    )).fetchall()

    valor_total = float(
        conta["valor_total"] or 0
    )
    saldo = max(
        0.0,
        float(conta["saldo"] or 0)
    )
    total_pago = max(
        0.0,
        round(
            valor_total - saldo,
            2
        )
    )

    percentual = 0.0

    if valor_total > 0:
        percentual = min(
            100.0,
            max(
                0.0,
                total_pago / valor_total * 100
            )
        )

    return {
        "id": conta_id,
        "paciente_id": conta["paciente_id"],
        "valor_total": valor_total,
        "saldo": saldo,
        "total_pago": total_pago,
        "vencimento": conta["vencimento"],
        "status": conta["status"],
        "data_quitacao": conta["data_quitacao"],
        "criado_em": conta["criado_em"],
        "percentual_pago": percentual,
        "pagamentos": [
            dict(item)
            for item in pagamentos
        ],
        "itens": [
            dict(item)
            for item in itens
        ],
    }


def listar_contas_individuais_paciente(
    paciente_id
):
    conexao = conectar()
    cursor = conexao.cursor()

    contas = cursor.execute("""
        SELECT *
        FROM contas_orcamento
        WHERE paciente_id = ?
        ORDER BY
            CASE
                WHEN status = 'Pendente' THEN 0
                ELSE 1
            END,
            id DESC
    """, (
        paciente_id,
    )).fetchall()

    resultado = [
        _montar_conta_individual(
            cursor,
            conta
        )
        for conta in contas
    ]

    conexao.close()
    return resultado


def listar_contas_pendentes_paciente(
    paciente_id
):
    return [
        conta
        for conta in listar_contas_individuais_paciente(
            paciente_id
        )
        if conta["status"] == "Pendente"
        and conta["saldo"] > 0.000001
    ]


def listar_contas_quitadas_paciente(
    paciente_id
):
    return [
        conta
        for conta in listar_contas_individuais_paciente(
            paciente_id
        )
        if conta["status"] == "Pago"
    ]


def registrar_pagamento_conta_individual(
    paciente_id,
    conta_id,
    valor,
    data_pagamento,
    observacao=""
):
    valor = _float(valor)
    data_pagamento = (
        data_pagamento or ""
    ).strip()
    observacao = (
        observacao or ""
    ).strip()

    if valor <= 0:
        raise ValueError(
            "O valor do pagamento precisa ser maior que zero."
        )

    if not data_pagamento:
        raise ValueError(
            "Informe a data do pagamento."
        )

    conexao = conectar()

    try:
        cursor = conexao.cursor()
        cursor.execute(
            "BEGIN IMMEDIATE"
        )

        conta = cursor.execute("""
            SELECT *
            FROM contas_orcamento
            WHERE id = ?
              AND paciente_id = ?
            LIMIT 1
        """, (
            conta_id,
            paciente_id
        )).fetchone()

        if not conta:
            raise ValueError(
                "Conta não encontrada."
            )

        saldo_atual = float(
            conta["saldo"] or 0
        )

        if saldo_atual <= 0.000001:
            raise ValueError(
                "Este orçamento já está totalmente pago."
            )

        if valor > saldo_atual + 0.000001:
            raise ValueError(
                f"O pagamento não pode ser maior que o saldo de R$ {saldo_atual:.2f}."
            )

        novo_saldo = max(
            0.0,
            round(
                saldo_atual - valor,
                2
            )
        )

        nome = _obter_nome_paciente(
            cursor,
            paciente_id
        )

        cursor.execute("""
            INSERT INTO movimentacoes
            (
                descricao,
                tipo,
                valor,
                data
            )
            VALUES (?, 'Entrada', ?, ?)
        """, (
            f"Pagamento orçamento #{conta_id} - {nome}",
            valor,
            data_pagamento
        ))

        movimentacao_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO pagamentos_conta_orcamento
            (
                conta_orcamento_id,
                paciente_id,
                valor,
                data_pagamento,
                observacao,
                movimentacao_id
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            conta_id,
            paciente_id,
            valor,
            data_pagamento,
            observacao,
            movimentacao_id
        ))

        if novo_saldo <= 0.000001:
            cursor.execute("""
                UPDATE contas_orcamento
                SET
                    saldo = 0,
                    status = 'Pago',
                    data_quitacao = ?,
                    atualizado_em = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                data_pagamento,
                conta_id
            ))

            conta_receber_id = conta[
                "conta_receber_id"
            ]

            if conta_receber_id:
                try:
                    cursor.execute("""
                        UPDATE boletos
                        SET conta_receber_id = NULL
                        WHERE conta_receber_id = ?
                    """, (
                        conta_receber_id,
                    ))
                except Exception:
                    pass

                cursor.execute("""
                    UPDATE contas_orcamento
                    SET conta_receber_id = NULL
                    WHERE id = ?
                """, (
                    conta_id,
                ))

                cursor.execute("""
                    DELETE FROM contas_receber
                    WHERE id = ?
                """, (
                    conta_receber_id,
                ))

        else:
            cursor.execute("""
                UPDATE contas_orcamento
                SET
                    saldo = ?,
                    status = 'Pendente',
                    data_quitacao = NULL,
                    atualizado_em = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                novo_saldo,
                conta_id
            ))

            cursor.execute("""
                UPDATE contas_receber
                SET
                    valor = ?,
                    status = 'Pendente'
                WHERE id = ?
            """, (
                novo_saldo,
                conta["conta_receber_id"]
            ))

        conexao.commit()
        return novo_saldo

    except Exception:
        conexao.rollback()
        raise

    finally:
        conexao.close()


def excluir_pagamento_conta_individual(
    paciente_id,
    pagamento_id
):
    conexao = conectar()

    try:
        cursor = conexao.cursor()
        cursor.execute(
            "BEGIN IMMEDIATE"
        )

        pagamento = cursor.execute("""
            SELECT *
            FROM pagamentos_conta_orcamento
            WHERE id = ?
              AND paciente_id = ?
            LIMIT 1
        """, (
            pagamento_id,
            paciente_id
        )).fetchone()

        if not pagamento:
            raise ValueError(
                "Pagamento não encontrado."
            )

        conta = cursor.execute("""
            SELECT *
            FROM contas_orcamento
            WHERE id = ?
            LIMIT 1
        """, (
            pagamento[
                "conta_orcamento_id"
            ],
        )).fetchone()

        if not conta:
            raise ValueError(
                "Conta não encontrada."
            )

        novo_saldo = min(
            float(
                conta["valor_total"] or 0
            ),
            round(
                float(
                    conta["saldo"] or 0
                )
                + float(
                    pagamento["valor"] or 0
                ),
                2
            )
        )

        cursor.execute("""
            DELETE FROM pagamentos_conta_orcamento
            WHERE id = ?
        """, (
            pagamento_id,
        ))

        if pagamento["movimentacao_id"]:
            cursor.execute("""
                DELETE FROM movimentacoes
                WHERE id = ?
            """, (
                pagamento[
                    "movimentacao_id"
                ],
            ))

        cursor.execute("""
            UPDATE contas_orcamento
            SET
                saldo = ?,
                status = 'Pendente',
                data_quitacao = NULL,
                atualizado_em = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            novo_saldo,
            conta["id"]
        ))

        conta_receber_id = conta[
            "conta_receber_id"
        ]

        nome = _obter_nome_paciente(
            cursor,
            paciente_id
        )

        if conta_receber_id:
            cursor.execute("""
                UPDATE contas_receber
                SET
                    valor = ?,
                    status = 'Pendente'
                WHERE id = ?
            """, (
                novo_saldo,
                conta_receber_id
            ))
        else:
            cursor.execute("""
                INSERT INTO contas_receber
                (
                    paciente_id,
                    descricao,
                    valor,
                    vencimento,
                    status
                )
                VALUES (?, ?, ?, ?, 'Pendente')
            """, (
                paciente_id,
                f"Orçamento #{conta['id']} - {nome}",
                novo_saldo,
                conta["vencimento"]
            ))

            nova_receber_id = cursor.lastrowid

            cursor.execute("""
                UPDATE contas_orcamento
                SET conta_receber_id = ?
                WHERE id = ?
            """, (
                nova_receber_id,
                conta["id"]
            ))

        conexao.commit()
        return novo_saldo

    except Exception:
        conexao.rollback()
        raise

    finally:
        conexao.close()


def excluir_conta_orcamento_individual(
    paciente_id,
    conta_id
):
    """
    Apaga somente UM orçamento/conta do paciente.
    Outras contas do mesmo paciente permanecem intactas.
    """
    conexao = conectar()

    try:
        cursor = conexao.cursor()
        cursor.execute(
            "BEGIN IMMEDIATE"
        )

        conta = cursor.execute("""
            SELECT *
            FROM contas_orcamento
            WHERE id = ?
              AND paciente_id = ?
            LIMIT 1
        """, (
            conta_id,
            paciente_id
        )).fetchone()

        if not conta:
            raise ValueError(
                "Conta não encontrada."
            )

        pagamentos = cursor.execute("""
            SELECT *
            FROM pagamentos_conta_orcamento
            WHERE conta_orcamento_id = ?
        """, (
            conta_id,
        )).fetchall()

        # Preserva as movimentações de pagamentos já recebidos,
        # porque o dinheiro realmente entrou na clínica.
        cursor.execute("""
            DELETE FROM pagamentos_conta_orcamento
            WHERE conta_orcamento_id = ?
        """, (
            conta_id,
        ))

        cursor.execute("""
            DELETE FROM itens_conta_orcamento
            WHERE conta_orcamento_id = ?
        """, (
            conta_id,
        ))

        conta_receber_id = conta[
            "conta_receber_id"
        ]

        if conta_receber_id:
            try:
                cursor.execute("""
                    UPDATE boletos
                    SET conta_receber_id = NULL
                    WHERE conta_receber_id = ?
                """, (
                    conta_receber_id,
                ))
            except Exception:
                pass

            cursor.execute("""
                UPDATE contas_orcamento
                SET conta_receber_id = NULL
                WHERE id = ?
            """, (
                conta_id,
            ))

            cursor.execute("""
                DELETE FROM contas_receber
                WHERE id = ?
            """, (
                conta_receber_id,
            ))

        cursor.execute("""
            DELETE FROM contas_orcamento
            WHERE id = ?
        """, (
            conta_id,
        ))

        conexao.commit()

    except Exception:
        conexao.rollback()
        raise

    finally:
        conexao.close()
