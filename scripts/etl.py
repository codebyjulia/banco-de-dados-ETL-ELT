from pathlib import Path
from dbfread import DBF
import pandas as pd

arquivo = Path("RDSE2401.dbf")

colunas = [
    "DT_INTER",
    "DT_SAIDA",
    "IDADE",
    "DIAS_PERM",
    "VAL_TOT",
    "MORTE",
    "DIAG_PRINC"
]

print("Iniciando extração dos dados...")

tabela = DBF(
    str(arquivo),
    encoding="latin1",
    char_decode_errors="replace"
)

dados = pd.DataFrame(
    [
        {coluna: registro[coluna] for coluna in colunas}
        for registro in tabela
    ]
)

print("\nExtração concluída!")
print("Quantidade de registros:", len(dados))
print("Quantidade de colunas:", len(dados.columns))

print("\nPrimeiros 5 registros:")
print(dados.head())

print("\nIniciando transformação dos dados...")

dados["DT_INTER"] = pd.to_datetime(
    dados["DT_INTER"],
    format="%Y%m%d",
    errors="coerce"
)

dados["DT_SAIDA"] = pd.to_datetime(
    dados["DT_SAIDA"],
    format="%Y%m%d",
    errors="coerce"
)

for coluna in ["IDADE", "DIAS_PERM", "MORTE"]:
    dados[coluna] = pd.to_numeric(
        dados[coluna],
        errors="coerce"
    ).astype("Int64")

dados["VAL_TOT"] = pd.to_numeric(
    dados["VAL_TOT"],
    errors="coerce"
).round(2)

dados["DIAG_PRINC"] = (
    dados["DIAG_PRINC"]
    .astype("string")
    .str.strip()
    .replace("", pd.NA)
)

print("Transformação concluída!")

print("\nTipos de dados após transformação:")
print(dados.dtypes)

print("\nValores ausentes por coluna:")
print(dados.isna().sum())

print("\nQuantidade final de registros:", len(dados))


from sqlalchemy import create_engine, text
from getpass import getpass

print("\nIniciando carga no PostgreSQL...")

senha = getpass("Digite a senha do PostgreSQL: ")

engine = create_engine(
    "postgresql+psycopg2://",
    connect_args={
        "host": "localhost",
        "port": 5432,
        "user": "postgres",
        "password": senha,
        "dbname": "datasusETL"
    }
)

try:
   
    dados.to_sql(
        name="internacoes",
        con=engine,
        schema="public",
        if_exists="replace",
        index=False,
        chunksize=1000
    )

    print("Carga concluída!")

   
    with engine.connect() as conexao:
        total = conexao.execute(
            text("SELECT COUNT(*) FROM public.internacoes")
        ).scalar()

    print("Registros no PostgreSQL:", total)

except Exception as erro:
    print("Erro durante a carga:", erro)
    raise

finally:
    engine.dispose()