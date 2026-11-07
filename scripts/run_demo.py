"""Executa a aplicação apontando para o banco de demonstração.

Uso local:
    python scripts/run_demo.py

Sobe em http://127.0.0.1:5001 por padrão. Em produção (Render, etc.)
usa a variável de ambiente PORT e escuta em 0.0.0.0.
"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DEMO_DB = ROOT / "demo" / "dentista_demo.db"

if not DEMO_DB.exists():
    raise SystemExit(
        "Banco de demonstração não encontrado.\n"
        "Gere primeiro com: python scripts/seed_demo.py"
    )

import sistema_dentista.config as config

config.DATABASE_PATH = DEMO_DB
config.BACKUP_DIR = ROOT / "demo" / "backups"
config.DEBUG = False

porta = int(os.environ.get("PORT", "5001"))
config.PORT = porta

from sistema_dentista import create_app

app = create_app()


if __name__ == "__main__":
    host = "0.0.0.0" if os.environ.get("PORT") else "127.0.0.1"
    app.run(host=host, port=porta, debug=False)
