from fastapi import APIRouter


router = APIRouter(prefix="/frontend", tags=["Frontend"])


@router.get("/config")
def configuracao_frontend():
    # O frontend pode chamar esta rota para descobrir endpoints importantes.
    # Assim o aluno enxerga onde cada parte se encaixa.
    return {
        "api": {
            "health": "/health",
            "listar_inadimplencia": "/inadimplencia",
            "criar_inadimplencia": "/inadimplencia",
            "buscar_com_ia": "/ia/buscar-similares",
            "prever_risco": "/ml/prever-risco",
            "botpress_webhook": "/botpress/webhook",
        },
        "mensagem": "Use estes caminhos no fetch, axios ou no seu frontend.",
    }
