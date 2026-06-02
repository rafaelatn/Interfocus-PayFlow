from pathlib import Path
import random
import sys

from faker import Faker
import numpy as np
import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.data.marilia_bairros import BAIRROS_MARILIA

fake = Faker("pt_BR")
random.seed(42)
np.random.seed(42)

TOTAL_LINHAS_GERADAS = 1200
TOTAL_LINHAS_CSV = 1000

PASTA_SAIDA = Path("csv_supabase")
ARQUIVO_SAIDA = PASTA_SAIDA / "inadimplencia_sintetica.csv"


def classificar_risco(dias: int) -> str:
    if dias <= 30:
        probs = {"Baixo": 0.75, "Medio": 0.20, "Alto": 0.04, "Critico": 0.01}
    elif dias <= 90:
        probs = {"Baixo": 0.15, "Medio": 0.55, "Alto": 0.25, "Critico": 0.05}
    elif dias <= 180:
        probs = {"Baixo": 0.05, "Medio": 0.25, "Alto": 0.50, "Critico": 0.20}
    elif dias <= 365:
        probs = {"Baixo": 0.02, "Medio": 0.10, "Alto": 0.45, "Critico": 0.43}
    else:
        probs = {"Baixo": 0.01, "Medio": 0.05, "Alto": 0.25, "Critico": 0.69}

    return np.random.choice(list(probs.keys()), p=list(probs.values()))


def taxa_juros(risco: str) -> float:
    return {
        "Baixo": 0.02,
        "Medio": 0.035,
        "Alto": 0.055,
        "Critico": 0.08,
    }[risco]


def mensalidade_base(risco: str) -> float:
    faixas = {
        "Baixo": (200, 800),
        "Medio": (400, 1500),
        "Alto": (800, 3000),
        "Critico": (1500, 8000),
    }
    minimo, maximo = faixas[risco]
    base = np.random.uniform(minimo, maximo)
    ruido = np.random.lognormal(mean=0, sigma=0.2)
    return base * ruido


def calcular_valor(dias: int, risco: str) -> float:
    meses = dias / 30
    return round(mensalidade_base(risco) * ((1 + taxa_juros(risco)) ** meses), 2)


def gerar_dataframe() -> pd.DataFrame:
    nomes = [fake.name() for _ in range(TOTAL_LINHAS_GERADAS)]
    bairros = [bairro["nome"] for bairro in BAIRROS_MARILIA]
    regioes = np.random.choice(
        bairros,
        size=TOTAL_LINHAS_GERADAS,
    )

    dias_raw = np.random.exponential(scale=120, size=TOTAL_LINHAS_GERADAS)
    dias = np.clip(dias_raw, 1, 730).astype(int)
    riscos = [classificar_risco(int(dia)) for dia in dias]
    valores = [calcular_valor(int(dia), risco) for dia, risco in zip(dias, riscos)]

    df = pd.DataFrame(
        {
            "nome_cliente": nomes,
            "valor_inadimplencia": valores,
            "dias_inadimplencia": dias,
            "tipo_risco": riscos,
            "bairro": regioes,
        }
    )

    return df.sample(TOTAL_LINHAS_CSV, random_state=42).reset_index(drop=True)


def main() -> None:
    PASTA_SAIDA.mkdir(parents=True, exist_ok=True)
    df = gerar_dataframe()
    df.to_csv(ARQUIVO_SAIDA, index=False, encoding="utf-8-sig")
    print(f"CSV criado em: {ARQUIVO_SAIDA.resolve()}")
    print(f"Total de linhas: {len(df)}")


if __name__ == "__main__":
    main()
