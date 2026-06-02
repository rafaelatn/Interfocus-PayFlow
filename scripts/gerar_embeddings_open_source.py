import os

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from supabase import create_client


load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
TABLE_NAME = os.getenv(
    "SUPABASE_EMBEDDING_TABLE",
    os.getenv("SUPABASE_TABLE_INADIMPLENCIAS", "inadimplencias"),
)
BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "100"))
MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2",
)


def require_env(name: str, value: str | None) -> str:
    if not value:
        raise RuntimeError(f"Configure {name} no arquivo .env")
    return value


def montar_texto(row: dict) -> str:
    valor = row.get("valor_inadimplencia") or 0
    return (
        f"Cliente {row.get('nome_cliente', '')} com "
        f"{row.get('dias_inadimplencia', '')} dias de inadimplencia, "
        f"risco {row.get('tipo_risco', '')}, "
        f"valor R$ {float(valor):.2f}, "
        f"regiao {row.get('regiao', '')}."
    )


def main() -> None:
    supabase_url = require_env("SUPABASE_URL", SUPABASE_URL)
    supabase_key = require_env("SUPABASE_SERVICE_ROLE_KEY", SUPABASE_KEY)

    client = create_client(supabase_url, supabase_key)
    model = SentenceTransformer(MODEL_NAME)

    rows = (
        client.table(TABLE_NAME)
        .select(
            "id,nome_cliente,dias_inadimplencia,tipo_risco,"
            "valor_inadimplencia,regiao"
        )
        .is_("embedding", "null")
        .limit(BATCH_SIZE)
        .execute()
    )

    if not rows.data:
        print("Nenhum registro sem embedding encontrado.")
        return

    for row in rows.data:
        texto = montar_texto(row)
        embedding = model.encode(texto, normalize_embeddings=True).tolist()

        (
            client.table(TABLE_NAME)
            .update({"embedding": embedding})
            .eq("id", row["id"])
            .execute()
        )

        print(f"Embedding salvo para id={row['id']}")

    print(f"Finalizado. Registros processados: {len(rows.data)}")


if __name__ == "__main__":
    main()
