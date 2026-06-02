import os
from pathlib import Path

from dotenv import load_dotenv


# Carrega as variaveis do arquivo .env.
# Tudo que for senha, chave ou URL sensivel deve ficar no .env, nao no codigo.
ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(ENV_PATH)


class Settings:
    app_name: str = os.getenv("APP_NAME", "Interfocus PayFlow API")
    app_env: str = os.getenv("APP_ENV", "development")

    supabase_url: str | None = os.getenv("SUPABASE_URL")
    supabase_service_role_key: str | None = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    supabase_table_inadimplencias: str = os.getenv(
        "SUPABASE_TABLE_INADIMPLENCIAS",
        "inadimplencias",
    )
    supabase_match_function: str = os.getenv(
        "SUPABASE_MATCH_FUNCTION",
        "match_inadimplencias",
    )
    supabase_verify_ssl: bool = os.getenv(
        "SUPABASE_VERIFY_SSL",
        "true",
    ).lower() not in {"0", "false", "no", "nao"}

    embedding_model: str = os.getenv(
        "EMBEDDING_MODEL",
        "sentence-transformers/all-MiniLM-L6-v2",
    )
    embedding_batch_size: int = int(os.getenv("EMBEDDING_BATCH_SIZE", "100"))
    huggingface_verify_ssl: bool = os.getenv(
        "HUGGINGFACE_VERIFY_SSL",
        "true",
    ).lower() not in {"0", "false", "no", "nao"}


settings = Settings()
