from ..database.connection import conectar


def _garantir_campos_identificacao():
    """
    Garante que bancos antigos recebam os campos novos
    sem apagar nem recriar a tabela pacientes.
    """
    conexao = conectar()
    cursor = conexao.cursor()

    try:
        colunas = cursor.execute(
            "PRAGMA table_info(pacientes)"
        ).fetchall()

        nomes = {
            coluna[1]
            for coluna in colunas
        }

        novas_colunas = {
            "cpf": "TEXT DEFAULT ''",
            "rg": "TEXT DEFAULT ''",
            "data_nascimento": "TEXT DEFAULT ''",
            "tem_responsavel": "INTEGER NOT NULL DEFAULT 0",
            "responsavel_nome": "TEXT DEFAULT ''",
            "responsavel_cpf": "TEXT DEFAULT ''",
            "responsavel_relacao": "TEXT DEFAULT ''",
        }

        for nome, definicao in novas_colunas.items():
            if nome not in nomes:
                cursor.execute(
                    f"ALTER TABLE pacientes "
                    f"ADD COLUMN {nome} {definicao}"
                )

        conexao.commit()

    finally:
        conexao.close()



from ..validators import validar_cpf, validar_telefone


def cadastrar_paciente(nome, telefone):
    nome = (nome or "").strip()
    telefone = (telefone or "").strip()

    if not nome:
        raise ValueError("Nome é obrigatório.")

    if not validar_telefone(telefone):
        raise ValueError(
            "Telefone inválido. Use DDD + número "
            "(ex.: 11999999999)."
        )

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        INSERT INTO pacientes (nome, telefone, ativo)
        VALUES (?, ?, 1)
        """,
        (nome, telefone),
    )

    conexao.commit()
    conexao.close()


def listar_pacientes(busca="", pagina=1, por_pagina=20):
    _garantir_campos_identificacao()

    conexao = conectar()
    cursor = conexao.cursor()

    offset = (pagina - 1) * por_pagina

    if busca:
        cursor.execute(
            """
            SELECT COUNT(*) FROM pacientes
            WHERE ativo = 1 AND nome LIKE ?
            """,
            (f"%{busca}%",),
        )
        total = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT id, nome, telefone, ativo, prontuario, anamnese, endereco, cpf, rg, data_nascimento, tem_responsavel, responsavel_nome, responsavel_cpf, responsavel_relacao
            FROM pacientes
            WHERE ativo = 1
              AND nome LIKE ?
            ORDER BY nome
            LIMIT ? OFFSET ?
            """,
            (f"%{busca}%", por_pagina, offset),
        )
    else:
        cursor.execute(
            "SELECT COUNT(*) FROM pacientes WHERE ativo = 1"
        )
        total = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT id, nome, telefone, ativo, prontuario, anamnese, endereco, cpf, rg, data_nascimento, tem_responsavel, responsavel_nome, responsavel_cpf, responsavel_relacao
            FROM pacientes
            WHERE ativo = 1
            ORDER BY nome
            LIMIT ? OFFSET ?
            """,
            (por_pagina, offset),
        )

    pacientes = cursor.fetchall()
    conexao.close()
    return pacientes, total


def listar_todos_pacientes(busca="", pagina=1, por_pagina=20):
    _garantir_campos_identificacao()

    conexao = conectar()
    cursor = conexao.cursor()

    offset = (pagina - 1) * por_pagina

    if busca:
        cursor.execute(
            "SELECT COUNT(*) FROM pacientes WHERE nome LIKE ?",
            (f"%{busca}%",),
        )
        total = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT id, nome, telefone, ativo, prontuario, anamnese, endereco, cpf, rg, data_nascimento, tem_responsavel, responsavel_nome, responsavel_cpf, responsavel_relacao
            FROM pacientes
            WHERE nome LIKE ?
            ORDER BY ativo DESC, nome
            LIMIT ? OFFSET ?
            """,
            (f"%{busca}%", por_pagina, offset),
        )
    else:
        cursor.execute("SELECT COUNT(*) FROM pacientes")
        total = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT id, nome, telefone, ativo, prontuario, anamnese, endereco, cpf, rg, data_nascimento, tem_responsavel, responsavel_nome, responsavel_cpf, responsavel_relacao
            FROM pacientes
            ORDER BY ativo DESC, nome
            LIMIT ? OFFSET ?
            """,
            (por_pagina, offset),
        )

    pacientes = cursor.fetchall()
    conexao.close()
    return pacientes, total


def obter_paciente(paciente_id):
    _garantir_campos_identificacao()

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, nome, telefone, ativo, prontuario, anamnese, endereco, cpf, rg, data_nascimento, tem_responsavel, responsavel_nome, responsavel_cpf, responsavel_relacao
        FROM pacientes
        WHERE id = ?
    """, (paciente_id,))

    paciente = cursor.fetchone()
    conexao.close()
    return paciente


