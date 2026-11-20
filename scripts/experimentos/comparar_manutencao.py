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

motor_etl = conectar("datasusETL")
motor_elt = conectar("datasusELT")

try:
    consulta = """
        SELECT
            "DT_INTER",
            "DT_SAIDA",
            "IDADE",
            "DIAS_PERM",
            "VAL_TOT",
            "MORTE",
            "DIAG_PRINC",
            "HOUVE_OBITO"
        FROM public.internacoes_manutencao
    """

    with motor_etl.connect() as conexao:
        etl = pd.read_sql(text(consulta), conexao)

    with motor_elt.connect() as conexao:
        elt = pd.read_sql(text(consulta), conexao)

    def normalizar(dados):
        dados = dados.copy()

        for coluna in ["DT_INTER", "DT_SAIDA"]:
            dados[coluna] = pd.to_datetime(
                dados[coluna], errors="coerce"
            ).dt.strftime("%Y-%m-%d")

        for coluna in ["IDADE", "DIAS_PERM", "MORTE", "HOUVE_OBITO"]:
            dados[coluna] = pd.to_numeric(
                dados[coluna], errors="coerce"
            ).astype("Int64")

        dados["VAL_TOT"] = pd.to_numeric(
            dados["VAL_TOT"], errors="coerce"
        ).round(2)

        dados["DIAG_PRINC"] = (
            dados["DIAG_PRINC"]
            .astype("string")
            .str.strip()
        )

        # Padronizar valores ausentes
        dados = dados.astype(object).where(pd.notna(dados), None)

        return Counter(
            tuple(linha)
            for linha in dados.itertuples(index=False, name=None)
        )

    registros_etl = normalizar(etl)
    registros_elt = normalizar(elt)

    print("\n===== COMPARAÇÃO DA MANUTENÇÃO =====")
    print(f"Registros ETL: {len(etl)}")
    print(f"Registros ELT: {len(elt)}")

    if registros_etl == registros_elt:
        print("RESULTADO: OS REGISTROS SÃO EQUIVALENTES!")
        print("A nova coluna HOUVE_OBITO também foi validada.")
    else:
        print("RESULTADO: FORAM ENCONTRADAS DIFERENÇAS!")
        print(
            "Registros exclusivos do ETL:",
            sum((registros_etl - registros_elt).values())
        )
        print(
            "Registros exclusivos do ELT:",
            sum((registros_elt - registros_etl).values())
        )

finally:
    motor_etl.dispose()
    motor_elt.dispose()