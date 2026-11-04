from ..database.connection import conectar
from datetime import datetime, timezone, timedelta

ESTADOS_VALIDOS = [
    "Limpeza",
    "Restauração",
    "Manutenção",
    "Implante",
    "Cárie",
    "Ausente",
    "Extração",
    "Canal",
    "Prótese",
    "Fraturado",
]

def formatar_data_local(data_banco):
    if not data_banco:
        return ""

    try:
        data_utc = datetime.strptime(
            data_banco,
            "%Y-%m-%d %H:%M:%S"
        )

        data_utc = data_utc.replace(
            tzinfo=timezone.utc
        )

        fuso_brasilia = timezone(
            timedelta(hours=-3)
        )

        data_local = data_utc.astimezone(
            fuso_brasilia
        )

        return data_local.strftime(
            "%d/%m/%Y %H:%M"
        )

    except (ValueError, TypeError):
        return data_banco

def criar_tabela_odontograma():
    conexao = conectar()
    cursor = conexao.cursor()

    # Mantém/cria a tabela principal do odontograma.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS odontograma (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER NOT NULL,
            dente TEXT NOT NULL,
            arcada TEXT NOT NULL DEFAULT '',
            estado TEXT NOT NULL DEFAULT 'Limpeza',
            observacao TEXT DEFAULT '',
            atualizado_em TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(paciente_id, dente),
            FOREIGN KEY (paciente_id) REFERENCES pacientes(id)
        )
    """)

    # Uma linha por face do dente.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS odontograma_faces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER NOT NULL,
            dente TEXT NOT NULL,
            face TEXT NOT NULL,
            estado TEXT NOT NULL DEFAULT 'Limpeza',
            atualizado_em TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(paciente_id, dente, face),
            FOREIGN KEY (paciente_id) REFERENCES pacientes(id)
        )
    """)

    # Histórico clínico por dente/face.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS odontograma_procedimentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER NOT NULL,
            procedimento TEXT NOT NULL,
            data_procedimento TEXT NOT NULL,
            descricao TEXT DEFAULT '',
            dente TEXT NOT NULL,
            face TEXT DEFAULT '',
            estado TEXT NOT NULL DEFAULT 'Limpeza',
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (paciente_id) REFERENCES pacientes(id)
        )
    """)

    # Migra nomes antigos sem apagar dados.
    migracoes = [
        ("Restaurado", "Restauração"),
        ("Extração indicada", "Extração"),
        ("Saudável", "Limpeza"),
    ]

    for antigo, novo in migracoes:
        cursor.execute(
            "UPDATE odontograma SET estado = ? WHERE estado = ?",
            (novo, antigo)
        )
        cursor.execute(
            "UPDATE odontograma_faces SET estado = ? WHERE estado = ?",
            (novo, antigo)
        )
        cursor.execute(
            "UPDATE odontograma_procedimentos SET estado = ? WHERE estado = ?",
            (novo, antigo)
        )

    conexao.commit()
    conexao.close()


def _arcada_do_dente(dente):
    numero = int(str(dente))

    if 11 <= numero <= 28:
        return "Superior permanente"
    if 31 <= numero <= 48:
        return "Inferior permanente"
    if 51 <= numero <= 65:
        return "Superior decídua"
    if 71 <= numero <= 85:
        return "Inferior decídua"

    return "Não identificada"


# ------------------------------------------------------------------
# COMPATIBILIDADE COM O ODONTOGRAMA ANTIGO
# ------------------------------------------------------------------

def listar_odontograma(paciente_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            dente,
            arcada,
            estado,
            observacao,
            atualizado_em
        FROM odontograma
        WHERE paciente_id = ?
    """, (paciente_id,))

    resultados = cursor.fetchall()
    conexao.close()

    odontograma = {}

    for resultado in resultados:
        odontograma[str(resultado["dente"])] = {
            "arcada": resultado["arcada"] or _arcada_do_dente(resultado["dente"]),
            "estado": resultado["estado"],
            "observacao": resultado["observacao"] or "",
            "atualizado_em": formatar_data_local(
                resultado["atualizado_em"]
            ),
        }

    return odontograma


