from fastapi import APIRouter
order_router = APIRouter()

@order_router.get("/pedido-teste")
def testar_pedido():
    return {"mensagem": "Rota de pedidos funcionando!"}
