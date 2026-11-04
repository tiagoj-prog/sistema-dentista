from ..database.connection import conectar


STATUS_TRATAMENTO = {
    "Planejado",
    "Em andamento",
    "Concluído",
    "Cancelado",
}


def criar_tabela_tratamentos():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tratamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paciente_id INTEGER NOT NULL,
            procedimento TEXT NOT NULL,
            data_inicio TEXT DEFAULT '',
            status TEXT NOT NULL DEFAULT 'Planejado',
            observacao TEXT DEFAULT '',
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
            atualizado_em TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (paciente_id)
                REFERENCES pacientes(id)
                ON DELETE CASCADE
        )
    """)

    conexao.commit()
    conexao.close()


def listar_tratamentos(paciente_id):
    conexao = conectar()
    cursor = conexao.cursor()

    registros = cursor.execute("""
        SELECT *
        FROM tratamentos
        WHERE paciente_id = ?
        ORDER BY
            CASE status
                WHEN 'Em andamento' THEN 0
                WHEN 'Planejado' THEN 1
                WHEN 'Concluído' THEN 2
                ELSE 3
            END,
            id DESC
    """, (paciente_id,)).fetchall()

    conexao.close()
    return registros


def adicionar_tratamento(
    paciente_id,
    procedimento,
    data_inicio="",
    observacao="",
):
    procedimento = (
        procedimento or ""
    ).strip()

    if not procedimento:
        raise ValueError(
            "Informe o procedimento."
        )

    conexao = conectar()
    cursor = conexao.cursor()

    # Funciona tanto no banco novo quanto no banco que já possui
    # a coluna "regiao" da versão anterior.
    colunas = cursor.execute(
        "PRAGMA table_info(tratamentos)"
    ).fetchall()

    nomes_colunas = {
        coluna["name"]
        for coluna in colunas
    }

    if "regiao" in nomes_colunas:
        cursor.execute("""
            INSERT INTO tratamentos
            (
                paciente_id,
                procedimento,
                regiao,
                data_inicio,
                status,
                observacao
            )
            VALUES (?, ?, '', ?, 'Planejado', ?)
        """, (
            paciente_id,
            procedimento,
            (data_inicio or "").strip(),
            (observacao or "").strip(),
        ))
    else:
        cursor.execute("""
            INSERT INTO tratamentos
            (
                paciente_id,
                procedimento,
                data_inicio,
                status,
                observacao
            )
            VALUES (?, ?, ?, 'Planejado', ?)
        """, (
            paciente_id,
            procedimento,
            (data_inicio or "").strip(),
            (observacao or "").strip(),
        ))

    conexao.commit()
    conexao.close()


def alterar_status_tratamento(
    tratamento_id,
    paciente_id,
    status,
):
    if status not in STATUS_TRATAMENTO:
        raise ValueError(
            "Status de tratamento inválido."
        )


    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE tratamentos
        SET
            status = ?,
            atualizado_em = CURRENT_TIMESTAMP
        WHERE id = ?
          AND paciente_id = ?
    """, (
        status,
        tratamento_id,
        paciente_id
    ))

    conexao.commit()
    conexao.close()


def excluir_tratamento(
    tratamento_id,
    paciente_id,
):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        DELETE FROM tratamentos
        WHERE id = ?
          AND paciente_id = ?
    """, (
        tratamento_id,
        paciente_id
    ))

    conexao.commit()
    conexao.close()
