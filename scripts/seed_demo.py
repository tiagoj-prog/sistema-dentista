"""Cria um banco de demonstração com dados fictícios.

Uso:

    python scripts/seed_demo.py

O arquivo gerado é ``demo/dentista_demo.db``. O banco real
(``dentista.db``) nunca é aberto para escrita por este script.

Depois de gerar, rode a demonstração com:

    python scripts/run_demo.py
"""

import sqlite3
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DEMO_DIR = ROOT / "demo"
DEMO_DB = DEMO_DIR / "dentista_demo.db"
DEMO_BACKUPS = DEMO_DIR / "backups"
REAL_DB = ROOT / "dentista.db"


PACIENTES = [
    ("Maria Souza", "(11) 98888-1010", 1, "Clareamento e restauração no dente 16",
     "Sem alergias conhecidas.", "Rua das Acácias, 120", "", "", "1988-03-14"),
    ("João Pereira", "(11) 98888-1011", 1, "Extração do dente 38",
     "Hipertenso, usa losartana.", "Av. Central, 45", "", "", "1975-07-02"),
    ("Ana Beatriz Lima", "(11) 98888-1012", 1, "Manutenção de aparelho",
     "Sem observações.", "Rua Verde, 900", "", "", "2001-11-23"),
    ("Carlos Eduardo Rocha", "(11) 98888-1013", 1, "Implante no dente 36",
     "Ex-fumante.", "Rua do Comércio, 77", "", "", "1969-01-30"),
    ("Fernanda Alves", "(11) 98888-1014", 1, "Limpeza semestral",
     "Sensibilidade nos incisivos.", "Rua das Flores, 310", "", "", "1994-05-09"),
    ("Rafael Moreira", "(11) 98888-1015", 1, "Canal no dente 46",
     "Alergia a penicilina.", "Av. Brasil, 1520", "", "", "1983-09-18"),
    ("Juliana Castro", "(11) 98888-1016", 1, "Avaliação para prótese",
     "Sem observações.", "Rua Projetada, 12", "", "", "1990-12-05"),
    ("Pedro Henrique Dias", "(11) 98888-1017", 1, "Restauração no dente 21",
     "Bruxismo noturno.", "Rua Aurora, 88", "", "", "1997-02-27"),
    ("Luciana Prado", "(11) 98888-1018", 0, "Paciente inativa",
     "Transferiu o tratamento.", "Rua Antiga, 5", "", "", "1986-08-11"),
]


def _segunda_feira(hoje):
    return hoje - timedelta(days=hoje.weekday())


def criar_estrutura():
    import sistema_dentista.config as config

    config.DATABASE_PATH = DEMO_DB
    config.BACKUP_DIR = DEMO_BACKUPS

    from sistema_dentista.web import initialize_database

    initialize_database()


