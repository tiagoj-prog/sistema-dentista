from sistema_dentista.config import HOST, PORT, DEBUG

from app import app

if __name__ == "__main__":
    app.run(
        host=HOST,
        port=PORT,
        debug=DEBUG,
    )