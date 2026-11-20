from sqlalchemy import create_engine, text
from getpass import getpass

usuario = "postgres"
senha = getpass("Digite a senha do PostgreSQL: ")
banco = input("Nome do banco ETL: ").strip()

engine = create_engine(
    "postgresql+psycopg2://",
    connect_args={
        "host": "localhost",
        "port": 5432,
        "user": usuario,
        "password": senha,
        "dbname": banco
    }
)

try:
    with engine.connect() as conexao:
        resultado = conexao.execute(
            text("SELECT current_database(), version()")
        ).fetchone()

        print("\nConexão realizada com sucesso!")
        print("Banco:", resultado[0])
        print("PostgreSQL:", resultado[1].split(",")[0])

except Exception as erro:
    print("\nErro ao conectar:", erro)

finally:
    engine.dispose()