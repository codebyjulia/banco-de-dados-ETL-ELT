from dbfread import DBF

print("Lendo os dados de Sergipe...")

tabela = DBF(
    "RDSE2401.dbf",
    encoding="latin1",
    char_decode_errors="replace"
)

print("\nQuantidade de registros:", len(tabela))

print("\nColunas disponíveis:")
for coluna in tabela.field_names:
    print(coluna)

print("\nPrimeiros 3 registros:")
for i, registro in enumerate(tabela):
    print(dict(registro))
    if i == 2:
        break