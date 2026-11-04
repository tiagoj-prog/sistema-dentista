from sistema_dentista import create_app
from sistema_dentista.config import HOST, PORT, DEBUG

app = create_app()

if __name__ == "__main__":
    app.run(
        host=HOST,
        port=PORT,
        debug=DEBUG,
    )