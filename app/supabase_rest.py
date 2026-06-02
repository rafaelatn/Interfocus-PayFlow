from urllib.parse import quote

import httpx

from app.config import settings


def _verify_ssl() -> bool:
    return settings.supabase_verify_ssl


def _headers(prefer: str = "return=representation") -> dict[str, str]:
    if not settings.supabase_service_role_key:
        raise RuntimeError("Configure SUPABASE_SERVICE_ROLE_KEY no arquivo .env")

    return {
        "apikey": settings.supabase_service_role_key,
        "Authorization": f"Bearer {settings.supabase_service_role_key}",
        "Content-Type": "application/json",
        "Prefer": prefer,
    }


def _base_url() -> str:
    if not settings.supabase_url:
        raise RuntimeError("Configure SUPABASE_URL no arquivo .env")
    return settings.supabase_url.rstrip("/")


def _table_url(path: str) -> str:
    return f"{_base_url()}/rest/v1/{path}"


def _raise_for_supabase(response: httpx.Response) -> None:
    if response.is_error:
        raise RuntimeError(f"Erro Supabase {response.status_code}: {response.text}")


def select_rows(
    table: str,
    columns: str,
    limit: int | None = None,
    filters: dict[str, str] | None = None,
    order: str | None = None,
) -> list[dict]:
    table_name = quote(table, safe="")
    query = [f"select={columns}"]
    if limit is not None:
        query.append(f"limit={limit}")
    if order:
        query.append(f"order={quote(order, safe='.,')}")
    for field, expression in (filters or {}).items():
        query.append(f"{quote(field, safe='')}={expression}")

    response = httpx.get(
        _table_url(f"{table_name}?{'&'.join(query)}"),
        headers=_headers(),
        verify=_verify_ssl(),
        timeout=30,
    )
    _raise_for_supabase(response)
    return response.json()


def insert_row(table: str, payload: dict) -> list[dict]:
    table_name = quote(table, safe="")
    response = httpx.post(
        _table_url(table_name),
        headers=_headers(),
        json=payload,
        verify=_verify_ssl(),
        timeout=30,
    )
    _raise_for_supabase(response)
    return response.json()


def update_by_id(
    table: str,
    row_id: str | int,
    payload: dict,
    prefer: str = "return=minimal",
) -> None:
    table_name = quote(table, safe="")
    row_id_encoded = quote(str(row_id), safe="")
    response = httpx.patch(
        _table_url(f"{table_name}?id=eq.{row_id_encoded}"),
        headers=_headers(prefer=prefer),
        json=payload,
        verify=_verify_ssl(),
        timeout=30,
    )
    _raise_for_supabase(response)


def rpc(function_name: str, payload: dict) -> list[dict]:
    function_path = quote(function_name, safe="")
    response = httpx.post(
        _table_url(f"rpc/{function_path}"),
        headers=_headers(),
        json=payload,
        verify=_verify_ssl(),
        timeout=60,
    )
    _raise_for_supabase(response)
    return response.json()
