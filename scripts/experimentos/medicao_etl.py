
from pathlib import Path
from getpass import getpass
import time
import tracemalloc

import pandas as pd
from dbfread import DBF
from sqlalchemy import create_engine, text

# Localizar o arquivo DBF a partir da pasta do projeto
arquivo = Path(__file__).resolve().parents[1] / "RDSE2401.dbf"

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

senha = getpass("Digite a senha do PostgreSQL: ")

motor = create_engine(
    "postgresql+psycopg2://",
    connect_args={
        "host": "localhost",
        "port": 5432,
        "user": "postgres",
        "password": senha,
        "dbname": "datasusETL"
    }
)

tracemalloc.start()
inicio_total = time.perf_counter()

try:
    # ETAPA 1: EXTRAÇÃO
    inicio = time.perf_counter()

    tabela = DBF(
        str(arquivo),
        encoding="latin1",
        char_decode_errors="replace"
    )

    dados = pd.DataFrame([
        {coluna: registro[coluna] for coluna in colunas}
        for registro in tabela
    ])

    tempo_extracao = time.perf_counter() - inicio

    # ETAPA 2: TRANSFORMAÇÃO EM PYTHON
    inicio = time.perf_counter()

    for coluna in ["DT_INTER", "DT_SAIDA"]:
        dados[coluna] = pd.to_datetime(
            dados[coluna],
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

    tempo_transformacao = time.perf_counter() - inicio

    # ETAPA 3: CARGA NO POSTGRESQL
    inicio = time.perf_counter()

    dados.to_sql(
        name="internacoes_teste",
        con=motor,
        schema="public",
        if_exists="replace",
        index=False,
        chunksize=1000
    )

    tempo_carga = time.perf_counter() - inicio

    tempo_total = time.perf_counter() - inicio_total
    _, pico_memoria = tracemalloc.get_traced_memory()

    with motor.connect() as conexao:
        quantidade = conexao.execute(
            text("SELECT COUNT(*) FROM public.internacoes_teste")
        ).scalar()

    print("\n===== RESULTADOS DA MEDIÇÃO ETL =====")
    print(f"Registros carregados: {quantidade}")
    print(f"Tempo de extração: {tempo_extracao:.4f} segundos")
    print(f"Tempo de transformação: {tempo_transformacao:.4f} segundos")
    print(f"Tempo de carga: {tempo_carga:.4f} segundos")
    print(f"Tempo total: {tempo_total:.4f} segundos")
    print(f"Pico de memória Python: {pico_memoria / 1024**2:.2f} MiB")

finally:
    tracemalloc.stop()
    motor.dispose()
