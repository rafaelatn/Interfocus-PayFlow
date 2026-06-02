from fastapi import APIRouter, HTTPException

from app.config import settings
from app.schemas import BotpressBuscaRequest, BotpressClienteRequest
from app.services.embeddings import gerar_embedding, montar_texto_inadimplencia
from app.supabase_rest import insert_row, rpc, update_by_id


router = APIRouter(prefix="/botpress", tags=["Botpress"])


def dinheiro_br(valor) -> str:
    numero = float(valor or 0)
    return f"R$ {numero:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


@router.post("/clientes")
def cadastrar_cliente_botpress(payload: BotpressClienteRequest):
    dados = payload.model_dump(mode="json")

    try:
        inseridos = insert_row(settings.supabase_table_inadimplencias, dados)
        cliente = inseridos[0] if inseridos else dados

        row_para_embedding = {
            **dados,
            "id": cliente.get("id"),
        }
        embedding = gerar_embedding(montar_texto_inadimplencia(row_para_embedding))

        if cliente.get("id") is not None:
            update_by_id(
                settings.supabase_table_inadimplencias,
                cliente["id"],
                {"embedding": embedding},
            )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    mensagem = (
        f"Cliente {payload.nome_cliente} cadastrado no PayFlow. "
        f"Bairro: {payload.bairro}. "
        f"Risco: {payload.tipo_risco}. "
        f"Valor: {dinheiro_br(payload.valor_inadimplencia)}. "
        f"Atraso: {payload.dias_inadimplencia} dias."
    )

    return {
        "ok": True,
        "mensagem": mensagem,
        "cliente": cliente,
    }


@router.post("/buscar-clientes")
def buscar_clientes_botpress(payload: BotpressBuscaRequest):
    try:
        embedding = gerar_embedding(payload.consulta)
        resultados = rpc(
            settings.supabase_match_function,
            {
                "query_embedding": embedding,
                "match_count": payload.limite,
            },
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    if not resultados:
        return {
            "ok": True,
            "mensagem": "Nao encontrei clientes parecidos com essa busca.",
            "resultados": [],
        }

    linhas = []
    for idx, cliente in enumerate(resultados, start=1):
        similaridade = round(float(cliente.get("similaridade") or 0) * 100)
        linhas.append(
            f"{idx}. {cliente.get('nome_cliente')} | "
            f"{cliente.get('bairro')} | "
            f"risco {cliente.get('tipo_risco')} | "
            f"{cliente.get('dias_inadimplencia')} dias | "
            f"{dinheiro_br(cliente.get('valor_inadimplencia'))} | "
            f"{similaridade}% similar"
        )

    return {
        "ok": True,
        "mensagem": "\n".join(linhas),
        "resultados": resultados,
    }
