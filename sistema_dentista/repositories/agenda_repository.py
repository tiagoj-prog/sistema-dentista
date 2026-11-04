from datetime import date, datetime, timedelta
from ..database.connection import conectar


CORES_VALIDAS = {
    # Sem cor é o padrão para novos agendamentos.
    "sem-cor",

    # Procedimentos / tipos de atendimento usados na Agenda.
    "limpeza",
    "restauracao",
    "manutencao",
    "implante",
    "extracao",
    "canal",
    "protese",
    "ortodontia",
    "avaliacao",
    "retorno",

    # Compatibilidade com agendamentos antigos.
    "azul",
    "verde",
    "roxo",
    "amarelo",
    "vermelho",
    "cinza",

    # Compatibilidade com registros criados na versão anterior.
    "carie",
    "ausente",
    "fraturado",
}

STATUS_VALIDOS = {
    "Agendado",
    "Confirmado",
    "Concluído",
    "Cancelado",
}


def criar_tabela_agenda_visual():
    """
    Agenda independente do cadastro de pacientes.

    O nome e o telefone são digitados diretamente no compromisso.
    Não existe paciente_id nesta tabela.
    """
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agenda_eventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT DEFAULT '',
            titulo TEXT NOT NULL DEFAULT 'Consulta',
            data TEXT NOT NULL,
            hora_inicio TEXT NOT NULL,
            hora_fim TEXT NOT NULL,
            observacao TEXT DEFAULT '',
            status TEXT NOT NULL DEFAULT 'Agendado',
            cor TEXT NOT NULL DEFAULT 'sem-cor',
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conexao.commit()
    conexao.close()


def _segunda_feira(valor=None):
    if valor:
        try:
            referencia = datetime.strptime(
                valor,
                "%Y-%m-%d"
            ).date()
        except (TypeError, ValueError):
            referencia = date.today()
    else:
        referencia = date.today()

    return referencia - timedelta(
        days=referencia.weekday()
    )


def _horarios():
    
    horarios = []

    for hora in range(9, 19):
        horarios.append(f"{hora:02d}:00")
        horarios.append(f"{hora:02d}:30")

    horarios.append("19:00")
    return horarios


def listar_eventos_periodo(data_inicio, data_fim):
    conexao = conectar()
    cursor = conexao.cursor()

    registros = cursor.execute("""
        SELECT *
        FROM agenda_eventos
        WHERE data BETWEEN ? AND ?
        ORDER BY data, hora_inicio, id
    """, (
        data_inicio,
        data_fim
    )).fetchall()

    conexao.close()
    return registros


def preparar_agenda_semana(referencia=None):
    inicio = _segunda_feira(referencia)
    fim = inicio + timedelta(days=6)

    eventos = listar_eventos_periodo(
        inicio.isoformat(),
        fim.isoformat()
    )

    nomes_dias = [
        "Seg",
        "Ter",
        "Qua",
        "Qui",
        "Sex",
        "Sáb",
        "Dom",
    ]

    dias = []

    for indice in range(7):
        data_dia = inicio + timedelta(days=indice)

        eventos_dia = []

        for evento in eventos:
            if evento["data"] != data_dia.isoformat():
                continue

            try:
                hi = datetime.strptime(
                    evento["hora_inicio"],
                    "%H:%M"
                )
                hf = datetime.strptime(
                    evento["hora_fim"],
                    "%H:%M"
                )
            except ValueError:
                continue

            minutos_inicio = (
                (hi.hour - 9) * 60
                + hi.minute
            )

            minutos_duracao = max(
                30,
                int(
                    (hf - hi).total_seconds()
                    / 60
                )
            )

            # Cada 30 min = 44 px
            top = max(
                0,
                minutos_inicio / 30 * 44
            )

            altura = max(
                40,
                minutos_duracao / 30 * 44 - 4
            )

            item = dict(evento)
            item["top"] = round(top, 2)
            item["altura"] = round(altura, 2)

            eventos_dia.append(item)

        dias.append({
            "nome": nomes_dias[indice],
            "data": data_dia.isoformat(),
            "dia": data_dia.day,
            "mes": data_dia.month,
            "hoje": data_dia == date.today(),
            "eventos": eventos_dia,
        })

    return {
        "inicio": inicio.isoformat(),
        "fim": fim.isoformat(),
        "anterior": (
            inicio - timedelta(days=7)
        ).isoformat(),
        "proxima": (
            inicio + timedelta(days=7)
        ).isoformat(),
        "titulo": (
            f"{inicio.strftime('%d/%m/%Y')} "
            f"— {fim.strftime('%d/%m/%Y')}"
        ),
        "dias": dias,
        "horarios": _horarios(),
    }


