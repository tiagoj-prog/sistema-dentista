"""Pacote principal do Sistema Dentista.

A importação deste pacote não cria uma aplicação Flask nem inicializa o banco.
As funções públicas exigem chamada explícita.
"""


def create_flask_app():
    """Cria e configura a aplicação Flask, sem inicializar o banco."""
    from .web import create_flask_app as _create_flask_app

    return _create_flask_app()


def initialize_database():
    """Executa a inicialização do banco, separada da criação do Flask."""
    from .web import initialize_database as _initialize_database

    return _initialize_database()


def create_app(init_database=True):
    """Combina a criação do Flask com a inicialização opcional do banco."""
    app = create_flask_app()

    if init_database:
        initialize_database()

    return app


__all__ = [
    "create_flask_app",
    "initialize_database",
    "create_app",
]