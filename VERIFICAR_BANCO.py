from sistema_dentista.database.connection import criar_banco, conectar, DB_NAME


def main():
    criar_banco()

    conexao = conectar()
    try:
        colunas = conexao.execute(
            "PRAGMA table_info(pacientes)"
        ).fetchall()

        nomes = [coluna[1] for coluna in colunas]

        print("Banco usado:")
        print(DB_NAME)
        print()
        print("Colunas da tabela pacientes:")
        for nome in nomes:
            print("-", nome)

        faltando = [
            nome for nome in (
                "cpf",
                "rg",
                "data_nascimento"
            )
            if nome not in nomes
        ]

        print()
        if faltando:
            print(
                "Ainda faltam:",
                ", ".join(faltando)
            )
        else:
            print(
                "OK: CPF, RG e data_nascimento existem."
            )
    finally:
        conexao.close()


if __name__ == "__main__":
    main()
