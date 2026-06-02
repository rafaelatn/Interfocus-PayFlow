from pathlib import Path
import argparse
import sys


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.config import settings
from app.services.embeddings import gerar_embedding, montar_texto_inadimplencia
from app.supabase_rest import select_rows, update_by_id


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    # Este script e usado fora da API.
    # Ele serve para preencher registros antigos que ainda estao com embedding null.
    rows = select_rows(
        settings.supabase_table_inadimplencias,
            "id,nome_cliente,dias_inadimplencia,tipo_risco,"
        "valor_inadimplencia,bairro",
        limit=settings.embedding_batch_size,
        filters={"embedding": "is.null"},
    )

    if not rows:
        print("Nenhum registro com embedding null encontrado.")
        return

    for row in rows:
        texto = montar_texto_inadimplencia(row)
        embedding = gerar_embedding(texto)

        update_by_id(
            settings.supabase_table_inadimplencias,
            row["id"],
            {"embedding": embedding},
        )

        if not args.quiet:
            print(f"Embedding salvo para id={row['id']}")

    print(f"Finalizado. Registros processados: {len(rows)}")


if __name__ == "__main__":
    main()
