from sistema_dentista.config import HOST, PORT, DEBUG

from app import app


def main():
    app.run(
        host=HOST,
        port=PORT,
        debug=DEBUG,
    )


if __name__ == "__main__":
    main()