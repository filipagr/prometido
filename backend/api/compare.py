"""
GET /api/compare
  ?topic=<habitação|saúde|...>    — obrigatório
  &parties=<PS,PSD,BE>            — opcional, default todos
  &election=<leg_2019|...>        — opcional, default todas as eleições

Feature principal do Arquivo Eleitoral — compara promessas de diferentes partidos
sobre o mesmo tema, lado a lado por partido.
"""

from fastapi import APIRouter, Query, HTTPException

from backend.database import get_connection

router = APIRouter()


@router.get("/compare")
def compare(
    topic: str = Query(..., description="Tópico a comparar (habitação, saúde, educação, ...)"),
    parties: str | None = Query(None, description="Partidos separados por vírgula (PS,PSD,BE)"),
    election: str | None = Query(None, description="Eleição específica (leg_2019)"),
):
    conn = get_connection()

    party_list = [p.strip() for p in parties.split(",")] if parties else None

    where_clauses = ["p.is_valid = 1", "(p.topic = ? OR EXISTS (SELECT 1 FROM json_each(p.topics) WHERE value = ?))"]
    params: list = [topic, topic]

    if party_list:
        where_clauses.append(f"p.party_id IN ({','.join('?' * len(party_list))})")
        params.extend(party_list)
    if election:
        where_clauses.append("p.election_id = ?")
        params.append(election)

    where = " AND ".join(where_clauses)

    rows = conn.execute(
        f"""SELECT p.id, p.text, p.topic, p.status, p.tier,
                   p.party_id, p.election_id,
                   pg.archived_url, pg.timestamp, pg.source_type,
                   pt.name as party_name, pt.color as party_color, pt.short_name,
                   e.date as election_date, e.description as election_desc
            FROM promises p
            LEFT JOIN archived_pages pg ON p.page_id = pg.id
            LEFT JOIN parties pt ON p.party_id = pt.id
            LEFT JOIN elections e ON p.election_id = e.id
            WHERE {where}
            ORDER BY e.date DESC, p.party_id""",
        params,
    ).fetchall()

    if not rows:
        conn.close()
        return {"topic": topic, "parties": [], "promise_count": 0}

    # agrupar por partido
    by_party: dict[str, dict] = {}
    for r in rows:
        pid = r["party_id"]
        if pid not in by_party:
            by_party[pid] = {
                "id": pid,
                "name": r["party_name"],
                "short_name": r["short_name"],
                "color": r["party_color"],
                "promises": [],
            }
        by_party[pid]["promises"].append({
            "id": r["id"],
            "text": r["text"],
            "status": r["status"],
            "tier": r["tier"],
            "election": {
                "id": r["election_id"],
                "date": r["election_date"],
                "description": r["election_desc"],
            },
            "archived_url": r["archived_url"],
            "archived_date": r["timestamp"][:8] if r["timestamp"] else None,
            "source_type": r["source_type"] or "arquivo_pt",
        })

    conn.close()
    return {
        "topic": topic,
        "election_filter": election,
        "promise_count": len(rows),
        "parties": list(by_party.values()),
    }
