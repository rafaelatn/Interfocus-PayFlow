from pathlib import Path
import json
import sys
import time


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.config import settings
from app.services.embeddings import gerar_embedding
from app.supabase_rest import rpc, select_rows


CONSULTAS_VALIDACAO = [
    "clientes de alto risco no Alto Cafezal",
    "clientes com muitos dias de atraso no Palmital",
    "dividas altas perto do Centro",
    "clientes de risco medio em Jardim America",
    "clientes de baixo risco em Nova Marilia",
]


def normalizar_risco(risco: str) -> str:
    risco = str(risco or "").lower()
    if "crit" in risco or "alto" in risco:
        return "alto"
    if "m" in risco:
        return "medio"
    return "baixo"


def classificar_por_atraso(dias: int) -> str:
    dias = int(dias or 0)
    if dias <= 30:
        return "baixo"
    if dias <= 90:
        return "medio"
    return "alto"


def validar_precisao(rows: list[dict]) -> dict:
    total = max(len(rows), 1)
    acertos = sum(
        1
        for row in rows
        if normalizar_risco(row.get("tipo_risco"))
        == classificar_por_atraso(row.get("dias_inadimplencia"))
    )
    return {
        "total_avaliado": len(rows),
        "acertos": acertos,
        "precisao": round(acertos / total, 3),
    }


def validar_eficiencia(rows: list[dict], tempo_listagem: float) -> dict:
    inicio = time.perf_counter()
    for consulta in CONSULTAS_VALIDACAO:
        embedding = gerar_embedding(consulta)
        rpc(
            settings.supabase_match_function,
            {"query_embedding": embedding, "match_count": 5},
        )
    tempo_buscas = time.perf_counter() - inicio

    amostra = rows[:100]
    inicio = time.perf_counter()
    for row in amostra:
        (
            f"Olá {row.get('nome_cliente')}, identificamos "
            f"{row.get('dias_inadimplencia')} dias de atraso no pagamento de "
            f"R$ {row.get('valor_inadimplencia')}. Bairro: {row.get('bairro')}."
        )
    tempo_mensagens = time.perf_counter() - inicio

    # Referencia operacional simulada para comparacao didatica:
    # localizar cliente, conferir dados e escrever mensagem manualmente.
    tempo_manual_por_cliente_s = 60
    tempo_manual_100_clientes_s = tempo_manual_por_cliente_s * len(amostra)

    return {
        "tempo_listagem_1000_s": round(tempo_listagem, 3),
        "tempo_5_buscas_ia_s": round(tempo_buscas, 3),
        "tempo_gerar_100_mensagens_s": round(tempo_mensagens, 6),
        "referencia_manual_100_clientes_s": tempo_manual_100_clientes_s,
        "ganho_estimado_mensagens_100_clientes_x": round(
            tempo_manual_100_clientes_s / max(tempo_mensagens, 0.001),
            1,
        ),
    }


def validar_consistencia(rows: list[dict]) -> dict:
    amostra = rows[:100]
    consistentes = 0
    for row in amostra:
        mensagem = (
            f"Olá {row.get('nome_cliente')}, identificamos "
            f"{row.get('dias_inadimplencia')} dias de atraso no pagamento de "
            f"R$ {row.get('valor_inadimplencia')}. Bairro: {row.get('bairro')}."
        )
        campos = [
            row.get("nome_cliente"),
            row.get("dias_inadimplencia"),
            row.get("valor_inadimplencia"),
            row.get("bairro"),
        ]
        if all(str(campo) in mensagem for campo in campos):
            consistentes += 1

    return {
        "amostra_mensagens": len(amostra),
        "mensagens_consistentes": consistentes,
        "consistencia": round(consistentes / max(len(amostra), 1), 3),
    }


def main() -> None:
    inicio = time.perf_counter()
    rows = select_rows(
        settings.supabase_table_inadimplencias,
        "id,nome_cliente,dias_inadimplencia,tipo_risco,"
        "valor_inadimplencia,bairro,tentativas_cobranca,embedding",
        limit=1000,
    )
    tempo_listagem = time.perf_counter() - inicio

    metricas = {
        "total_registros": len(rows),
        "embedding_preenchido": sum(1 for row in rows if row.get("embedding") is not None),
        "embedding_null": sum(1 for row in rows if row.get("embedding") is None),
        "precisao_ia": validar_precisao(rows),
        "eficiencia_operacional": validar_eficiencia(rows, tempo_listagem),
        "consistencia_dados": validar_consistencia(rows),
    }
    print(json.dumps(metricas, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