def adicionar_evento(
    nome,
    telefone,
    titulo,
    data_evento,
    hora_inicio,
    hora_fim,
    observacao="",
    cor="sem-cor",
):
    nome = (nome or "").strip()
    telefone = (telefone or "").strip()
    titulo = (titulo or "Consulta").strip()
    data_evento = (data_evento or "").strip()
    hora_inicio = (hora_inicio or "").strip()
    hora_fim = (hora_fim or "").strip()
    observacao = (observacao or "").strip()
    cor = (cor or "sem-cor").strip().lower()

    if not nome:
        raise ValueError(
            "Informe o nome para o agendamento."
        )

    try:
        datetime.strptime(
            data_evento,
            "%Y-%m-%d"
        )
        inicio = datetime.strptime(
            hora_inicio,
            "%H:%M"
        )
        fim = datetime.strptime(
            hora_fim,
            "%H:%M"
        )
    except ValueError:
        raise ValueError(
            "Data ou horário inválido."
        )

    if fim <= inicio:
        raise ValueError(
            "O horário final precisa ser depois do horário inicial."
        )

    limite_inicio = datetime.strptime(
        "09:00",
        "%H:%M"
    )

    limite_ultimo_inicio = datetime.strptime(
        "18:30",
        "%H:%M"
    )

    limite_fim = datetime.strptime(
        "19:00",
        "%H:%M"
    )

    if inicio < limite_inicio or inicio > limite_ultimo_inicio:
        raise ValueError(
            "O horário inicial deve ficar entre 09:00 e 18:30."
        )

    if fim > limite_fim:
        raise ValueError(
            "O horário final não pode passar de 19:00."
        )

    if inicio.minute not in (0, 30) or fim.minute not in (0, 30):
        raise ValueError(
            "Use somente minutos 00 ou 30."
        )

    if cor not in CORES_VALIDAS:
        cor = "sem-cor"

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO agenda_eventos
        (
            nome,
            telefone,
            titulo,
            data,
            hora_inicio,
            hora_fim,
            observacao,
            status,
            cor
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, 'Agendado', ?)
    """, (
        nome,
        telefone,
        titulo or "Consulta",
        data_evento,
        hora_inicio,
        hora_fim,
        observacao,
        cor
    ))

    conexao.commit()
    conexao.close()


def alterar_status_evento(evento_id, status):
    if status not in STATUS_VALIDOS:
        raise ValueError(
            "Status inválido."
        )

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE agenda_eventos
        SET status = ?
        WHERE id = ?
    """, (
        status,
        evento_id
    ))

    conexao.commit()
    conexao.close()

def obter_evento(evento_id):
    conexao = conectar()
    cursor = conexao.cursor()

    evento = cursor.execute("""
        SELECT *
        FROM agenda_eventos
        WHERE id = ?
        LIMIT 1
    """, (evento_id,)).fetchone()

    conexao.close()

    return evento


def excluir_evento(evento_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        DELETE FROM agenda_eventos
        WHERE id = ?
    """, (evento_id,))

    conexao.commit()
    conexao.close()
