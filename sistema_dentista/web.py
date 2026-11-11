import csv
import io
from flask import ( # pyright: ignore[reportMissingImports]
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash
)
from datetime import date

from sistema_dentista.database.connection import (
    criar_banco,
    criar_indices,
)

from .repositories.patients_repository import (
    cadastrar_paciente,
    listar_pacientes,
    listar_todos_pacientes,
    obter_paciente,
    atualizar_paciente,
    desativar_paciente,
    ativar_paciente,
    excluir_paciente_permanentemente
)


from .repositories.odontogram_repository import (
    criar_tabela_odontograma,
    listar_odontograma,
    salvar_dente,
    listar_faces_odontograma,
    salvar_face_odontograma,
    listar_procedimentos_odontograma,
    adicionar_procedimento_odontograma,
    excluir_procedimento_odontograma,
)


from .repositories.financial_repository import (
    adicionar_orcamento,
    excluir_orcamento,
    adicionar_conta_receber,
    marcar_receber_pago,
    adicionar_conta_pagar,
    marcar_pagar_pago,
    adicionar_movimentacao,
    adicionar_despesa_recorrente,
    alterar_status_despesa_recorrente,
    excluir_despesa_recorrente,
    sincronizar_despesas_recorrentes,
    criar_tabelas_conta_paciente,
    criar_tabelas_contas_individuais,
    listar_orcamentos_com_status_individual,
    total_orcamento_nao_transferido_individual,
    passar_orcamento_para_receber_individual,
    listar_contas_pendentes_paciente,
    listar_contas_quitadas_paciente,
    registrar_pagamento_conta_individual,
    excluir_pagamento_conta_individual,
    excluir_conta_orcamento_individual
)

from .repositories.agenda_repository import (
    criar_tabela_agenda_visual,
    preparar_agenda_semana,
    adicionar_evento,
    alterar_status_evento,
    excluir_evento,
)

from .repositories.treatments_repository import (
    criar_tabela_tratamentos,
    listar_tratamentos,
    adicionar_tratamento,
    alterar_status_tratamento,
    excluir_tratamento,
)

from .services.backup_service import verificar_backup_mensal


from .config import (
    TEMPLATES_DIR,
    STATIC_DIR,
    SECRET_KEY,
)

from .services.finance_summary_service import (
    calcular_resumo_dashboard,
    carregar_dados_financeiros,
)