def inserir_dados(conexao):
    cursor = conexao.cursor()
    hoje = date.today()
    segunda = _segunda_feira(hoje)

    def dia(indice):
        return (segunda + timedelta(days=indice)).isoformat()

    # Pacientes
    cursor.executemany(
        """
        INSERT INTO pacientes
            (nome, telefone, ativo, prontuario, anamnese, endereco,
             cpf, rg, data_nascimento)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        PACIENTES,
    )

    # Consultas (usadas nos indicadores do dashboard)
    consultas = [
        (1, dia(0), "09:00", "Confirmada", 1),
        (2, dia(0), "10:30", "Confirmada", 1),
        (3, dia(1), "14:00", "Aguardando", 0),
        (4, dia(1), "16:30", "Confirmada", 1),
        (5, dia(2), "08:30", "Aguardando", 0),
        (6, dia(2), "11:00", "Confirmada", 1),
        (7, dia(3), "15:00", "Aguardando", 0),
        (8, dia(3), "17:30", "Cancelada", 0),
        (1, dia(7), "09:30", "Aguardando", 0),
        (4, dia(8), "10:00", "Aguardando", 0),
    ]
    cursor.executemany(
        """
        INSERT INTO consultas
            (paciente_id, data, horario, status, mensagem_enviada)
        VALUES (?, ?, ?, ?, ?)
        """,
        consultas,
    )

    # Agenda da semana atual
    eventos = [
        ("Maria Souza", "(11) 98888-1010", "Avaliação", dia(0), "09:00", "09:40",
         "Clareamento", "Agendado", "avaliacao"),
        ("João Pereira", "(11) 98888-1011", "Consulta", dia(0), "10:30", "11:10",
         "Avaliação pré-cirúrgica", "Agendado", "implante"),
        ("Fernanda Alves", "(11) 98888-1014", "Limpeza", dia(0), "14:00", "14:40",
         "Profilaxia", "Agendado", "limpeza"),
        ("Ana Beatriz Lima", "(11) 98888-1012", "Manutenção", dia(1), "14:00", "14:30",
         "Ajuste de aparelho", "Agendado", "retorno"),
        ("Carlos Eduardo Rocha", "(11) 98888-1013", "Cirurgia", dia(1), "16:30", "18:00",
         "Instalação de implante", "Agendado", "implante"),
        ("Rafael Moreira", "(11) 98888-1015", "Canal", dia(2), "08:30", "10:00",
         "Segunda sessão", "Agendado", "implante"),
        ("Juliana Castro", "(11) 98888-1016", "Avaliação", dia(2), "11:00", "11:40",
         "Prótese parcial", "Agendado", "avaliacao"),
        ("Pedro Henrique Dias", "(11) 98888-1017", "Restauração", dia(3), "15:00", "16:00",
         "Dente 21", "Agendado", "limpeza"),
        ("Maria Souza", "(11) 98888-1010", "Retorno", dia(4), "09:00", "09:30",
         "Controle", "Agendado", "retorno"),
        ("Fernanda Alves", "(11) 98888-1014", "Retorno", dia(4), "10:00", "10:30",
         "Reavaliação", "Agendado", "retorno"),
    ]
    cursor.executemany(
        """
        INSERT INTO agenda_eventos
            (nome, telefone, titulo, data, hora_inicio, hora_fim,
             observacao, status, cor)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        eventos,
    )

    # Odontograma da Maria Souza (paciente 1)
    dentes = [
        (1, "11", "superior", "Limpeza", ""),
        (1, "16", "superior", "Cárie", "Cárie oclusal"),
        (1, "21", "superior", "Restauração", "Restauração em resina"),
        (1, "26", "superior", "Ausente", "Extraído em 2024"),
        (1, "36", "inferior", "Implante", "Implante osseointegrado"),
        (1, "46", "inferior", "Canal", "Tratamento endodôntico"),
    ]
    cursor.executemany(
        """
        INSERT INTO odontograma
            (paciente_id, dente, arcada, estado, observacao)
        VALUES (?, ?, ?, ?, ?)
        """,
        dentes,
    )

    faces = [
        (1, "16", "O", "Cárie"),
        (1, "16", "M", "Restauração"),
        (1, "11", "V", "Limpeza"),
        (1, "36", "O", "Implante"),
        (1, "46", "O", "Canal"),
    ]
    cursor.executemany(
        """
        INSERT INTO odontograma_faces
            (paciente_id, dente, face, estado)
        VALUES (?, ?, ?, ?)
        """,
        faces,
    )

    procedimentos = [
        (1, "Restauração", dia(-30), "Resina composta", "16", "O", "Restauração"),
        (1, "Limpeza", dia(-30), "Profilaxia completa", "11", "V", "Limpeza"),
        (1, "Implante", dia(-90), "Instalação do pino", "36", "O", "Implante"),
        (1, "Canal", dia(-120), "Tratamento em sessão única", "46", "O", "Canal"),
    ]
    cursor.executemany(
        """
        INSERT INTO odontograma_procedimentos
            (paciente_id, procedimento, data_procedimento, descricao,
             dente, face, estado)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        procedimentos,
    )

    tratamentos = [
        (1, "Clareamento dental", dia(-14), "Em andamento", "Sessões semanais"),
        (1, "Restauração dente 16", dia(-30), "Concluído", ""),
        (2, "Extração do dente 38", dia(-7), "Planejado", "Aguardando exames"),
        (2, "Profilaxia", dia(-7), "Concluído", ""),
        (3, "Manutenção de aparelho", dia(0), "Em andamento", "Controles mensais"),
        (4, "Implante dente 36", dia(-90), "Em andamento", "Aguardando coroa"),
        (6, "Tratamento de canal 46", dia(0), "Planejado", "Duas sessões previstas"),
    ]
    cursor.executemany(
        """
        INSERT INTO tratamentos
            (paciente_id, procedimento, data_inicio, status, observacao)
        VALUES (?, ?, ?, ?, ?)
        """,
        tratamentos,
    )

    orcamentos = [
        (1, "Estética", "Clareamento dental a laser", 1200.00),
        (2, "Cirurgia", "Extração do dente 38", 900.00),
        (4, "Implantodontia", "Implante unitário com coroa", 3800.00),
        (9, "Avaliação", "Consulta de avaliação", 150.00),
    ]
    cursor.executemany(
        """
        INSERT INTO orcamentos
            (paciente_id, categoria, descricao, valor)
        VALUES (?, ?, ?, ?)
        """,
        orcamentos,
    )

    contas = [
        (1, 1200.00, 400.00, (hoje + timedelta(days=12)).isoformat(), "Pendente"),
        (2, 900.00, 900.00, (hoje + timedelta(days=5)).isoformat(), "Pendente"),
        (4, 3800.00, 1900.00, (hoje + timedelta(days=25)).isoformat(), "Pendente"),
    ]
    cursor.executemany(
        """
        INSERT INTO contas_orcamento
            (paciente_id, valor_total, saldo, vencimento, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        contas,
    )

    itens = [
        (1, 1, "Estética", "Clareamento dental a laser", 1200.00),
        (2, 2, "Cirurgia", "Extração do dente 38", 900.00),
        (3, 3, "Implantodontia", "Implante unitário com coroa", 3800.00),
    ]
    cursor.executemany(
        """
        INSERT INTO itens_conta_orcamento
            (conta_orcamento_id, orcamento_id, categoria, descricao, valor)
        VALUES (?, ?, ?, ?, ?)
        """,
        itens,
    )

    receber = [
        (1, "Clareamento - parcela 1/3", 400.00, (hoje + timedelta(days=12)).isoformat(), "Pendente"),
        (2, "Extração dente 38", 900.00, (hoje + timedelta(days=5)).isoformat(), "Pendente"),
        (4, "Implante - entrada", 1900.00, (hoje + timedelta(days=25)).isoformat(), "Pendente"),
        (3, "Manutenção de aparelho", 250.00, (hoje - timedelta(days=3)).isoformat(), "Pago"),
        (6, "Canal - sessão 1", 600.00, (hoje + timedelta(days=9)).isoformat(), "Pendente"),
    ]
    cursor.executemany(
        """
        INSERT INTO contas_receber
            (paciente_id, descricao, valor, vencimento, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        receber,
    )

    pagar = [
        ("Aluguel do consultório", "Imobiliária Central", 2800.00,
         (hoje + timedelta(days=6)).isoformat(), "Pendente"),
        ("Materiais de consumo", "Dental Supply", 740.50,
         (hoje + timedelta(days=3)).isoformat(), "Pendente"),
        ("Laboratório de prótese", "Prótese Silva", 1150.00,
         (hoje + timedelta(days=15)).isoformat(), "Pendente"),
        ("Energia elétrica", "Concessionária", 320.00,
         (hoje - timedelta(days=4)).isoformat(), "Pago"),
    ]
    cursor.executemany(
        """
        INSERT INTO contas_pagar
            (descricao, fornecedor, valor, vencimento, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        pagar,
    )

    movimentacoes = [
        ("Recebimento - Maria Souza", "Entrada", 400.00, dia(0)),
        ("Material odontológico", "Saída", 320.50, dia(1)),
        ("Recebimento - Ana Beatriz", "Entrada", 250.00, dia(2)),
        ("Aluguel do consultório", "Saída", 2800.00, dia(3)),
        ("Recebimento - Carlos Eduardo", "Entrada", 1900.00, dia(3)),
    ]
    cursor.executemany(
        """
        INSERT INTO movimentacoes
            (descricao, tipo, valor, data)
        VALUES (?, ?, ?, ?)
        """,
        movimentacoes,
    )

    cursor.execute(
        "INSERT OR IGNORE INTO migracoes_sistema (chave) VALUES (?)",
        ("contas_orcamento_v2",),
    )

    conexao.commit()


def main():
    if DEMO_DB.resolve() == REAL_DB.resolve():
        raise SystemExit("Destino inválido: o script não pode usar o banco real.")

    if DEMO_DB.exists():
        raise SystemExit(
            f"O arquivo {DEMO_DB} já existe.\n"
            "Remova a pasta demo/ manualmente se quiser recriar."
        )

    DEMO_DIR.mkdir(parents=True, exist_ok=True)
    criar_estrutura()

    conexao = sqlite3.connect(DEMO_DB)
    conexao.execute("PRAGMA foreign_keys = ON")
    try:
        inserir_dados(conexao)
        total_pacientes = conexao.execute(
            "SELECT COUNT(*) FROM pacientes"
        ).fetchone()[0]
        total_eventos = conexao.execute(
            "SELECT COUNT(*) FROM agenda_eventos"
        ).fetchone()[0]
    finally:
        conexao.close()

    print(f"Banco de demonstração criado em: {DEMO_DB}")
    print(f"Pacientes: {total_pacientes} | Eventos de agenda: {total_eventos}")
    print("Para visualizar: python scripts/run_demo.py")


if __name__ == "__main__":
    main()
