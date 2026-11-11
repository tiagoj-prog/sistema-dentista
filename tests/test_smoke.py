"""Smoke tests leves para a aplicação Sistema Dentista.

Estes testes não inicializam o banco e não executam migrações.
Eles verificam a criação da aplicação Flask, o número de rotas, os
endpoints esperados e a configuração dos caminhos de templates/static.
"""

import unittest

from sistema_dentista import create_flask_app


ESPERADOS = {
    "inicio",
    "pacientes",
    "cadastrar_paciente_web",
    "perfil_paciente",
    "passar_orcamento_receber_web",
    "registrar_pagamento_paciente_web",
    "excluir_pagamento_paciente_web",
    "salvar_perfil_paciente",
    "desativar_paciente_web",
    "ativar_paciente_web",
    "excluir_paciente_web",
    "agenda",
    "adicionar_evento_agenda_web",
    "status_evento_agenda_web",
    "excluir_evento_agenda_web",
    "odontograma_paciente",
    "salvar_odontograma",
    "salvar_face_odontograma_web",
    "adicionar_procedimento_odontograma_web",
    "excluir_procedimento_odontograma_web",
    "tratamento_paciente",
    "adicionar_tratamento_web",
    "status_tratamento_web",
    "excluir_tratamento_web",
    "adicionar_orcamento_web",
    "excluir_orcamento_web",
    "financeiro",
    "adicionar_receber_web",
    "pagar_receber_web",
    "adicionar_pagar_web",
    "pagar_conta_web",
    "adicionar_movimentacao_web",
    "excluir_conta_paciente_web",
    "adicionar_despesa_recorrente_web",
    "status_despesa_recorrente_web",
    "excluir_despesa_recorrente_web",
    "excluir_movimentacao_web",
    "excluir_receber_web",
    "excluir_pagar_web",
    "exportar_pacientes_csv",
    "exportar_financeiro_csv",
}


class TestSmoke(unittest.TestCase):

    def test_create_flask_app(self):
        app = create_flask_app()
        self.assertIsNotNone(app)
        self.assertTrue(app.template_folder.endswith("templates"))
        self.assertTrue(app.static_folder.endswith("static"))
        self.assertEqual(app.static_url_path, "/static")

    def test_dashboard_route_count(self):
        app = create_flask_app()
        rules = [
            rule
            for rule in app.url_map.iter_rules()
            if rule.endpoint != "static"
        ]
        self.assertEqual(len(rules), 41)

    def test_expected_endpoints_exist(self):
        app = create_flask_app()
        endpoints = set(app.view_functions) - {"static"}
        self.assertTrue(ESPERADOS.issubset(endpoints))

    def test_before_request_backup_is_registered(self):
        app = create_flask_app()
        before_request_funcs = app.before_request_funcs.get(None, [])
        self.assertTrue(
            any(func.__name__ == "executar_backup_mensal" for func in before_request_funcs)
        )


if __name__ == "__main__":
    unittest.main()