def create_flask_app():
    app = Flask(
        __name__,
        template_folder=str(TEMPLATES_DIR),
        static_folder=str(STATIC_DIR),
        static_url_path="/static"
    )
    app.secret_key = SECRET_KEY

    @app.errorhandler(404)
    def pagina_nao_encontrada(erro):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def erro_interno(erro):
        app.logger.exception("Erro interno: %s", erro)
        return render_template("500.html"), 500

    
    # =========================================
    # BACKUP MENSAL
    # =========================================
    
    
    @app.before_request
    def executar_backup_mensal():

        try:
            verificar_backup_mensal()

        except Exception as erro:
            app.logger.exception(
                "Erro no backup mensal automatico: %s",
                erro,
            )
    
    
    
    # =========================================
    # FUNÇÕES AUXILIARES
    # =========================================
    
    # =========================================
    # DASHBOARD
    # =========================================
    
    @app.route("/")
    def inicio():
        resumo_dashboard = calcular_resumo_dashboard()

        return render_template(
            "index.html",
            total=resumo_dashboard["total"],
            confirmadas=resumo_dashboard["confirmadas"],
            aguardando=resumo_dashboard["aguardando"],
            canceladas=resumo_dashboard["canceladas"],
            total_pacientes=resumo_dashboard["total_pacientes"],
            total_receber=resumo_dashboard["total_receber"],
            total_pagar=resumo_dashboard["total_pagar"],
        )
    
    
    # =========================================
    # PACIENTES
    # =========================================
    
    @app.route("/pacientes")
    def pacientes():
        busca = request.args.get("busca", "").strip()
        pagina = request.args.get("page", 1, type=int)
        if pagina < 1:
            pagina = 1

        pacientes_lista, total = listar_todos_pacientes(
            busca, pagina=pagina, por_pagina=20
        )

        total_paginas = max(1, (total + 19) // 20)

        return render_template(
            "pacientes.html",
            pacientes=pacientes_lista,
            busca=busca,
            pagina=pagina,
            total=total,
            total_paginas=total_paginas,
        )
    
    
    @app.route("/pacientes/cadastrar", methods=["POST"])
    def cadastrar_paciente_web():
        nome = request.form.get("nome", "").strip()
        telefone = request.form.get("telefone", "").strip()

        if not nome or not telefone:
            flash("Preencha todos os campos.", "erro")
            return redirect(url_for("pacientes"))

        try:
            cadastrar_paciente(nome, telefone)
        except ValueError as erro:
            flash(str(erro), "erro")
            return redirect(url_for("pacientes"))

        flash(
            "Paciente cadastrado com sucesso!",
            "sucesso"
        )

        return redirect(url_for("pacientes"))
    
    
    @app.route("/pacientes/exportar")
    def exportar_pacientes_csv():
        pacientes_lista, _ = listar_todos_pacientes(por_pagina=100000)

        buffer = io.StringIO()
        escritor = csv.writer(buffer, delimiter=";", quoting=csv.QUOTE_MINIMAL)
        escritor.writerow([
            "ID", "Nome", "Telefone", "Status", "CPF", "RG",
            "Data de nascimento", "Endereço", "Prontuário", "Anamnese",
        ])

        for paciente in pacientes_lista:
            escritor.writerow([
                paciente["id"],
                paciente["nome"],
                paciente["telefone"],
                "Ativo" if paciente["ativo"] == 1 else "Inativo",
                paciente["cpf"] or "",
                paciente["rg"] or "",
                paciente["data_nascimento"] or "",
                paciente["endereco"] or "",
                paciente["prontuario"] or "",
                paciente["anamnese"] or "",
            ])

        resposta = app.response_class(
            buffer.getvalue(),
            mimetype="text/csv; charset=utf-8",
        )
        resposta.headers["Content-Disposition"] = (
            "attachment; filename=pacientes.csv"
        )
        return resposta
    @app.route("/pacientes/perfil/<int:paciente_id>")
    def perfil_paciente(paciente_id):
        paciente = obter_paciente(paciente_id)
    
        if paciente is None:
            flash(
                "Paciente não encontrado.",
                "erro"
            )
            return redirect(
                url_for("pacientes")
            )
    
        idade = None
        data_nascimento_formatada = ""
    
        if paciente["data_nascimento"]:
            try:
                nascimento = date.fromisoformat(
                    paciente["data_nascimento"]
                )
                hoje_data = date.today()
    
                idade = (
                    hoje_data.year
                    - nascimento.year
                    - (
                        (hoje_data.month, hoje_data.day)
                        < (nascimento.month, nascimento.day)
                    )
                )
    
                data_nascimento_formatada = (
                    nascimento.strftime("%d/%m/%Y")
                )
            except ValueError:
                idade = None
                data_nascimento_formatada = ""
    
        orcamentos = (
            listar_orcamentos_com_status_individual(
                paciente_id
            )
        )
    
        total_orcamentos = sum(
            item["valor"]
            for item in orcamentos
        )
    
        total_nao_transferido = (
            total_orcamento_nao_transferido_individual(
                paciente_id
            )
        )
    
        contas_pendentes = (
            listar_contas_pendentes_paciente(
                paciente_id
            )
        )
    
        contas_quitadas = (
            listar_contas_quitadas_paciente(
                paciente_id
            )
        )
    
        return render_template(
            "perfil_paciente.html",
            paciente=paciente,
            orcamentos=orcamentos,
            total_orcamentos=total_orcamentos,
            total_nao_transferido=total_nao_transferido,
            contas_pendentes=contas_pendentes,
            contas_quitadas=contas_quitadas,
            idade=idade,
            data_nascimento_formatada=data_nascimento_formatada,
            hoje=date.today().isoformat()
        )
    
    
    @app.route(
        "/pacientes/<int:paciente_id>/receber/passar-orcamento",
        methods=["POST"]
    )
    def passar_orcamento_receber_web(paciente_id):
        vencimento = request.form.get(
            "vencimento",
            ""
        )
    
        try:
            resultado = (
                passar_orcamento_para_receber_individual(
                    paciente_id,
                    vencimento
                )
            )
        except ValueError as erro:
            flash(
                str(erro),
                "erro"
            )
        else:
            flash(
                (
                    f"Conta #{resultado['conta_id']} criada: "
                    f"R$ {resultado['valor']:.2f}."
                ),
                "sucesso"
            )
    
        return redirect(
            url_for(
                "perfil_paciente",
                paciente_id=paciente_id
            )
        )
    
    @app.route(
        "/pacientes/<int:paciente_id>/receber/<int:conta_id>/pagamento",
        methods=["POST"]
    )
    def registrar_pagamento_paciente_web(
        paciente_id,
        conta_id
    ):
        try:
            saldo = registrar_pagamento_conta_individual(
                paciente_id=paciente_id,
                conta_id=conta_id,
                valor=request.form.get(
                    "valor",
                    "0"
                ),
                data_pagamento=request.form.get(
                    "data_pagamento",
                    ""
                ),
                observacao=request.form.get(
                    "observacao",
                    ""
                )
            )
        except ValueError as erro:
            flash(
                str(erro),
                "erro"
            )
        else:
            if saldo <= 0.000001:
                flash(
                    (
                        f"Orçamento #{conta_id} "
                        "foi totalmente pago."
                    ),
                    "sucesso"
                )
            else:
                flash(
                    (
                        "Pagamento registrado. "
                        f"Saldo desta conta: R$ {saldo:.2f}."
                    ),
                    "sucesso"
                )
    
        return redirect(
            url_for(
                "perfil_paciente",
                paciente_id=paciente_id
            )
        )
    
    @app.route(
        "/pacientes/<int:paciente_id>/receber/pagamento/<int:pagamento_id>/excluir",
        methods=["POST"]
    )
    def excluir_pagamento_paciente_web(
        paciente_id,
        pagamento_id
    ):
        try:
            excluir_pagamento_conta_individual(
                paciente_id,
                pagamento_id
            )
        except ValueError as erro:
            flash(
                str(erro),
                "erro"
            )
        else:
            flash(
                "Pagamento excluído e saldo recalculado.",
                "sucesso"
            )
    
        return redirect(
            url_for(
                "perfil_paciente",
                paciente_id=paciente_id
            )
        )
    
    
    @app.route(
        "/pacientes/perfil/<int:paciente_id>/salvar",
        methods=["POST"]
    )
    def salvar_perfil_paciente(paciente_id):
        paciente = obter_paciente(paciente_id)
    
        if paciente is None:
            flash("Paciente não encontrado.", "erro")
            return redirect(url_for("pacientes"))
    
        nome = request.form.get("nome", "").strip()
        telefone = request.form.get("telefone", "").strip()
        cpf = request.form.get("cpf", "").strip()
        rg = request.form.get("rg", "").strip()
        data_nascimento = request.form.get(
            "data_nascimento",
            ""
        ).strip()
        tem_responsavel = (
            request.form.get("tem_responsavel") == "1"
        )
        responsavel_nome = request.form.get(
            "responsavel_nome",
            ""
        ).strip()
        responsavel_cpf = request.form.get(
            "responsavel_cpf",
            ""
        ).strip()
        responsavel_relacao = request.form.get(
            "responsavel_relacao",
            ""
        ).strip()
    
        prontuario = request.form.get("prontuario", "")
        anamnese = request.form.get("anamnese", "")
        endereco = request.form.get("endereco", "")
    
        if data_nascimento:
            try:
                nascimento = date.fromisoformat(
                    data_nascimento
                )
            except ValueError:
                flash(
                    "Data de nascimento inválida.",
                    "erro"
                )
                return redirect(
                    url_for(
                        "perfil_paciente",
                        paciente_id=paciente_id
                    )
                )
    
            if nascimento > date.today():
                flash(
                    "A data de nascimento não pode estar no futuro.",
                    "erro"
                )
                return redirect(
                    url_for(
                        "perfil_paciente",
                        paciente_id=paciente_id
                    )
                )
    
        if tem_responsavel:
            if (
                not responsavel_nome
                or not responsavel_cpf
                or not responsavel_relacao
            ):
                flash(
                    (
                        "Ao informar responsável, preencha "
                        "nome, CPF e relação com o paciente."
                    ),
                    "erro"
                )
                return redirect(
                    url_for(
                        "perfil_paciente",
                        paciente_id=paciente_id
                    )
                )
        else:
            responsavel_nome = ""
            responsavel_cpf = ""
            responsavel_relacao = ""
    
        if not nome or not telefone:
            flash("Nome e telefone são obrigatórios.", "erro")
            return redirect(
                url_for(
                    "perfil_paciente",
                    paciente_id=paciente_id
                )
            )
    
        try:
            atualizar_paciente(
                paciente_id,
                nome,
                telefone,
                prontuario,
                anamnese,
                endereco,
                cpf,
                rg,
                data_nascimento,
                tem_responsavel,
                responsavel_nome,
                responsavel_cpf,
                responsavel_relacao
            )
        except ValueError as erro:
            flash(str(erro), "erro")
            return redirect(
                url_for(
                    "perfil_paciente",
                    paciente_id=paciente_id
                )
            )

        flash(
            "Perfil atualizado com sucesso!",
            "sucesso"
        )
    
        return redirect(
            url_for(
                "perfil_paciente",
                paciente_id=paciente_id
            )
        )
    
    
    @app.route(
        "/pacientes/desativar/<int:paciente_id>",
        methods=["POST"]
    )
    def desativar_paciente_web(paciente_id):
        desativar_paciente(paciente_id)
    
        flash(
            "Paciente descadastrado. O histórico foi mantido.",
            "sucesso"
        )
    
        return redirect(url_for("pacientes"))
    
    
    @app.route(
        "/pacientes/ativar/<int:paciente_id>",
        methods=["POST"]
    )
    def ativar_paciente_web(paciente_id):
        ativar_paciente(paciente_id)
    
        flash(
            "Paciente reativado com sucesso!",
            "sucesso"
        )
    
        return redirect(url_for("pacientes"))
    
    
    @app.route(
        "/pacientes/excluir/<int:paciente_id>",
        methods=["POST"]
    )
    def excluir_paciente_web(paciente_id):
        try:
            excluir_paciente_permanentemente(paciente_id)
        except ValueError as erro:
            app.logger.warning(
                "Exclusão de paciente não concluída para id %s: %s",
                paciente_id,
                erro,
            )

            flash(
                str(erro),
                "erro"
            )
        except Exception as erro:
            app.logger.exception(
                "Erro ao excluir paciente permanentemente para id %s",
                paciente_id,
            )

            flash(
                "Não foi possível concluir a exclusão do paciente.",
                "erro"
            )
        else:
            flash(
                "Paciente e dados associados excluídos permanentemente.",
                "sucesso"
            )

        return redirect(url_for("pacientes"))
    
    
    # =========================================
    # AGENDA
    # =========================================
    
    @app.route("/agenda")
    def agenda():
        semana = request.args.get(
            "semana",
            ""
        )
    
        dados_agenda = preparar_agenda_semana(
            semana or None
        )
    
        # A Agenda continua independente: os pacientes cadastrados
        # são usados apenas como sugestões para preencher nome/telefone.
        pacientes_agenda, _ = listar_pacientes(por_pagina=100000)
    
        return render_template(
            "agenda.html",
            agenda=dados_agenda,
            pacientes=pacientes_agenda
        )
    
    
    @app.route(
        "/agenda/evento/adicionar",
        methods=["POST"]
    )
    def adicionar_evento_agenda_web():
        # Lê hora e minuto separadamente.
        hora_inicio_h = request.form.get(
            "hora_inicio_h",
            ""
        )
    
        hora_inicio_m = request.form.get(
            "hora_inicio_m",
            ""
        )
    
        hora_fim_h = request.form.get(
            "hora_fim_h",
            ""
        )
    
        hora_fim_m = request.form.get(
            "hora_fim_m",
            ""
        )
    
        # Monta o horário final no formato HH:MM.
        hora_inicio = ""
    
        if hora_inicio_h and hora_inicio_m:
            hora_inicio = (
                f"{hora_inicio_h}:{hora_inicio_m}"
            )
    
        hora_fim = ""
    
        if hora_fim_h and hora_fim_m:
            hora_fim = (
                f"{hora_fim_h}:{hora_fim_m}"
            )
    
        try:
            adicionar_evento(
                nome=request.form.get(
                    "nome",
                    ""
                ),
                telefone=request.form.get(
                    "telefone",
                    ""
                ),
                titulo=request.form.get(
                    "titulo",
                    "Consulta"
                ),
                data_evento=request.form.get(
                    "data",
                    ""
                ),
                hora_inicio=hora_inicio,
                hora_fim=hora_fim,
                observacao=request.form.get(
                    "observacao",
                    ""
                ),
                cor=request.form.get(
                    "cor",
                    "azul"
                )
            )
    
        except ValueError as erro:
            flash(
                str(erro),
                "erro"
            )
    
        else:
            flash(
                "Agendamento criado.",
                "sucesso"
            )
    
        return redirect(
            url_for(
                "agenda",
                semana=request.form.get(
                    "data",
                    ""
                )
            )
        )
    
    @app.route(
        "/agenda/evento/<int:evento_id>/status/<status>",
        methods=["POST"]
    )
    def status_evento_agenda_web(
        evento_id,
        status
    ):
        try:
            alterar_status_evento(
                evento_id,
                status
            )
        except ValueError as erro:
            flash(
                str(erro),
                "erro"
            )
    
        return redirect(
            request.referrer
            or url_for("agenda")
        )
    
    
    @app.route(
        "/agenda/evento/<int:evento_id>/excluir",
        methods=["POST"]
    )
    def excluir_evento_agenda_web(
        evento_id
    ):
        excluir_evento(
            evento_id
        )
    
        flash(
            "Agendamento excluído.",
            "sucesso"
        )
    
        return redirect(
            request.referrer
            or url_for("agenda")
        )
    
    # =========================================
    # ODONTOGRAMA
    # =========================================
    
    @app.route(
        "/pacientes/<int:paciente_id>/odontograma"
    )
    def odontograma_paciente(paciente_id):
    
        faces = listar_faces_odontograma(
            paciente_id
        )
    
        procedimentos = listar_procedimentos_odontograma(
            paciente_id
        )
    
    
        paciente = obter_paciente(
            paciente_id
        )    
    
        if paciente is None:
    
            return (
                "Paciente não encontrado.",
                404
            )
    
    
        odontograma = listar_odontograma(
            paciente_id
        )
    
    
        dentes_superiores_esquerda = [
            18, 17, 16, 15,
            14, 13, 12, 11
        ]
    
        dentes_superiores_direita = [
            21, 22, 23, 24,
            25, 26, 27, 28
        ]
    
        dentes_inferiores_esquerda = [
            48, 47, 46, 45,
            44, 43, 42, 41
        ]
    
        dentes_inferiores_direita = [
            31, 32, 33, 34,
            35, 36, 37, 38
        ]
    
    
        dentes_deciduos_superiores = [
            55, 54, 53, 52, 51,
            61, 62, 63, 64, 65
        ]
    
        dentes_deciduos_inferiores = [
            85, 84, 83, 82, 81,
            71, 72, 73, 74, 75
        ]
    
    
        return render_template(
            "odontograma.html",
    
            faces=faces,
    
            procedimentos=procedimentos,
    
            paciente=paciente,
    
            odontograma=odontograma,
            
            hoje=date.today().isoformat(),
    
            dentes_superiores_esquerda=
                dentes_superiores_esquerda,
    
            dentes_superiores_direita=
                dentes_superiores_direita,
    
            dentes_inferiores_esquerda=
                dentes_inferiores_esquerda,
    
            dentes_inferiores_direita=
                dentes_inferiores_direita,
    
            dentes_deciduos_superiores=
                dentes_deciduos_superiores,
    
            dentes_deciduos_inferiores=
                dentes_deciduos_inferiores
        )
    
    
    
    @app.route(
        "/pacientes/<int:paciente_id>/odontograma/salvar",
        methods=["POST"]
    )
    def salvar_odontograma(paciente_id):
        dados = request.get_json(silent=True) or {}
    
        dente = str(dados.get("dente", "")).strip()
        estado = dados.get("estado")
        observacao = dados.get("observacao", "") or ""
    
        if not dente:
            return {
                "sucesso": False,
                "erro": "Dente não informado."
            }, 400
    
        # Se a requisição veio apenas para salvar a observação,
        # preserva o estado atual do dente.
        if not estado:
            dados_atuais = listar_odontograma(paciente_id)
            estado = dados_atuais.get(dente, {}).get(
                "estado",
                "Saudável"
            )
    
        try:
            salvar_dente(
                paciente_id,
                dente,
                estado,
                observacao
            )
        except Exception as erro:
            app.logger.exception(
                "Erro ao salvar odontograma: %s",
                erro,
            )
            return {
                "sucesso": False,
                "erro": "Não foi possível salvar o odontograma."
            }, 500
    
        return {
            "sucesso": True,
            "dente": dente,
            "estado": estado,
            "observacao": observacao
        }
    
    @app.route(
        "/pacientes/<int:paciente_id>/odontograma/face/salvar",
        methods=["POST"]
    )
    def salvar_face_odontograma_web(paciente_id):
        dados = request.get_json() or {}
    
        dente = dados.get("dente")
        face = dados.get("face")
        estado = dados.get("estado")
    
        if not dente or not face or not estado:
            return {
                "sucesso": False,
                "erro": "Dente, face e estado são obrigatórios."
            }, 400
    
        try:
            salvar_face_odontograma(
                paciente_id,
                dente,
                face,
                estado
            )
        except ValueError as erro:
            return {
                "sucesso": False,
                "erro": str(erro)
            }, 400
    
        return {
            "sucesso": True
        }
    
    
    @app.route(
        "/pacientes/<int:paciente_id>/odontograma/procedimento/adicionar",
        methods=["POST"]
    )
    def adicionar_procedimento_odontograma_web(paciente_id):
        try:
            adicionar_procedimento_odontograma(
                paciente_id=paciente_id,
                procedimento=request.form.get(
                    "procedimento",
                    ""
                ),
                data_procedimento=request.form.get(
                    "data_procedimento",
                    ""
                ),
                descricao=request.form.get(
                    "descricao",
                    ""
                ),
                dente=request.form.get(
                    "dente",
                    ""
                ),
                face=request.form.get(
                    "face",
                    ""
                ),
                estado=request.form.get(
                    "estado",
                    "Saudável"
                )
            )
        except ValueError as erro:
            flash(str(erro), "erro")
        else:
            flash(
                "Procedimento adicionado ao odontograma.",
                "sucesso"
            )
    
        return redirect(
            url_for(
                "odontograma_paciente",
                paciente_id=paciente_id
            )
        )
    
    
    @app.route(
        "/pacientes/<int:paciente_id>/odontograma/procedimento/<int:procedimento_id>/excluir",
        methods=["POST"]
    )
    def excluir_procedimento_odontograma_web(
        paciente_id,
        procedimento_id
    ):
        excluir_procedimento_odontograma(
            procedimento_id,
            paciente_id
        )
    
        flash(
            "Registro clínico excluído.",
            "sucesso"
        )
    
        return redirect(
            url_for(
                "odontograma_paciente",
                paciente_id=paciente_id
            )
        )
    
    
    # =========================================
    # TRATAMENTOS
    # =========================================
    
    @app.route(
        "/pacientes/<int:paciente_id>/tratamento"
    )
    def tratamento_paciente(
        paciente_id
    ):
        paciente = obter_paciente(
            paciente_id
        )
    
        if paciente is None:
            return (
                "Paciente não encontrado.",
                404
            )
    
        tratamentos = listar_tratamentos(
            paciente_id
        )
    
        return render_template(
            "tratamento.html",
            paciente=paciente,
            tratamentos=tratamentos
        )
    
    
    @app.route(
        "/pacientes/<int:paciente_id>/tratamento/adicionar",
        methods=["POST"]
    )
    def adicionar_tratamento_web(
        paciente_id
    ):
        try:
            adicionar_tratamento(
                paciente_id=paciente_id,
                procedimento=request.form.get(
                    "procedimento",
                    ""
                ),
                data_inicio=request.form.get(
                    "data_inicio",
                    ""
                ),
                observacao=request.form.get(
                    "observacao",
                    ""
                ),
            )
        except ValueError as erro:
            flash(
                str(erro),
                "erro"
            )
        else:
            flash(
                "Procedimento adicionado ao tratamento.",
                "sucesso"
            )
    
        return redirect(
            url_for(
                "tratamento_paciente",
                paciente_id=paciente_id
            )
        )
    
    
    @app.route(
        "/pacientes/<int:paciente_id>/tratamento/<int:tratamento_id>/status/<status>",
        methods=["POST"]
    )
    def status_tratamento_web(
        paciente_id,
        tratamento_id,
        status
    ):
        try:
            alterar_status_tratamento(
                tratamento_id,
                paciente_id,
                status
            )
        except ValueError as erro:
            flash(
                str(erro),
                "erro"
            )
    
        return redirect(
            url_for(
                "tratamento_paciente",
                paciente_id=paciente_id
            )
        )
    
    
    @app.route(
        "/pacientes/<int:paciente_id>/tratamento/<int:tratamento_id>/excluir",
        methods=["POST"]
    )
    def excluir_tratamento_web(
        paciente_id,
        tratamento_id
    ):
        excluir_tratamento(
            tratamento_id,
            paciente_id
        )
    
        flash(
            "Item do tratamento excluído.",
            "sucesso"
        )
    
        return redirect(
            url_for(
                "tratamento_paciente",
                paciente_id=paciente_id
            )
        )
    
    
    
    # =========================================
    # ORÇAMENTOS
    # =========================================
    
    @app.route(
        "/orcamentos/<int:paciente_id>/adicionar",
        methods=["POST"]
    )
    def adicionar_orcamento_web(paciente_id):
        categoria = request.form.get("categoria", "Clínica Geral")
        descricao = request.form.get("descricao", "").strip()
        valor = request.form.get("valor", "0")
    
        if not descricao:
            flash("Informe a descrição do procedimento.", "erro")
            return redirect(
                url_for(
                    "perfil_paciente",
                    paciente_id=paciente_id
                )
            )
    
        adicionar_orcamento(
            paciente_id,
            categoria,
            descricao,
            valor
        )
    
        flash(
            "Item de orçamento adicionado.",
            "sucesso"
        )
    
        return redirect(
            url_for(
                "perfil_paciente",
                paciente_id=paciente_id
            )
        )
    
    
    @app.route(
        "/orcamentos/excluir/<int:orcamento_id>",
        methods=["POST"]
    )
    def excluir_orcamento_web(orcamento_id):
        paciente_id = request.form.get("paciente_id")
    
        excluir_orcamento(orcamento_id)
    
        flash(
            "Item do orçamento excluído.",
            "sucesso"
        )
    
        if paciente_id:
            return redirect(
                url_for(
                    "perfil_paciente",
                    paciente_id=paciente_id
                )
            )
    
        return redirect(url_for("financeiro"))
    
    
    # =========================================
    # FINANCEIRO
    # =========================================
    
    @app.route("/financeiro/exportar")
    def exportar_financeiro_csv():
        resumo = carregar_dados_financeiros()

        buffer = io.StringIO()
        escritor = csv.writer(buffer, delimiter=";", quoting=csv.QUOTE_MINIMAL)

        escritor.writerow(["=== CONTAS A RECEBER ==="])
        escritor.writerow([
            "ID", "Paciente", "Descrição", "Valor", "Vencimento", "Status",
        ])
        for conta in resumo["receber"]:
            escritor.writerow([
                conta["id"],
                conta["paciente_nome"] or "Sem paciente",
                conta["descricao"],
                f"{conta['valor']:.2f}".replace(".", ","),
                conta["vencimento"],
                conta["status"],
            ])

        escritor.writerow([])
        escritor.writerow(["=== CONTAS A PAGAR ==="])
        escritor.writerow([
            "ID", "Fornecedor", "Descrição", "Valor", "Vencimento", "Status",
        ])
        for conta in resumo["pagar"]:
            escritor.writerow([
                conta["id"],
                conta["fornecedor"] or "-",
                conta["descricao"],
                f"{conta['valor']:.2f}".replace(".", ","),
                conta["vencimento"],
                conta["status"],
            ])

        escritor.writerow([])
        escritor.writerow(["=== MOVIMENTAÇÕES DO MÊS ==="])
        escritor.writerow(["Data", "Descrição", "Tipo", "Valor"])
        for mov in resumo["movimentacoes"]:
            escritor.writerow([
                mov["data"],
                mov["descricao"],
                mov["tipo"],
                f"{mov['valor']:.2f}".replace(".", ","),
            ])

        resposta = app.response_class(
            buffer.getvalue(),
            mimetype="text/csv; charset=utf-8",
        )
        resposta.headers["Content-Disposition"] = (
            "attachment; filename=financeiro.csv"
        )
        return resposta

    @app.route("/financeiro")
    def financeiro():
        resumo_financeiro = carregar_dados_financeiros(

            request.args.get("ano")

        )



        receber = resumo_financeiro["receber"]

        pagar = resumo_financeiro["pagar"]

        movimentacoes = resumo_financeiro["movimentacoes"]

        despesas_recorrentes = resumo_financeiro["despesas_recorrentes"]

        pacientes_lista = resumo_financeiro["pacientes"]

        total_receber = resumo_financeiro["total_receber"]

        total_pagar = resumo_financeiro["total_pagar"]

        entradas = resumo_financeiro["entradas"]

        saidas = resumo_financeiro["saidas"]

        saldo = resumo_financeiro["saldo"]

        anos_gastos = resumo_financeiro["anos_gastos"]

        ano_selecionado = resumo_financeiro["ano_selecionado"]

        gastos_mensais = resumo_financeiro["gastos_mensais"]

        gastos_anuais = resumo_financeiro["gastos_anuais"]

        total_gastos_ano = resumo_financeiro["total_gastos_ano"]

        total_gastos_ano_pago = resumo_financeiro["total_gastos_ano_pago"]

        total_gastos_ano_pendente = resumo_financeiro["total_gastos_ano_pendente"]

        total_entradas_ano = resumo_financeiro["total_entradas_ano"]

        total_saidas_ano = resumo_financeiro["total_saidas_ano"]

        saldo_fluxo_ano = resumo_financeiro["saldo_fluxo_ano"]

        hoje_data = resumo_financeiro["hoje_data"]

        meses_pt = {
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
    
        return render_template(
            "financeiro.html",
    
            receber=receber,
            pagar=pagar,
            movimentacoes=movimentacoes,
            pacientes=pacientes_lista,
            despesas_recorrentes=despesas_recorrentes,
    
            total_receber=total_receber,
            total_pagar=total_pagar,
    
            entradas=entradas,
            saidas=saidas,
            saldo=saldo,
    
            anos_gastos=anos_gastos,
            ano_selecionado=ano_selecionado,
            gastos_mensais=gastos_mensais,
            gastos_anuais=gastos_anuais,
    
            total_gastos_ano=total_gastos_ano,
            total_gastos_ano_pago=total_gastos_ano_pago,
            total_gastos_ano_pendente=total_gastos_ano_pendente,
    
            total_entradas_ano=total_entradas_ano,
            total_saidas_ano=total_saidas_ano,
            saldo_fluxo_ano=saldo_fluxo_ano,
    
            mes_atual_nome=meses_pt[hoje_data.month],
            ano_atual=hoje_data.year,
            hoje=hoje_data.isoformat()
        )
    
    
    @app.route(
        "/financeiro/receber/adicionar",
        methods=["POST"]
    )
    def adicionar_receber_web():
        paciente_id = request.form.get("paciente_id")
        descricao = request.form.get("descricao", "").strip()
        valor = request.form.get("valor", "0")
        vencimento = request.form.get("vencimento", "")
    
        if not descricao or not vencimento:
            flash("Preencha descrição e vencimento.", "erro")
            return redirect(url_for("financeiro"))
    
        adicionar_conta_receber(
            paciente_id,
            descricao,
            valor,
            vencimento
        )
    
        flash(
            "Conta a receber adicionada.",
            "sucesso"
        )
    
        return redirect(url_for("financeiro"))
    
    
    @app.route(
        "/financeiro/receber/pagar/<int:conta_id>",
        methods=["POST"]
    )
    def pagar_receber_web(conta_id):
        marcar_receber_pago(conta_id)
    
        flash(
            "Conta marcada como paga.",
            "sucesso"
        )
    
        return redirect(url_for("financeiro"))
    
    
    @app.route(
        "/financeiro/pagar/adicionar",
        methods=["POST"]
    )
    def adicionar_pagar_web():
        descricao = request.form.get("descricao", "").strip()
        fornecedor = request.form.get("fornecedor", "").strip()
        valor = request.form.get("valor", "0")
        vencimento = request.form.get("vencimento", "")
    
        if not descricao or not vencimento:
            flash("Preencha descrição e vencimento.", "erro")
            return redirect(url_for("financeiro"))
    
        adicionar_conta_pagar(
            descricao,
            fornecedor,
            valor,
            vencimento
        )
    
        flash(
            "Conta a pagar adicionada.",
            "sucesso"
        )
    
        return redirect(url_for("financeiro"))
    
    
    @app.route(
        "/financeiro/pagar/pagar/<int:conta_id>",
        methods=["POST"]
    )
    def pagar_conta_web(conta_id):
        marcar_pagar_pago(conta_id)
    
        flash(
            "Conta marcada como paga.",
            "sucesso"
        )
    
        return redirect(url_for("financeiro"))
    
    
    @app.route(
        "/financeiro/movimentacao/adicionar",
        methods=["POST"]
    )
    def adicionar_movimentacao_web():
        descricao = request.form.get("descricao", "").strip()
        tipo = request.form.get("tipo", "Entrada")
        valor = request.form.get("valor", "0")
        data_mov = request.form.get("data", "")
    
        if not descricao or not data_mov:
            flash("Preencha todos os campos.", "erro")
            return redirect(url_for("financeiro"))
    
        if tipo not in ["Entrada", "Saída"]:
            tipo = "Entrada"
    
        adicionar_movimentacao(
            descricao,
            tipo,
            valor,
            data_mov
        )
    
        flash(
            "Movimentação adicionada ao fluxo de caixa.",
            "sucesso"
        )
    
        return redirect(url_for("financeiro"))
    
    @app.route(
        "/pacientes/<int:paciente_id>/receber/<int:conta_id>/excluir",
        methods=["POST"]
    )
    def excluir_conta_paciente_web(
        paciente_id,
        conta_id
    ):
        try:
            excluir_conta_orcamento_individual(
                paciente_id,
                conta_id
            )
        except ValueError as erro:
            flash(
                str(erro),
                "erro"
            )
        else:
            flash(
                f"Conta #{conta_id} apagada.",
                "sucesso"
            )
    
        return redirect(
            url_for(
                "perfil_paciente",
                paciente_id=paciente_id
            )
        )
    
    # =========================================
    # DESPESAS RECORRENTES
    # =========================================
    
    @app.route(
        "/financeiro/despesa-recorrente/adicionar",
        methods=["POST"]
    )
    def adicionar_despesa_recorrente_web():
        descricao = request.form.get("descricao", "").strip()
        fornecedor = request.form.get("fornecedor", "").strip()
        categoria = request.form.get("categoria", "Outros").strip()
        valor = request.form.get("valor", "0")
        recorrencia = request.form.get("recorrencia", "Mensal")
        dia_vencimento = request.form.get("dia_vencimento", "")
        mes_vencimento = request.form.get("mes_vencimento")
    
        if not descricao or not dia_vencimento:
            flash("Informe a descrição e o dia de vencimento.", "erro")
            return redirect(url_for("financeiro"))
    
        try:
            adicionar_despesa_recorrente(
                descricao,
                fornecedor,
                categoria,
                valor,
                recorrencia,
                dia_vencimento,
                mes_vencimento
            )
            sincronizar_despesas_recorrentes()
        except ValueError as erro:
            flash(str(erro), "erro")
            return redirect(url_for("financeiro"))
    
        flash("Despesa recorrente adicionada.", "sucesso")
        return redirect(url_for("financeiro"))
    
    
    @app.route(
        "/financeiro/despesa-recorrente/<int:despesa_id>/status/<int:ativa>",
        methods=["POST"]
    )
    def status_despesa_recorrente_web(despesa_id, ativa):
        alterar_status_despesa_recorrente(
            despesa_id,
            ativa == 1
        )
    
        flash(
            "Despesa recorrente ativada." if ativa == 1
            else "Despesa recorrente pausada.",
            "sucesso"
        )
        return redirect(url_for("financeiro"))
    
    
    @app.route(
        "/financeiro/despesa-recorrente/<int:despesa_id>/excluir",
        methods=["POST"]
    )
    def excluir_despesa_recorrente_web(despesa_id):
        excluir_despesa_recorrente(despesa_id)
        flash(
            "Regra de despesa recorrente excluída. "
            "As contas já geradas foram mantidas.",
            "sucesso"
        )
        return redirect(url_for("financeiro"))
    
    
    # =========================================
    # EXCLUSÕES DO FINANCEIRO
    # =========================================
    
    @app.route(
        "/financeiro/movimentacao/excluir/<int:movimentacao_id>",
        methods=["POST"]
    )
    def excluir_movimentacao_web(movimentacao_id):
        from .repositories.financial_repository import excluir_movimentacao
    
        excluir_movimentacao(movimentacao_id)
        flash("Movimentação excluída com sucesso.", "sucesso")
        return redirect(url_for("financeiro"))
    
    
    @app.route(
        "/financeiro/receber/excluir/<int:conta_id>",
        methods=["POST"]
    )
    def excluir_receber_web(conta_id):
        from .repositories.financial_repository import excluir_conta_receber
    
        excluir_conta_receber(conta_id)
        flash("Conta a receber excluída com sucesso.", "sucesso")
        return redirect(url_for("financeiro"))
    
    
    @app.route(
        "/financeiro/pagar/excluir/<int:conta_id>",
        methods=["POST"]
    )
    def excluir_pagar_web(conta_id):
        from .repositories.financial_repository import excluir_conta_pagar
    
        excluir_conta_pagar(conta_id)
        flash("Conta a pagar excluída com sucesso.", "sucesso")
        return redirect(url_for("financeiro"))
    

    return app


def initialize_database():
    criar_banco()
    criar_indices()
    criar_tabelas_conta_paciente()
    criar_tabela_odontograma()
    criar_tabelas_contas_individuais()
    criar_tabela_agenda_visual()
    criar_tabela_tratamentos()
