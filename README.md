# Comparação entre ETL e ELT com dados do DATASUS

Este repositório possui códigos utilizados no experimento de comparação entre as abordagens ETL (Extract, Transform, Load) e ELT (Extract, Load, Transform), utilizando dados públicos de internações hospitalares do DATASUS.

O experimento utilizou 9.829 registros do SIH/SUS referentes ao estado de Sergipe, em janeiro de 2024, com sete atributos selecionados.

## Tecnologias utilizadas

- Python 3.12
- PostgreSQL 17
- Pandas
- SQLAlchemy
- psutil
- Visual Studio Code

## Organização do experimento

Foram implementados dois fluxos de processamento:

**ETL:** os dados são extraídos do arquivo DBF, transformados utilizando Python e Pandas e posteriormente carregados no PostgreSQL.

**ELT:** os dados são extraídos do arquivo DBF e carregados no PostgreSQL antes das transformações, que são realizadas por meio de comandos SQL.

## Base de dados

A pesquisa utiliza o arquivo `RDSE2401.dbf`, referente às internações hospitalares registradas em Sergipe, em janeiro de 2024.

Os atributos selecionados foram:

- DT_INTER
- DT_SAIDA
- IDADE
- DIAS_PERM
- VAL_TOT
- MORTE
- DIAG_PRINC

## Preparação do ambiente

É necessário ter Python 3.12 e PostgreSQL 17 instalados.

Crie um ambiente virtual Python:

```bash
python -m venv .venv
```

No Windows, ative o ambiente:

```powershell
.venv\Scripts\activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Crie os bancos de dados `datasusETL` e `datasusELT` no PostgreSQL e configure os dados de conexão utilizados pelos scripts.

## Execução

1. Configure a conexão com o PostgreSQL.
2. Verifique se o arquivo `RDSE2401.dbf` está no caminho esperado pelos scripts.
3. Execute o fluxo ETL.
4. Execute o fluxo ELT.
5. Consulte as tabelas geradas nos respectivos bancos de dados para verificar os resultados.

**Observação:** os comandos específicos de execução devem ser preenchidos com os nomes reais dos scripts Python do projeto.

## Avaliação

O experimento considera o tempo de execução, indicadores de memória e a equivalência dos dados produzidos. Também foi realizado um teste funcional com a inclusão do campo `HOUVE_OBITO` nos dois fluxos.
