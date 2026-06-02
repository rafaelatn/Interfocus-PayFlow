from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.config import settings
from app.services.embeddings import gerar_embedding, montar_texto_inadimplencia
from app.supabase_rest import rpc, select_rows, update_by_id


CONSULTAS_TESTE = [
    "clientes de alto risco em bairros de Marilia",
    "clientes com muitos dias de atraso no Palmital",
    "dividas altas perto do Centro",
]


def treinar_embeddings(limite: int = 20) -> int:
    rows = select_rows(
        settings.supabase_table_inadimplencias,
            "id,nome_cliente,dias_inadimplencia,tipo_risco,"
        "valor_inadimplencia,bairro",
        limit=limite,
        filters={"embedding": "is.null"},
    )

    for row in rows:
        texto = montar_texto_inadimplencia(row)
        embedding = gerar_embedding(texto)
        update_by_id(
            settings.supabase_table_inadimplencias,
            row["id"],
            {"embedding": embedding},
        )
        print(f"Treinado id={row['id']} | {texto}")

    return len(rows)


def testar_consultas(limite_por_consulta: int = 3) -> None:
    for consulta in CONSULTAS_TESTE:
        embedding = gerar_embedding(consulta)
        resultados = rpc(
            settings.supabase_match_function,
            {
                "query_embedding": embedding,
                "match_count": limite_por_consulta,
            },
        )

        print()
        print(f"Consulta: {consulta}")
        if not resultados:
            print("  Sem resultados. Verifique se existem embeddings preenchidos.")
            continue

        for row in resultados:
            similaridade = float(row.get("similaridade") or 0)
            print(
                "  "
                f"{row.get('nome_cliente')} | "
                f"{row.get('bairro') or row.get('regiao')} | "
                f"risco {row.get('tipo_risco')} | "
                f"similaridade {similaridade:.3f}"
            )


def main() -> None:
    print("1) Treino: transformando registros da tabela em embeddings.")
    total = treinar_embeddings()
    print(f"Registros treinados nesta execucao: {total}")

    print()
    print("2) Teste: fazendo perguntas semanticamente parecidas.")
    testar_consultas()


if __name__ == "__main__":
    main()
