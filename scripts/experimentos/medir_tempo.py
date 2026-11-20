import time
from pathlib import Path
from dbfread import DBF
import pandas as pd

# Localização do arquivo DBF
PASTA_PROJETO = Path(__file__).resolve().parents[2]
ARQUIVO = PASTA_PROJETO / "RDSE2401.dbf"

COLUNAS = [
    "DT_INTER",
    "DT_SAIDA",
    "IDADE",
    "DIAS_PERM",
    "VAL_TOT",
    "MORTE",
    "DIAG_PRINC"
]

print("Iniciando teste de tempo da extração...")

inicio = time.perf_counter()

tabela = DBF(
    str(ARQUIVO),
    encoding="latin1",
    char_decode_errors="replace"
)

dados = pd.DataFrame([
    {coluna: registro[coluna] for coluna in COLUNAS}
    for registro in tabela
])

fim = time.perf_counter()

tempo_extracao = fim - inicio

print(f"Registros extraídos: {len(dados)}")
print(f"Tempo de extração: {tempo_extracao:.4f} segundos")