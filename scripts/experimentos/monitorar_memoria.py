
import csv
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

import psutil

PASTA = Path(__file__).resolve().parent
RESULTADOS = PASTA / "resultados_memoria"
RESULTADOS.mkdir(exist_ok=True)

INTERVALO = 0.05
MIB = 1024 ** 2


def memoria_privada(processo):
    try:
        info = processo.memory_full_info()

        if hasattr(info, "uss"):
            return info.uss / MIB

        if hasattr(info, "private"):
            return info.private / MIB

        return None

    except (
        psutil.NoSuchProcess,
        psutil.AccessDenied,
        psutil.ZombieProcess
    ):
        return None


def medir_python(processo_principal):
    processos = [processo_principal]

    try:
        processos.extend(
            processo_principal.children(recursive=True)
        )
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

    total = 0.0
    encontrados = 0

    for processo in processos:
        memoria = memoria_privada(processo)

        if memoria is not None:
            total += memoria
            encontrados += 1

    return total if encontrados else None


def medir_postgresql():
    total = 0.0
    encontrados = 0

    for processo in psutil.process_iter(["name"]):
        try:
            nome = (processo.info["name"] or "").lower()

            if nome == "postgres.exe":
                memoria = memoria_privada(processo)

                if memoria is not None:
                    total += memoria
                    encontrados += 1

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess
        ):
            continue

    return total if encontrados else None


def monitorar(pid, arquivo_csv, parar, resultados):
    processo_principal = psutil.Process(pid)
    inicio = time.perf_counter()

    amostras = 0
    inicial_python = None
    inicial_postgres = None
    pico_python = None
    pico_postgres = None

    with open(
        arquivo_csv,
        "w",
        newline="",
        encoding="utf-8"
    ) as arquivo:

        escritor = csv.writer(arquivo)

        escritor.writerow([
            "tempo_segundos",
            "python_memoria_privada_mib",
            "postgres_memoria_privada_mib"
        ])

        while not parar.is_set():
            python_mib = medir_python(processo_principal)
            postgres_mib = medir_postgresql()

            if python_mib is not None:
                if inicial_python is None:
                    inicial_python = python_mib

                pico_python = max(
                    pico_python or 0,
                    python_mib
                )

            if postgres_mib is not None:
                if inicial_postgres is None:
                    inicial_postgres = postgres_mib

                pico_postgres = max(
                    pico_postgres or 0,
                    postgres_mib
                )

            escritor.writerow([
                round(time.perf_counter() - inicio, 4),
                round(python_mib, 4)
                if python_mib is not None else "",
                round(postgres_mib, 4)
                if postgres_mib is not None else ""
            ])

            amostras += 1
            parar.wait(INTERVALO)

    resultados["amostras"] = amostras
    resultados["inicial_python"] = inicial_python
    resultados["inicial_postgres"] = inicial_postgres
    resultados["pico_python"] = pico_python
    resultados["pico_postgres"] = pico_postgres


def formatar(valor):
    if valor is None:
        return "indisponível"

    return f"{valor:.2f} MiB"


def main():
    print("===== MONITORAMENTO DE MEMÓRIA =====")
    print("1 - ETL")
    print("2 - ELT")

    escolha = input("\nEscolha a abordagem: ").strip()

    if escolha == "1":
        abordagem = "ETL"
        script = PASTA / "medicao_etl.py"

    elif escolha == "2":
        abordagem = "ELT"
        script = PASTA / "medicao_elt.py"

    else:
        print("Opção inválida.")
        return

    if not script.exists():
        print(f"Arquivo não encontrado: {script}")
        return

    identificador = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    arquivo_csv = (
        RESULTADOS / f"{abordagem}_{identificador}.csv"
    )

    print(f"\nAbordagem: {abordagem}")
    print("Digite a senha quando for solicitada.\n")

    processo = subprocess.Popen(
        [sys.executable, str(script)],
        cwd=str(PASTA.parent.parent)
    )

    parar = threading.Event()
    resultados = {}

    monitor = threading.Thread(
        target=monitorar,
        args=(
            processo.pid,
            arquivo_csv,
            parar,
            resultados
        ),
        daemon=True
    )

    monitor.start()

    try:
        codigo_saida = processo.wait()

    finally:
        parar.set()
        monitor.join()

    print("\n===== RESULTADOS DO MONITORAMENTO =====")
    print(f"Abordagem: {abordagem}")
    print(f"Código de saída: {codigo_saida}")
    print(f"Amostras: {resultados.get('amostras', 0)}")

    inicial_python = resultados.get("inicial_python")
    inicial_postgres = resultados.get("inicial_postgres")
    pico_python = resultados.get("pico_python")
    pico_postgres = resultados.get("pico_postgres")

    print(
        "Memória privada inicial Python: "
        + formatar(inicial_python)
    )

    print(
        "Pico de memória privada Python: "
        + formatar(pico_python)
    )

    print(
        "Memória privada inicial PostgreSQL: "
        + formatar(inicial_postgres)
    )

    print(
        "Pico de memória privada PostgreSQL: "
        + formatar(pico_postgres)
    )

    print(f"CSV salvo em: {arquivo_csv}")

    if codigo_saida != 0:
        print(
            "\nATENÇÃO: execução com erro. "
            "Não utilize esta medição."
        )


if __name__ == "__main__":
    main()