def atualizar_paciente(
    paciente_id,
    nome,
    telefone,
    prontuario,
    anamnese,
    endereco,
    cpf="",
    rg="",
    data_nascimento="",
    tem_responsavel=0,
    responsavel_nome="",
    responsavel_cpf="",
    responsavel_relacao=""
):
    nome = (nome or "").strip()
    telefone = (telefone or "").strip()

    if not nome:
        raise ValueError("Nome é obrigatório.")

    if not validar_telefone(telefone):
        raise ValueError(
            "Telefone inválido. Use DDD + número "
            "(ex.: 11999999999)."
        )

    if not validar_cpf(cpf):
        raise ValueError("CPF inválido.")

    if not validar_cpf(responsavel_cpf):
        raise ValueError("CPF do responsável inválido.")

    _garantir_campos_identificacao()

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE pacientes
        SET nome = ?,
            telefone = ?,
            prontuario = ?,
            anamnese = ?,
            endereco = ?,
            cpf = ?,
            rg = ?,
            data_nascimento = ?,
            tem_responsavel = ?,
            responsavel_nome = ?,
            responsavel_cpf = ?,
            responsavel_relacao = ?
        WHERE id = ?
    """, (
        nome.strip(),
        telefone.strip(),
        prontuario,
        anamnese,
        endereco,
        cpf.strip(),
        rg.strip(),
        data_nascimento.strip(),
        1 if tem_responsavel else 0,
        responsavel_nome.strip(),
        responsavel_cpf.strip(),
        responsavel_relacao.strip(),
        paciente_id
    ))

    conexao.commit()
    conexao.close()


def desativar_paciente(paciente_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE pacientes
        SET ativo = 0
        WHERE id = ?
    """, (paciente_id,))

    conexao.commit()
    conexao.close()


