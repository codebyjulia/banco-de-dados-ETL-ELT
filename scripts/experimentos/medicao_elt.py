
from pathlib import Path
from getpass import getpass
import time
import tracemalloc

import pandas as pd
from dbfread import DBF
from sqlalchemy import create_engine, text

# Mesmo arquivo e mesmas colunas do ETL
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
        "dbname": "datasusELT"
    }
)

tracemalloc.start()

try:
    inicio_total = time.perf_counter()

    # 1. EXTRAÇÃO: leitura sem transformar os dados
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

    # 2. CARGA: armazenar os dados brutos
    inicio = time.perf_counter()

    dados.to_sql(
    "internacoes_brutas_teste",
    motor,
    schema="public",
    if_exists="replace",
    index=False,
    chunksize=1000
)

    tempo_carga = time.perf_counter() - inicio

    # 3. TRANSFORMAÇÃO: executar no PostgreSQL
    inicio = time.perf_counter()

    sql = """
    DROP TABLE IF EXISTS public.internacoes_teste;

    CREATE TABLE public.internacoes_teste AS
    SELECT
        TO_DATE(NULLIF(TRIM("DT_INTER"), ''), 'YYYYMMDD')
            AS "DT_INTER",

        TO_DATE(NULLIF(TRIM("DT_SAIDA"), ''), 'YYYYMMDD')
            AS "DT_SAIDA",

        "IDADE"::BIGINT AS "IDADE",

        "DIAS_PERM"::BIGINT AS "DIAS_PERM",

        ROUND("VAL_TOT"::NUMERIC, 2)
            AS "VAL_TOT",

        "MORTE"::BIGINT AS "MORTE",

        NULLIF(TRIM("DIAG_PRINC"), '')
            AS "DIAG_PRINC"

    FROM public.internacoes_brutas_teste;
    """

    with motor.begin() as conexao:
        conexao.execute(text(sql))

    tempo_transformacao = time.perf_counter() - inicio
    tempo_total = time.perf_counter() - inicio_total

    _, pico_memoria = tracemalloc.get_traced_memory()

    with motor.connect() as conexao:
        total_registros = conexao.execute(
            text("SELECT COUNT(*) FROM public.internacoes_teste")
        ).scalar_one()

    print("\n===== RESULTADOS DA MEDIÇÃO ELT =====")
    print(f"Registros carregados: {total_registros}")
    print(f"Tempo de extração: {tempo_extracao:.4f} segundos")
    print(f"Tempo de carga: {tempo_carga:.4f} segundos")
    print(f"Tempo de transformação: {tempo_transformacao:.4f} segundos")
    print(f"Tempo total: {tempo_total:.4f} segundos")
    print(f"Pico de memória Python: {pico_memoria / (1024 ** 2):.2f} MiB")

finally:
    tracemalloc.stop()
    motor.dispose()
