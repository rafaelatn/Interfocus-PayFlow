from functools import lru_cache

from fastapi import HTTPException


CLASSES_RISCO = ["baixo", "medio", "alto"]


@lru_cache
def treinar_modelo_exemplo():
    # Este modelo e pequeno de proposito.
    # Ele funciona como uma planilha de exemplos para o scikit-learn aprender.
    try:
        from sklearn.ensemble import RandomForestClassifier
    except ImportError as exc:
        raise HTTPException(
            status_code=500,
            detail="Instale as dependencias com: pip install -r requirements.txt",
        ) from exc

    exemplos = [
        [0, 50],
        [5, 120],
        [10, 300],
        [15, 450],
        [25, 800],
        [35, 1200],
        [50, 1800],
        [70, 3000],
        [90, 5000],
        [120, 9000],
    ]
    respostas = [
        "baixo",
        "baixo",
        "baixo",
        "medio",
        "medio",
        "medio",
        "alto",
        "alto",
        "alto",
        "alto",
    ]

    modelo = RandomForestClassifier(n_estimators=50, random_state=42)
    modelo.fit(exemplos, respostas)
    return modelo


def prever_risco(dias_inadimplencia: int, valor_inadimplencia: float) -> dict:
    modelo = treinar_modelo_exemplo()
    entrada = [[dias_inadimplencia, valor_inadimplencia]]
    risco_previsto = modelo.predict(entrada)[0]
    probabilidades_modelo = modelo.predict_proba(entrada)[0]

    probabilidades = {
        classe: round(float(probabilidade), 3)
        for classe, probabilidade in zip(modelo.classes_, probabilidades_modelo)
    }

    return {
        "risco_previsto": risco_previsto,
        "probabilidades": probabilidades,
        "explicacao": (
            "O modelo comparou dias de atraso e valor em aberto com exemplos "
            "simples de treino. E como olhar casos antigos parecidos antes de "
            "dar um palpite."
        ),
    }
