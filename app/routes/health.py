from fastapi import APIRouter


router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
def health_check():
    # Primeira rota para testar.
    # Se isto responder, o FastAPI esta rodando corretamente.
    return {"status": "ok", "message": "PayFlow API online"}

