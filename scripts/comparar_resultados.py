from getpass import getpass
from collections import Counter

import pandas as pd
from sqlalchemy import create_engine, text

senha = getpass("Digite a senha do PostgreSQL: ")


def conectar(banco):
    return create_engine(
        "postgresql+psycopg2://",
        connect_args={
            "host": "localhost",
            "port": 5432,
            "user": "postgres",
            "password": senha,
            "dbname": banco
        }
    )


colunas = [
    "DT_INTER", "DT_SAIDA", "IDADE",
    "DIAS_PERM", "VAL_TOT", "MORTE", "DIAG_PRINC"
]

consulta = """
SELECT
    "DT_INTER", "DT_SAIDA", "IDADE",
    "DIAS_PERM", "VAL_TOT", "MORTE", "DIAG_PRINC"
FROM public.internacoes_teste
"""

engine_etl = conectar("datasusETL")
engine_elt = conectar("datasusELT")

try:
    with engine_etl.connect() as conexao:
        etl = pd.read_sql_query(text(consulta), conexao)

    with engine_elt.connect() as conexao:
        elt = pd.read_sql_query(text(consulta), conexao)

    print("Registros ETL:", len(etl))
    print("Registros ELT:", len(elt))

    def preparar(df):
        df = df[colunas].copy()

        for coluna in ["DT_INTER", "DT_SAIDA"]:
            df[coluna] = pd.to_datetime(
                df[coluna], errors="coerce"
            ).dt.strftime("%Y-%m-%d")

        for coluna in ["IDADE", "DIAS_PERM", "MORTE"]:
            df[coluna] = pd.to_numeric(
                df[coluna], errors="coerce"
            )

    
        df["VAL_TOT"] = pd.to_numeric(
            df["VAL_TOT"], errors="coerce"
        ).round(2)

        df = df.astype(object).where(pd.notna(df), None)

        return Counter(
            tuple(linha)
            for linha in df.itertuples(index=False, name=None)
        )

    iguais = preparar(etl) == preparar(elt)

    print("\nRESULTADO DA COMPARAÇÃO")

    if iguais:
        print("SUCESSO! os registros ETL e ELT são equivalentes!")
    else:
        print("ATENÇÃO! foram encontradas diferenças entre ETL e ELT.")

finally:
    engine_etl.dispose()
    engine_elt.dispose()