def ativar_paciente(paciente_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE pacientes
        SET ativo = 1
        WHERE id = ?
    """, (paciente_id,))

    conexao.commit()
    conexao.close()


def _tabela_existe(cursor, tabela):
    registro = cursor.execute(
        """
        SELECT 1
        FROM sqlite_master
        WHERE type = 'table'
          AND name = ?
        LIMIT 1
        """,
        (tabela,),
    ).fetchone()

    return registro is not None


def excluir_paciente_permanentemente(paciente_id):
    """
    Exclui permanentemente os registros operacionais relacionados ao
    paciente em uma única transação.

    Falhas em operações obrigatórias interrompem o procedimento e
    provocam rollback. Tabelas antigas podem ser inexistentes em bancos
    legados, mas, quando existirem, seus dados são excluídos.

    movimentacoes é preservado, conforme regra atual de auditoria financeira.
    """
    conexao = conectar()

    try:
        cursor = conexao.cursor()
        cursor.execute("BEGIN IMMEDIATE")

        paciente = cursor.execute(
            """
            SELECT id
            FROM pacientes
            WHERE id = ?
            """,
            (paciente_id,),
        ).fetchone()

        if paciente is None:
            raise ValueError("Paciente não encontrado.")

        # O esquema atual garante a existência de todas as tabelas abaixo.
        # Se alguma estiver ausente, a exclusão é interrompida antes de
        # qualquer operação de remoção, preservando a transação.
        tabelas_obrigatorias = [
            "contas_orcamento",
            "pagamentos_conta_orcamento",
            "itens_conta_orcamento",
            "contas_paciente",
            "pagamentos_paciente",
            "quitacoes_paciente",
            "orcamentos_transferidos",
            "boletos",
            "notas_fiscais",
            "contas_receber",
            "orcamentos",
            "odontograma",
            "odontograma_faces",
            "odontograma_procedimentos",
            "consultas",
        ]

        tabelas_ausentes = [
            tabela
            for tabela in tabelas_obrigatorias
            if not _tabela_existe(cursor, tabela)
        ]

        if tabelas_ausentes:
            raise RuntimeError(
                "Tabelas obrigatórias ausentes para a exclusão segura: "
                + ", ".join(tabelas_ausentes)
            )
        # -----------------------------------------------------------------------------
        # Contas novas por orçamento
        # -----------------------------------------------------------------------------
        if _tabela_existe(cursor, "contas_orcamento"):
            contas_novas = cursor.execute(
                """
                SELECT id, conta_receber_id
                FROM contas_orcamento
                WHERE paciente_id = ?
                """,
                (paciente_id,),
            ).fetchall()

            ids_contas_novas = [conta["id"] for conta in contas_novas]

            for conta in contas_novas:
                cursor.execute(
                    """
                    DELETE FROM pagamentos_conta_orcamento
                    WHERE conta_orcamento_id = ?
                    """,
                    (conta["id"],),
                )

                cursor.execute(
                    """
                    DELETE FROM itens_conta_orcamento
                    WHERE conta_orcamento_id = ?
                    """,
                    (conta["id"],),
                )

                if conta["conta_receber_id"]:
                    if _tabela_existe(cursor, "boletos"):
                        cursor.execute(
                            """
                            UPDATE boletos
                            SET conta_receber_id = NULL
                            WHERE conta_receber_id = ?
                            """,
                            (conta["conta_receber_id"],),
                        )

                    cursor.execute(
                        """
                        UPDATE contas_orcamento
                        SET conta_receber_id = NULL
                        WHERE id = ?
                        """,
                        (conta["id"],),
                    )

            cursor.execute(
                """
                DELETE FROM contas_orcamento
                WHERE paciente_id = ?
                """,
                (paciente_id,),
            )

            if cursor.execute(
                """
                SELECT 1
                FROM contas_orcamento
                WHERE paciente_id = ?
                LIMIT 1
                """,
                (paciente_id,),
            ).fetchone() is not None:
                raise RuntimeError("Não foi possível validar a exclusão de contas_orcamento.")

            if ids_contas_novas:
                placeholders = ", ".join("?" for _ in ids_contas_novas)
                if _tabela_existe(cursor, "pagamentos_conta_orcamento"):
                    if cursor.execute(
                        f"""
                        SELECT 1
                        FROM pagamentos_conta_orcamento
                        WHERE conta_orcamento_id IN ({placeholders})
                        LIMIT 1
                        """,
                        tuple(ids_contas_novas),
                    ).fetchone() is not None:
                        raise RuntimeError("Não foi possível validar a exclusão de pagamentos_conta_orcamento.")
                if _tabela_existe(cursor, "itens_conta_orcamento"):
                    if cursor.execute(
                        f"""
                        SELECT 1
                        FROM itens_conta_orcamento
                        WHERE conta_orcamento_id IN ({placeholders})
                        LIMIT 1
                        """,
                        tuple(ids_contas_novas),
                    ).fetchone() is not None:
                        raise RuntimeError("Não foi possível validar a exclusão de itens_conta_orcamento.")

        # -----------------------------------------------------------------------------
        # Estruturas antigas de recebimento
        # -----------------------------------------------------------------------------
        if _tabela_existe(cursor, "contas_paciente"):
            contas_antigas = cursor.execute(
                """
                SELECT id, conta_receber_id
                FROM contas_paciente
                WHERE paciente_id = ?
                """,
                (paciente_id,),
            ).fetchall()

            ids_contas_antigas = [conta["id"] for conta in contas_antigas]

            for conta in contas_antigas:
                if _tabela_existe(cursor, "pagamentos_paciente"):
                    cursor.execute(
                        """
                        DELETE FROM pagamentos_paciente
                        WHERE conta_paciente_id = ?
                        """,
                        (conta["id"],),
                    )
                if _tabela_existe(cursor, "quitacoes_paciente"):
                    cursor.execute(
                        """
                        DELETE FROM quitacoes_paciente
                        WHERE conta_paciente_id = ?
                        """,
                        (conta["id"],),
                    )
                if _tabela_existe(cursor, "orcamentos_transferidos"):
                    cursor.execute(
                        """
                        DELETE FROM orcamentos_transferidos
                        WHERE conta_paciente_id = ?
                        """,
                        (conta["id"],),
                    )

                if conta["conta_receber_id"]:
                    if _tabela_existe(cursor, "boletos"):
                        cursor.execute(
                            """
                            UPDATE boletos
                            SET conta_receber_id = NULL
                            WHERE conta_receber_id = ?
                            """,
                            (conta["conta_receber_id"],),
                        )
                    cursor.execute(
                        """
                        UPDATE contas_paciente
                        SET conta_receber_id = NULL
                        WHERE id = ?
                        """,
                        (conta["id"],),
                    )

            cursor.execute(
                """
                DELETE FROM contas_paciente
                WHERE paciente_id = ?
                """,
                (paciente_id,),
            )

            if cursor.execute(
                """
                SELECT 1
                FROM contas_paciente
                WHERE paciente_id = ?
                LIMIT 1
                """,
                (paciente_id,),
            ).fetchone() is not None:
                raise RuntimeError("Não foi possível validar a exclusão de contas_paciente.")

            if ids_contas_antigas:
                placeholders = ", ".join("?" for _ in ids_contas_antigas)
                if _tabela_existe(cursor, "pagamentos_paciente"):
                    if cursor.execute(
                        f"""
                        SELECT 1
                        FROM pagamentos_paciente
                        WHERE conta_paciente_id IN ({placeholders})
                        LIMIT 1
                        """,
                        tuple(ids_contas_antigas),
                    ).fetchone() is not None:
                        raise RuntimeError("Não foi possível validar a exclusão de pagamentos_paciente.")
                if _tabela_existe(cursor, "quitacoes_paciente"):
                    if cursor.execute(
                        f"""
                        SELECT 1
                        FROM quitacoes_paciente
                        WHERE conta_paciente_id IN ({placeholders})
                        LIMIT 1
                        """,
                        tuple(ids_contas_antigas),
                    ).fetchone() is not None:
                        raise RuntimeError("Não foi possível validar a exclusão de quitacoes_paciente.")
                if _tabela_existe(cursor, "orcamentos_transferidos"):
                    if cursor.execute(
                        f"""
                        SELECT 1
                        FROM orcamentos_transferidos
                        WHERE conta_paciente_id IN ({placeholders})
                        LIMIT 1
                        """,
                        tuple(ids_contas_antigas),
                    ).fetchone() is not None:
                        raise RuntimeError("Não foi possível validar a exclusão de orcamentos_transferidos.")

        # -----------------------------------------------------------------------------
        # Financeiro antigo
        # -----------------------------------------------------------------------------
        if _tabela_existe(cursor, "boletos"):
            cursor.execute(
                """
                DELETE FROM boletos
                WHERE paciente_id = ?
                """,
                (paciente_id,),
            )
            if cursor.execute(
                """
                SELECT 1
                FROM boletos
                WHERE paciente_id = ?
                LIMIT 1
                """,
                (paciente_id,),
            ).fetchone() is not None:
                raise RuntimeError("Não foi possível validar a exclusão de boletos.")

        if _tabela_existe(cursor, "notas_fiscais"):
            cursor.execute(
                """
                DELETE FROM notas_fiscais
                WHERE paciente_id = ?
                """,
                (paciente_id,),
            )
            if cursor.execute(
                """
                SELECT 1
                FROM notas_fiscais
                WHERE paciente_id = ?
                LIMIT 1
                """,
                (paciente_id,),
            ).fetchone() is not None:
                raise RuntimeError("Não foi possível validar a exclusão de notas_fiscais.")

        # -----------------------------------------------------------------------------
        # Contas a receber
        # -----------------------------------------------------------------------------
        if _tabela_existe(cursor, "contas_receber"):
            cursor.execute(
                """
                DELETE FROM contas_receber
                WHERE paciente_id = ?
                """,
                (paciente_id,),
            )
            if cursor.execute(
                """
                SELECT 1
                FROM contas_receber
                WHERE paciente_id = ?
                LIMIT 1
                """,
                (paciente_id,),
            ).fetchone() is not None:
                raise RuntimeError("Não foi possível validar a exclusão de contas_receber.")

        # -----------------------------------------------------------------------------
        # Orçamentos
        # -----------------------------------------------------------------------------
        if _tabela_existe(cursor, "orcamentos_transferidos") and _tabela_existe(cursor, "orcamentos"):
            cursor.execute(
                """
                DELETE FROM orcamentos_transferidos
                WHERE orcamento_id IN (
                    SELECT id
                    FROM orcamentos
                    WHERE paciente_id = ?
                )
                """,
                (paciente_id,),
            )

        if _tabela_existe(cursor, "orcamentos"):
            cursor.execute(
                """
                DELETE FROM orcamentos
                WHERE paciente_id = ?
                """,
                (paciente_id,),
            )
            if cursor.execute(
                """
                SELECT 1
                FROM orcamentos
                WHERE paciente_id = ?
                LIMIT 1
                """,
                (paciente_id,),
            ).fetchone() is not None:
                raise RuntimeError("Não foi possível validar a exclusão de orcamentos.")

            if _tabela_existe(cursor, "orcamentos_transferidos"):
                if cursor.execute(
                    """
                    SELECT 1
                    FROM orcamentos_transferidos
                    WHERE orcamento_id IN (
                        SELECT id
                        FROM orcamentos
                        WHERE paciente_id = ?
                    )
                    LIMIT 1
                    """,
                    (paciente_id,),
                ).fetchone() is not None:
                    raise RuntimeError("Não foi possível validar a exclusão de orcamentos_transferidos.")

        # -----------------------------------------------------------------------------
        # Odontograma
        # -----------------------------------------------------------------------------
        for tabela in [
            "odontograma_procedimentos",
            "odontograma_faces",
            "odontograma",
        ]:
            if _tabela_existe(cursor, tabela):
                cursor.execute(
                    f'DELETE FROM "{tabela}" WHERE paciente_id = ?',
                    (paciente_id,),
                )
                if cursor.execute(
                    f'SELECT 1 FROM "{tabela}" WHERE paciente_id = ? LIMIT 1',
                    (paciente_id,),
                ).fetchone() is not None:
                    raise RuntimeError(f"Não foi possível validar a exclusão de {tabela}.")

        # -----------------------------------------------------------------------------
        # Agenda
        # -----------------------------------------------------------------------------
        if _tabela_existe(cursor, "consultas"):
            cursor.execute(
                """
                DELETE FROM consultas
                WHERE paciente_id = ?
                """,
                (paciente_id,),
            )
            if cursor.execute(
                """
                SELECT 1
                FROM consultas
                WHERE paciente_id = ?
                LIMIT 1
                """,
                (paciente_id,),
            ).fetchone() is not None:
                raise RuntimeError("Não foi possível validar a exclusão de consultas.")

        # -----------------------------------------------------------------------------
        # Paciente
        # -----------------------------------------------------------------------------
        cursor.execute(
            """
            DELETE FROM pacientes
            WHERE id = ?
            """,
            (paciente_id,),
        )

        if cursor.execute(
            """
            SELECT 1
            FROM pacientes
            WHERE id = ?
            """,
            (paciente_id,),
        ).fetchone() is not None:
            raise RuntimeError("Não foi possível validar a exclusão do paciente.")

        conexao.commit()

    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()
