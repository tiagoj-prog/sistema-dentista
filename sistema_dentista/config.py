"""Configuração centralizada da aplicação Sistema Dentista.

Esta etapa mantém a simplicidade de um sistema local. A chave secreta da
sessão Flask é persistida localmente, para não mudar a cada inicialização.
"""

from pathlib import Path
import os
import secrets

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATABASE_PATH = PROJECT_ROOT / "dentista.db"
BACKUP_DIR = PROJECT_ROOT / "backups"
TEMPLATES_DIR = PROJECT_ROOT / "sistema_dentista" / "templates"
STATIC_DIR = PROJECT_ROOT / "sistema_dentista" / "static"

# O Flask usa esta chave somente para assinar cookies de sessão.
# O arquivo é local, não deve ser versionado e pode ser recriado.
SECRET_KEY_FILE = PROJECT_ROOT / ".secret_key"

if os.environ.get("SECRET_KEY"):
    SECRET_KEY = os.environ.get("SECRET_KEY")
elif SECRET_KEY_FILE.exists():
    SECRET_KEY = SECRET_KEY_FILE.read_text(encoding="utf-8").strip()
else:
    SECRET_KEY = secrets.token_hex(32)
    SECRET_KEY_FILE.write_text(SECRET_KEY, encoding="utf-8")

# Configurações do servidor local.
# Usar 127.0.0.1 evita exposição à rede local. Em desenvolvimento, a chave
# FLASK_DEBUG pode ser ativada explicitamente sem alterar o código.
HOST = "127.0.0.1"
PORT = 5000
DEBUG = os.environ.get("FLASK_DEBUG", "").lower() in ("1", "true", "yes")