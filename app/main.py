from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.config import settings
from app.routes.botpress import router as botpress_router
from app.routes.health import router as health_router
from app.routes.ia import router as ia_router
from app.routes.inadimplencia import router as inadimplencia_router


# Este arquivo e a porta de entrada do backend.
# Quando voce roda `uvicorn app.main:app --reload`, o FastAPI procura esta
# variavel `app` para iniciar o servidor.
app = FastAPI(
    title=settings.app_name,
    description="Backend do Interfocus PayFlow com FastAPI, Supabase e IA.",
    version="0.1.0",
)

STATIC_DIR = Path(__file__).resolve().parent / "static"


@app.get("/", include_in_schema=False)
def root():
    # Entrega o frontend junto do backend, mantendo /docs para o Swagger.
    return FileResponse(STATIC_DIR / "index.html")


# Cada include_router registra um grupo de rotas.
# Assim o backend cresce organizado, sem colocar tudo dentro do main.py.
app.include_router(health_router)
app.include_router(inadimplencia_router)
app.include_router(ia_router)
app.include_router(botpress_router)
