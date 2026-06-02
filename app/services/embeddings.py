from functools import lru_cache

from app.config import settings


@lru_cache
def get_embedding_model():
    # O modelo e carregado uma vez e fica em memoria.
    # Na primeira execucao ele pode demorar porque baixa o modelo open source.
    if not settings.huggingface_verify_ssl:
        import requests
        import urllib3
        from huggingface_hub import configure_http_backend

        def backend_factory() -> requests.Session:
            session = requests.Session()
            session.verify = False
            return session

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        configure_http_backend(backend_factory=backend_factory)

    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(settings.embedding_model)


def montar_texto_inadimplencia(row: dict) -> str:
    # Aqui voce decide quais campos representam melhor o perfil financeiro.
    # Quanto melhor este texto, melhor tende a ficar a busca semantica.
    valor = row.get("valor_inadimplencia") or 0
    localizacao = row.get("bairro") or row.get("regiao") or ""

    return (
        f"Cliente {row.get('nome_cliente', '')} com "
        f"{row.get('dias_inadimplencia', '')} dias de inadimplencia, "
        f"risco {row.get('tipo_risco', '')}, "
        f"valor R$ {float(valor):.2f}, "
        f"bairro {localizacao} em Marilia/SP."
    )


def gerar_embedding(texto: str) -> list[float]:
    # normalize_embeddings=True melhora o uso com distancia/similaridade cosseno.
    model = get_embedding_model()
    return model.encode(texto, normalize_embeddings=True).tolist()
