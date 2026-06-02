from pathlib import Path
import argparse
import random
import sys


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.config import settings
from app.services.embeddings import gerar_embedding, montar_texto_inadimplencia
from app.supabase_rest import rpc, select_rows, update_by_id


CAMPOS = (
    "id,nome_cliente,dias_inadimplencia,tipo_risco,"
    "valor_inadimplencia,bairro"
)


def texto_teste(row: dict) -> str:
    return (
        f"clientes com risco {row.get('tipo_risco')} em {row.get('bairro')} "
        f"com {row.get('dias_inadimplencia')} dias de atraso e valor "
        f"{row.get('valor_inadimplencia')}"
    )


def buscar_registros(limite: int) -> list[dict]:
    rows = select_rows(
        settings.supabase_table_inadimplencias,
        CAMPOS,
        limit=limite,
    )
    return [row for row in rows if row.get("id") is not None]


def separar_split(rows: list[dict], percentual_treino: float, seed: int):
    rng = random.Random(seed)
    ordenados = rows[:]
    rng.shuffle(ordenados)
    qtd_treino = round(len(ordenados) * percentual_treino)
    return ordenados[:qtd_treino], ordenados[qtd_treino:]


def aplicar_treino(rows_treino: list[dict], quiet: bool) -> None:
    total = len(rows_treino)
    for pos, row in enumerate(rows_treino, start=1):
        embedding = gerar_embedding(montar_texto_inadimplencia(row))
        update_by_id(
            settings.supabase_table_inadimplencias,
            row["id"],
            {"embedding": embedding},
        )
        if not quiet and (pos % 25 == 0 or pos == total):
            print(f"Treino: {pos}/{total} registros com embedding salvo")


def limpar_teste(rows_teste: list[dict], quiet: bool) -> None:
    total = len(rows_teste)
    for pos, row in enumerate(rows_teste, start=1):
        update_by_id(
            settings.supabase_table_inadimplencias,
            row["id"],
            {"embedding": None},
        )
        if not quiet and (pos % 50 == 0 or pos == total):
            print(f"Teste: {pos}/{total} registros reservados com embedding null")


def testar_holdout(rows_teste: list[dict], limite_resultados: int) -> dict:
    acertos_bairro = 0
    acertos_risco = 0
    consultas_com_resultado = 0
    soma_similaridade = 0.0
    exemplos = []

    for row in rows_teste:
        consulta = texto_teste(row)
        embedding = gerar_embedding(consulta)
        resultados = rpc(
            settings.supabase_match_function,
            {
                "query_embedding": embedding,
                "match_count": limite_resultados,
            },
        )
        if not resultados:
            continue

        consultas_com_resultado += 1
        primeiro = resultados[0]
        soma_similaridade += float(primeiro.get("similaridade") or 0)

        if primeiro.get("bairro") == row.get("bairro"):
            acertos_bairro += 1
        if primeiro.get("tipo_risco") == row.get("tipo_risco"):
            acertos_risco += 1

        if len(exemplos) < 5:
            exemplos.append(
                {
                    "teste_id": row.get("id"),
                    "consulta": consulta,
                    "resultado_top1": {
                        "nome_cliente": primeiro.get("nome_cliente"),
                        "bairro": primeiro.get("bairro"),
                        "tipo_risco": primeiro.get("tipo_risco"),
                        "similaridade": round(float(primeiro.get("similaridade") or 0), 3),
                    },
                }
            )

    total = max(len(rows_teste), 1)
    com_resultado = max(consultas_com_resultado, 1)
    return {
        "total_teste": len(rows_teste),
        "consultas_com_resultado": consultas_com_resultado,
        "acuracia_bairro_top1": round(acertos_bairro / total, 3),
        "acuracia_risco_top1": round(acertos_risco / total, 3),
        "similaridade_media_top1": round(soma_similaridade / com_resultado, 3),
        "exemplos": exemplos,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Separa inadimplencias em 70% treino e 30% teste para embeddings."
    )
    parser.add_argument("--limite", type=int, default=1000)
    parser.add_argument("--percentual-treino", type=float, default=0.70)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--limite-resultados", type=int, default=3)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    rows = buscar_registros(args.limite)
    if not rows:
        print("Nenhum registro encontrado.")
        return

    rows_treino, rows_teste = separar_split(rows, args.percentual_treino, args.seed)

    print(
        f"Total: {len(rows)} | treino: {len(rows_treino)} "
        f"({args.percentual_treino:.0%}) | teste: {len(rows_teste)}"
    )

    aplicar_treino(rows_treino, args.quiet)
    limpar_teste(rows_teste, args.quiet)

    metricas = testar_holdout(rows_teste, args.limite_resultados)
    print("Metricas do teste holdout:")
    print(f"- consultas com resultado: {metricas['consultas_com_resultado']}/{metricas['total_teste']}")
    print(f"- acuracia bairro top1: {metricas['acuracia_bairro_top1']:.1%}")
    print(f"- acuracia risco top1: {metricas['acuracia_risco_top1']:.1%}")
    print(f"- similaridade media top1: {metricas['similaridade_media_top1']}")
    print("Exemplos:")
    for exemplo in metricas["exemplos"]:
        top = exemplo["resultado_top1"]
        print(
            f"- teste id={exemplo['teste_id']} -> "
            f"{top['nome_cliente']} | {top['bairro']} | "
            f"risco {top['tipo_risco']} | sim {top['similaridade']}"
        )


if __name__ == "__main__":
    main()
