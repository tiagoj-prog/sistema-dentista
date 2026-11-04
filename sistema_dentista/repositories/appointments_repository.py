from ..database.connection import conectar


def cadastrar_consulta(paciente_id, data, horario):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO consultas
        (paciente_id, data, horario, status, mensagem_enviada)
        VALUES (?, ?, ?, 'Aguardando', 0)
    """, (paciente_id, data, horario))

    conexao.commit()
    conexao.close()


def listar_consultas():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            consultas.id,
            pacientes.nome,
            pacientes.telefone,
            consultas.data,
            consultas.horario,
            consultas.status,
            consultas.mensagem_enviada,
            pacientes.ativo
        FROM consultas
        INNER JOIN pacientes
            ON consultas.paciente_id = pacientes.id
        ORDER BY consultas.id DESC
    """)

    consultas = cursor.fetchall()
    conexao.close()
    return consultas


def alterar_status(consulta_id, status):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE consultas
        SET status = ?
        WHERE id = ?
    """, (status, consulta_id))

    conexao.commit()
    conexao.close()


def obter_consulta(consulta_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            consultas.id,
            pacientes.nome,
            pacientes.telefone,
            consultas.data,
            consultas.horario,
            consultas.status,
            consultas.mensagem_enviada
        FROM consultas
        INNER JOIN pacientes
            ON consultas.paciente_id = pacientes.id
        WHERE consultas.id = ?
    """, (consulta_id,))

    consulta = cursor.fetchone()
    conexao.close()
    return consulta


def marcar_mensagem_enviada(consulta_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE consultas
        SET mensagem_enviada = 1
        WHERE id = ?
    """, (consulta_id,))

    conexao.commit()
    conexao.close()
