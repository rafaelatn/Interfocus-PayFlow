from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class InadimplenciaCreate(BaseModel):
    # Modelo usado quando voce cria um novo registro pela API.
    # O FastAPI usa este schema para validar se os dados chegaram no formato certo.
    nome_cliente: str = Field(..., examples=["Maria Oliveira"])
    dias_inadimplencia: int = Field(..., ge=0, examples=[45])
    tipo_risco: str = Field(..., examples=["medio"])
    valor_inadimplencia: Decimal = Field(..., ge=0, examples=[1250.50])
    bairro: Optional[str] = Field(default=None, examples=["Palmital"])
    regiao: Optional[str] = Field(default=None, examples=["Palmital"])


class InadimplenciaResponse(InadimplenciaCreate):
    # Modelo usado para responder ao usuario depois que o dado existe no banco.
    id: str


class BuscaSimilarRequest(BaseModel):
    # Texto livre usado para buscar clientes parecidos semanticamente.
    consulta: str = Field(
        ...,
        examples=[
            "clientes com alto valor em atraso e risco critico no bairro Palmital"
        ],
    )
    limite: int = Field(default=5, ge=1, le=20)


class TreinoEmbeddingsRequest(BaseModel):
    # Quantos registros com embedding null o backend deve processar por chamada.
    limite: int = Field(default=20, ge=1, le=200)


class TesteMachineLearningRequest(BaseModel):
    consultas: list[str] = Field(
        default=[
            "clientes de alto risco em bairros de Marilia",
            "clientes com muitos dias de atraso no Palmital",
            "dividas altas perto do Centro",
        ],
        min_length=1,
        max_length=5,
    )
    limite_por_consulta: int = Field(default=3, ge=1, le=10)


class BuscaSimilarResponse(BaseModel):
    id: str
    nome_cliente: str
    dias_inadimplencia: int
    tipo_risco: str
    valor_inadimplencia: Decimal
    bairro: str
    similaridade: float


class BotpressClienteRequest(BaseModel):
    nome_cliente: str = Field(..., examples=["Maria Oliveira"])
    valor_inadimplencia: Decimal = Field(..., ge=0, examples=[1250.50])
    dias_inadimplencia: int = Field(..., ge=0, examples=[45])
    tipo_risco: str = Field(default="Médio", examples=["Alto"])
    bairro: str = Field(..., examples=["Palmital"])
    tentativas_cobranca: int = Field(default=0, ge=0)


class BotpressBuscaRequest(BaseModel):
    consulta: str = Field(..., examples=["clientes de alto risco no Palmital"])
    limite: int = Field(default=5, ge=1, le=10)