def salvar_dente(paciente_id, dente, estado, observacao=""):
    if estado != "Limpar" and estado not in ESTADOS_VALIDOS:
        raise ValueError("Estado inválido.")

    conexao = conectar()
    cursor = conexao.cursor()

    if estado == "Limpar":
        cursor.execute("""
            DELETE FROM odontograma
            WHERE paciente_id = ? AND dente = ?
        """, (paciente_id, str(dente)))
    else:
        cursor.execute("""
            INSERT INTO odontograma
            (paciente_id, dente, arcada, estado, observacao)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(paciente_id, dente)
            DO UPDATE SET
                arcada = excluded.arcada,
                estado = excluded.estado,
                observacao = excluded.observacao,
                atualizado_em = CURRENT_TIMESTAMP
        """, (
            paciente_id,
            str(dente),
            _arcada_do_dente(dente),
            estado,
            observacao,
        ))

    conexao.commit()
    conexao.close()


# ------------------------------------------------------------------
# FACES DOS DENTES
# ------------------------------------------------------------------

def listar_faces_odontograma(paciente_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT dente, face, estado
        FROM odontograma_faces
        WHERE paciente_id = ?
    """, (paciente_id,))

    registros = cursor.fetchall()
    conexao.close()

    faces = {}

    for registro in registros:
        chave = f'{registro["dente"]}|{registro["face"]}'
        faces[chave] = registro["estado"]

    return faces


def salvar_face_odontograma(paciente_id, dente, face, estado):
    if not dente or not face:
        raise ValueError("Dente e face são obrigatórios.")

    if estado == "Limpar":
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute("""
            DELETE FROM odontograma_faces
            WHERE paciente_id = ? AND dente = ? AND face = ?
        """, (paciente_id, str(dente), face))
        conexao.commit()
        conexao.close()
        return

    if estado not in ESTADOS_VALIDOS:
        raise ValueError("Estado inválido.")

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO odontograma_faces
        (paciente_id, dente, face, estado)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(paciente_id, dente, face)
        DO UPDATE SET
            estado = excluded.estado,
            atualizado_em = CURRENT_TIMESTAMP
    """, (
        paciente_id,
        str(dente),
        face,
        estado,
    ))

    conexao.commit()
    conexao.close()


# ------------------------------------------------------------------
# HISTÓRICO DE PROCEDIMENTOS
# ------------------------------------------------------------------

def listar_procedimentos_odontograma(paciente_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT *
        FROM odontograma_procedimentos
        WHERE paciente_id = ?
        ORDER BY data_procedimento DESC, id DESC
    """, (paciente_id,))

    registros = cursor.fetchall()
    conexao.close()
    return registros


def adicionar_procedimento_odontograma(
    paciente_id,
    procedimento,
    data_procedimento,
    descricao,
    dente,
    face,
    estado,
):
    procedimento = (procedimento or "").strip()
    data_procedimento = (data_procedimento or "").strip()
    descricao = (descricao or "").strip()
    dente = str(dente or "").strip()
    face = (face or "").strip()
    estado = (estado or "Limpeza").strip()

    if not procedimento:
        raise ValueError("Informe o procedimento.")

    if not data_procedimento:
        raise ValueError("Informe a data do procedimento.")

    if not dente:
        raise ValueError("Selecione um dente.")

    if not face:
        raise ValueError("Selecione o dente inteiro ou uma face.")

    if estado not in ESTADOS_VALIDOS:
        raise ValueError("Estado inválido.")

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO odontograma_procedimentos
        (
            paciente_id,
            procedimento,
            data_procedimento,
            descricao,
            dente,
            face,
            estado
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        paciente_id,
        procedimento,
        data_procedimento,
        descricao,
        dente,
        face,
        estado,
    ))

    conexao.commit()
    conexao.close()

    # O procedimento também atualiza visualmente a área selecionada.
    #
    # "Dente inteiro" usa a tabela principal do odontograma.
    # As cinco faces continuam usando odontograma_faces.
    if face == "Dente inteiro":
        dados_atuais = listar_odontograma(
            paciente_id
        ).get(
            str(dente),
            {}
        )

        salvar_dente(
            paciente_id,
            dente,
            estado,
            dados_atuais.get(
                "observacao",
                ""
            )
        )
    else:
        salvar_face_odontograma(
            paciente_id,
            dente,
            face,
            estado,
        )


def excluir_procedimento_odontograma(procedimento_id, paciente_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        DELETE FROM odontograma_procedimentos
        WHERE id = ? AND paciente_id = ?
    """, (
        procedimento_id,
        paciente_id,
    ))

    conexao.commit()
    conexao.close()
