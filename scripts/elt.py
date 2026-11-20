from pathlib import Path
from getpass import getpass

import pandas as pd
from dbfread import DBF
from sqlalchemy import create_engine, text

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

if not arquivo.exists():
    raise FileNotFoundError(f"Arquivo não encontrado: {arquivo}")

print("Iniciando extração para o ELT...")

tabela = DBF(
    str(arquivo),
    encoding="latin1",
    char_decode_errors="replace"
)

dados_brutos = pd.DataFrame(
    [
        {coluna: registro[coluna] for coluna in colunas}
        for registro in tabela
    ]
)

print("Registros extraídos:", len(dados_brutos))

for coluna in ["DT_INTER", "DT_SAIDA", "DIAG_PRINC"]:
    dados_brutos[coluna] = dados_brutos[coluna].astype(object)

print("\nIniciando carga dos dados brutos...")

senha = getpass("Digite a senha do PostgreSQL: ")

engine = create_engine(
    "postgresql+psycopg2://",
    connect_args={
        "host": "localhost",
        "port": 5432,
        "user": "postgres",
        "password": senha,
        "dbname": "datasusELT"
    }
)

try:
    dados_brutos.to_sql(
        name="internacoes_brutas",
        con=engine,
        schema="public",
        if_exists="replace",
        index=False,
        chunksize=1000
    )

    with engine.connect() as conexao:
        total = conexao.execute(
            text("SELECT COUNT(*) FROM public.internacoes_brutas")
        ).scalar()

    print("Carga bruta concluída!")
    print("Registros no PostgreSQL:", total)

finally:
    engine.dispose()