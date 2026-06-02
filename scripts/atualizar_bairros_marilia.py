import argparse
import random
from pathlib import Path
import sys
from urllib.parse import quote

import httpx

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.config import settings
from app.data.marilia_bairros import BAIRROS_MARILIA
from app.supabase_client import get_supabase


def escolher_bairro(rng: random.Random) -> str:
    return rng.choice(BAIRROS_MARILIA)["nome"]


def headers_supabase() -> dict[str, str]:
    return {
        "apikey": settings.supabase_service_role_key or "",
        "Authorization": f"Bearer {settings.supabase_service_role_key or ''}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }


def rest_url(path: str) -> str:
    return f"{settings.supabase_url}/rest/v1/{path}"


def buscar_ids(limite: int) -> list[str]:
    supabase = get_supabase()
    response = (
        supabase.table(settings.supabase_table_inadimplencias)
        .select("id")
        .order("created_at", desc=True)
        .limit(limite)
        .execute()
    )
    return [row["id"] for row in response.data or []]


def buscar_ids_rest(limite: int, verificar_ssl: bool) -> list[str]:
    tabela = quote(settings.supabase_table_inadimplencias, safe="")
    url = rest_url(f"{tabela}?select=id&limit={limite}")
    response = httpx.get(url, headers=headers_supabase(), verify=verificar_ssl, timeout=30)
    if response.is_error:
        raise RuntimeError(f"Erro ao buscar ids no Supabase: {response.text}")
    return [row["id"] for row in response.json()]


def atualizar_registros(
    ids: list[str],
    seed: int,
    manter_embedding: bool,
    coluna_bairro: str,
) -> None:
    supabase = get_supabase()
    rng = random.Random(seed)

    for pos, row_id in enumerate(ids, start=1):
        payload = {coluna_bairro: escolher_bairro(rng)}
        if not manter_embedding:
            payload["embedding"] = None

        (
            supabase.table(settings.supabase_table_inadimplencias)
            .update(payload)
            .eq("id", row_id)
            .execute()
        )

        if pos % 50 == 0:
            print(f"{pos}/{len(ids)} registros atualizados...")


def atualizar_registros_rest(
    ids: list[str],
    seed: int,
    manter_embedding: bool,
    verificar_ssl: bool,
    coluna_bairro: str,
) -> None:
    rng = random.Random(seed)
    tabela = quote(settings.supabase_table_inadimplencias, safe="")

    for pos, row_id in enumerate(ids, start=1):
        payload = {coluna_bairro: escolher_bairro(rng)}
        if not manter_embedding:
            payload["embedding"] = None

        row_id_encoded = quote(str(row_id), safe="")
        url = rest_url(f"{tabela}?id=eq.{row_id_encoded}")
        response = httpx.patch(
            url,
            headers=headers_supabase(),
            json=payload,
            verify=verificar_ssl,
            timeout=30,
        )
        if response.is_error:
            raise RuntimeError(
                f"Erro ao atualizar id={row_id} no Supabase: {response.text}"
            )

        if pos % 50 == 0:
            print(f"{pos}/{len(ids)} registros atualizados...")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Troca a coluna regiao por bairros reais de Marilia/SP."
    )
    parser.add_argument("--limite", type=int, default=200)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--manter-embedding",
        action="store_true",
        help="Nao limpa embeddings existentes depois de mudar a regiao.",
    )
    parser.add_argument(
        "--sem-verificar-ssl",
        action="store_true",
        help="Usa REST direto sem verificar SSL. Use apenas em ambiente local.",
    )
    parser.add_argument(
        "--coluna",
        default="bairro",
        help="Coluna que recebera o bairro. Padrao: bairro.",
    )
    args = parser.parse_args()

    if args.sem_verificar_ssl:
        ids = buscar_ids_rest(args.limite, verificar_ssl=False)
    else:
        ids = buscar_ids(args.limite)

    if not ids:
        print("Nenhum registro encontrado na tabela.")
        return

    if args.sem_verificar_ssl:
        atualizar_registros_rest(
            ids,
            args.seed,
            args.manter_embedding,
            verificar_ssl=False,
            coluna_bairro=args.coluna,
        )
    else:
        atualizar_registros(ids, args.seed, args.manter_embedding, args.coluna)

    print(f"Finalizado. Registros atualizados: {len(ids)}")
    if not args.manter_embedding:
        print("Embeddings antigos foram limpos. Rode o treino para recalcular.")


if __name__ == "__main__":
    main()
