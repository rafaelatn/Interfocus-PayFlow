from fastapi import APIRouter

from app.schemas import PrevisaoRiscoRequest, PrevisaoRiscoResponse
from app.services.ml_model import prever_risco


router = APIRouter(prefix="/ml", tags=["Machine Learning"])


@router.post("/prever-risco", response_model=PrevisaoRiscoResponse)
def prever_risco_inadimplencia(payload: PrevisaoRiscoRequest):
    # Esta rota usa scikit-learn para dar uma previsao simples.
    # Ela nao substitui analise financeira real; e um exemplo didatico.
    return prever_risco(
        dias_inadimplencia=payload.dias_inadimplencia,
        valor_inadimplencia=payload.valor_inadimplencia,
    )
