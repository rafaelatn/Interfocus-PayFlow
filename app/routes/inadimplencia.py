from fastapi import APIRouter, HTTPException

from app.config import settings
from app.schemas import InadimplenciaCreate
from app.supabase_rest import insert_row, select_rows


router = APIRouter(prefix="/inadimplencia", tags=["Inadimplencia"])


@router.post("")
def criar_inadimplencia(payload: InadimplenciaCreate):
    # Esta rota recebe dados financeiros e grava na tabela inadimplencias.
    # O embedding fica null no inicio. Depois o script ou uma rota de IA preenche.
    dados = payload.model_dump(mode="json", exclude_none=True)
    if "regiao" in dados and "bairro" not in dados:
        dados["bairro"] = dados.pop("regiao")

    data = insert_row(settings.supabase_table_inadimplencias, dados)

    return {
        "message": "Registro criado com sucesso",
        "data": data,
    }


@router.get("")
def listar_inadimplencias(limite: int = 20):
    # Esta rota lista os registros mais recentes para voce verificar se o banco
    # esta recebendo os dados corretamente.
    try:
        data = select_rows(
            settings.supabase_table_inadimplencias,
            "id,nome_cliente,dias_inadimplencia,tipo_risco,"
            "valor_inadimplencia,bairro,tentativas_cobranca",
            limit=limite,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return data
