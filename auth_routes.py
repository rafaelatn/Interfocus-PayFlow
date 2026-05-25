from fastapi import APIRouter

auth_router = APIRouter()

@auth_router.get("/login-teste")
def testar_login():
    return {"mensagem": "Rota de autenticação funcionando!"}

