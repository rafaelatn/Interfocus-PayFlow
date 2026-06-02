from functools import lru_cache

from app.config import settings


@lru_cache
def get_supabase():
    # Este e o ponto central de conexao com o Supabase.
    # As rotas chamam esta funcao quando precisam ler ou gravar no banco.
    if not settings.supabase_url:
        raise RuntimeError("Configure SUPABASE_URL no arquivo .env")

    if not settings.supabase_service_role_key:
        raise RuntimeError("Configure SUPABASE_SERVICE_ROLE_KEY no arquivo .env")

    from supabase import create_client

    return create_client(
        settings.supabase_url,
        settings.supabase_service_role_key,
    )
