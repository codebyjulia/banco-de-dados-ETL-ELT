from pathlib import Path
from pyreaddbc.readdbc import dbc2dbf

arquivo = Path("RDSE2401.dbc")
arquivo_dbf = Path("RDSE2401.dbf")

if not arquivo.exists():
    print("ERRO: Arquivo RDSE2401.dbc não encontrado!")
    raise SystemExit(1)

print("Arquivo encontrado!")
print("Iniciando conversão do DBC...")

dbc2dbf(str(arquivo), str(arquivo_dbf))

print("Conversão concluída!")
print("Arquivo gerado:", arquivo_dbf)
print("Tamanho:", arquivo_dbf.stat().st_size, "bytes")