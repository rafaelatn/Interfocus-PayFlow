from fastapi import APIRouter, HTTPException

from app.config import settings
from app.schemas import HistoricoCobrancaCreate, InadimplenciaCreate
from app.supabase_rest import insert_row, select_rows


router = APIRouter(prefix="/inadimplencia", tags=["Inadimplencia"])
HISTORICO_COBRANCAS_TABLE = "historico_cobrancas"


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


@router.get("/historico")
def listar_historico_cobrancas(
    limite: int = 50,
    inadimplencia_id: int | None = None,
):
    filters = {}
    if inadimplencia_id is not None:
        filters["inadimplencia_id"] = f"eq.{inadimplencia_id}"

    try:
        return select_rows(
            HISTORICO_COBRANCAS_TABLE,
            "id,inadimplencia_id,canal,mensagem,status,observacao,created_at",
            limit=limite,
            filters=filters,
            order="created_at.desc",
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/historico")
def criar_historico_cobranca(payload: HistoricoCobrancaCreate):
    try:
        data = insert_row(
            HISTORICO_COBRANCAS_TABLE,
            payload.model_dump(mode="json", exclude_none=True),
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return {
        "message": "Historico registrado com sucesso",
        "data": data,
    }
