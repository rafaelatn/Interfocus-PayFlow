from fastapi import APIRouter

from app.config import settings
from app.schemas import (
    BuscaSimilarRequest,
    TesteMachineLearningRequest,
    TreinoEmbeddingsRequest,
)
from app.services.embeddings import gerar_embedding, montar_texto_inadimplencia
from app.supabase_rest import rpc, select_rows, update_by_id


router = APIRouter(prefix="/ia", tags=["IA"])


@router.post("/buscar-similares")
def buscar_clientes_similares(payload: BuscaSimilarRequest):
    # Esta rota transforma a consulta em embedding e chama uma funcao SQL no
    # Supabase. A funcao compara o vetor da consulta com os vetores salvos.
    embedding = gerar_embedding(payload.consulta)
    resultados = rpc(
        settings.supabase_match_function,
        {
            "query_embedding": embedding,
            "match_count": payload.limite,
        },
    )

    return {
        "consulta": payload.consulta,
        "resultados": resultados,
    }


@router.post("/treinar-embeddings")
def treinar_embeddings(payload: TreinoEmbeddingsRequest):
    # "Treinar", neste projeto, significa gerar embeddings para os registros
    # atuais. O modelo open source ja vem treinado; nos ensinamos o sistema
    # convertendo cada cliente da tabela em um vetor pesquisavel.
    rows = select_rows(
        settings.supabase_table_inadimplencias,
        "id,nome_cliente,dias_inadimplencia,tipo_risco,"
        "valor_inadimplencia,bairro",
        limit=payload.limite,
        filters={"embedding": "is.null"},
    )

    processados = []
    for row in rows:
        texto = montar_texto_inadimplencia(row)
        embedding = gerar_embedding(texto)
        update_by_id(
            settings.supabase_table_inadimplencias,
            row["id"],
            {"embedding": embedding},
        )
        processados.append({"id": row["id"], "texto_usado_no_treino": texto})

    return {
        "message": "Embeddings recalculados para os registros encontrados.",
        "processados": len(processados),
        "amostras": processados[:5],
    }


@router.post("/testar-machine-learning")
def testar_machine_learning(payload: TesteMachineLearningRequest):
    # Executa consultas de exemplo contra a funcao match_inadimplencias.
    # Se vierem resultados com similaridade, o ciclo embedding + pgvector esta ok.
    testes = []

    for consulta in payload.consultas:
        embedding = gerar_embedding(consulta)
        resultados = rpc(
            settings.supabase_match_function,
            {
                "query_embedding": embedding,
                "match_count": payload.limite_por_consulta,
            },
        )
        testes.append(
            {
                "consulta": consulta,
                "resultados": resultados,
                "ok": bool(resultados),
            }
        )

    return {"testes": testes}
