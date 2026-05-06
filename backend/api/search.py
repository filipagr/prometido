"""
GET /api/search
  ?q=<termo>
  &party=<PS|PSD|...>
  &election=<leg_2005|...>
  &topic=<habitação|...>
  &tier=<1|2|3>
  &status=<archived|corroborated|...>
  &limit=<int>          default 20, max 100
  &offset=<int>         default 0

Usa FTS5 se ?q= presente, caso contrário filtros directos.
"""

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from backend.database import get_connection

router = APIRouter()


@router.get("/search")
def search(
    q: str | None = Query(None),
    party: str | None = None,
    election: str | None = None,
    topic: str | None = None,
    tier: int | None = None,
    status: str | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    conn = get_connection()

    if q:
        # FTS5 full-text search
        base_query = """
            SELECT p.id, p.text, p.topic, p.party_id, p.election_id, p.tier, p.status,
                   p.extraction_confidence, p.validation_score,
                   pg.archived_url, pg.timestamp, pg.source_type,
                   pt.name as party_name, pt.short_name as party_short_name, pt.color as party_color,
                   e.date as election_date, e.description as election_desc,
                   eg.role as governed_role
            FROM promises_fts fts
            JOIN promises p ON fts.rowid = p.rowid
            LEFT JOIN archived_pages pg ON p.page_id = pg.id
            LEFT JOIN parties pt ON p.party_id = pt.id
            LEFT JOIN elections e ON p.election_id = e.id
            LEFT JOIN election_governments eg ON eg.election_id = p.election_id AND eg.party_id = p.party_id
            WHERE fts.promises_fts MATCH ?
              AND p.is_valid = 1
        """
        params: list = [q + "*"]
    else:
        base_query = """
            SELECT p.id, p.text, p.topic, p.party_id, p.election_id, p.tier, p.status,
                   p.extraction_confidence, p.validation_score,
                   pg.archived_url, pg.timestamp, pg.source_type,
                   pt.name as party_name, pt.short_name as party_short_name, pt.color as party_color,
                   e.date as election_date, e.description as election_desc,
                   eg.role as governed_role
            FROM promises p
            LEFT JOIN archived_pages pg ON p.page_id = pg.id
            LEFT JOIN parties pt ON p.party_id = pt.id
            LEFT JOIN elections e ON p.election_id = e.id
            LEFT JOIN election_governments eg ON eg.election_id = p.election_id AND eg.party_id = p.party_id
            WHERE p.is_valid = 1
        """
        params = []

    filters = []
    if party:
        filters.append("p.party_id = ?")
        params.append(party)
    if election:
        filters.append("p.election_id = ?")
        params.append(election)
    if topic:
        filters.append("p.topic = ?")
        params.append(topic)
    if tier is not None:
        filters.append("p.tier = ?")
        params.append(tier)
    if status:
        filters.append("p.status = ?")
        params.append(status)

    if filters:
        base_query += " AND " + " AND ".join(filters)

    # total para paginação
    count_query = f"SELECT COUNT(*) FROM ({base_query})"
    total = conn.execute(count_query, params).fetchone()[0]

    base_query += f" ORDER BY p.election_id DESC, p.party_id LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    rows = conn.execute(base_query, params).fetchall()
    conn.close()

    results = [
        {
            "id": r["id"],
            "text": r["text"],
            "topic": r["topic"],
            "party": {"id": r["party_id"], "name": r["party_name"], "short_name": r["party_short_name"], "color": r["party_color"]},
            "election": {"id": r["election_id"], "date": r["election_date"], "description": r["election_desc"]},
            "tier": r["tier"],
            "status": r["status"],
            "confidence": r["extraction_confidence"],
            "archived_url": r["archived_url"],
            "archived_date": r["timestamp"][:8] if r["timestamp"] else None,
            "source_type": r["source_type"] or "arquivo_pt",
            "governed_role": r["governed_role"],
        }
        for r in rows
    ]

    return {"total": total, "offset": offset, "limit": limit, "results": results}
