"""Executa a aplicação apontando para o banco de demonstração.

Uso:

    python scripts/run_demo.py

Sobe em http://127.0.0.1:5001, sem usar o banco real.
"""

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
config.PORT = 5001
config.DEBUG = False

from sistema_dentista import create_app

app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False)
