"""
GET /api/parties          — lista de partidos com stats
GET /api/party/{id}       — partido + promessas por eleição + breakdown
"""

import json

from fastapi import APIRouter, HTTPException

from backend.database import get_connection

router = APIRouter()


@router.get("/parties")
def list_parties():
    conn = get_connection()

    parties = conn.execute("SELECT * FROM parties ORDER BY id").fetchall()

    result = []
    for p in parties:
        total = conn.execute(
            "SELECT COUNT(*) FROM promises WHERE party_id = ? AND is_valid = 1",
            (p["id"],),
        ).fetchone()[0]

        elections_covered = conn.execute(
            "SELECT COUNT(DISTINCT election_id) FROM promises WHERE party_id = ? AND is_valid = 1",
            (p["id"],),
        ).fetchone()[0]

        result.append({
            "id": p["id"],
            "name": p["name"],
            "short_name": p["short_name"],
            "color": p["color"],
            "founded": p["founded"],
            "domains": json.loads(p["domains"] or "[]"),
            "promise_count": total,
            "elections_covered": elections_covered,
            "notes": p["notes"],
        })

    conn.close()
    return result


@router.get("/party/{party_id}")
def get_party(party_id: str):
    conn = get_connection()

    party = conn.execute("SELECT * FROM parties WHERE id = ?", (party_id,)).fetchone()
    if not party:
        raise HTTPException(status_code=404, detail="Partido não encontrado")

    # promessas agrupadas por eleição
    elections = conn.execute(
        """SELECT e.id, e.date, e.description,
                  COUNT(p.id) as promise_count,
                  SUM(CASE WHEN p.status = 'corroborated' THEN 1 ELSE 0 END) as corroborated,
                  SUM(CASE WHEN p.status = 'evidence_of_implementation' THEN 1 ELSE 0 END) as implemented,
                  SUM(CASE WHEN p.status = 'evidence_of_non_implementation' THEN 1 ELSE 0 END) as not_implemented,
                  SUM(CASE WHEN p.status = 'partial_implementation' THEN 1 ELSE 0 END) as partial
           FROM elections e
           LEFT JOIN promises p ON p.election_id = e.id AND p.party_id = ? AND p.is_valid = 1
           GROUP BY e.id
           ORDER BY e.date DESC""",
        (party_id,),
    ).fetchall()

    promise_count = conn.execute(
        "SELECT COUNT(*) FROM promises WHERE party_id = ? AND is_valid = 1",
        (party_id,),
    ).fetchone()[0]

    elections_covered = conn.execute(
        "SELECT COUNT(DISTINCT election_id) FROM promises WHERE party_id = ? AND is_valid = 1",
        (party_id,),
    ).fetchone()[0]

    # breakdown por tópico
    topics = conn.execute(
        """SELECT topic, COUNT(*) as n
           FROM promises
           WHERE party_id = ? AND is_valid = 1
           GROUP BY topic
           ORDER BY n DESC""",
        (party_id,),
    ).fetchall()

    conn.close()
    return {
        "id": party["id"],
        "name": party["name"],
        "short_name": party["short_name"],
        "color": party["color"],
        "founded": party["founded"],
        "domains": json.loads(party["domains"] or "[]"),
        "notes": party["notes"],
        "promise_count": promise_count,
        "elections_covered": elections_covered,
        "elections": [
            {
                "id": e["id"],
                "date": e["date"],
                "description": e["description"],
                "promise_count": e["promise_count"],
                "statuses": {
                    "corroborated": e["corroborated"],
                    "implemented": e["implemented"],
                    "not_implemented": e["not_implemented"],
                    "partial": e["partial"],
                },
            }
            for e in elections
            if e["promise_count"] > 0
        ],
        "topics": [{"topic": t["topic"], "count": t["n"]} for t in topics],
    }
