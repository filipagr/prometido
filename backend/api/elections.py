"""
GET /api/elections    — lista de eleições com stats
"""

import json

from fastapi import APIRouter

from backend.database import get_connection

router = APIRouter()


@router.get("/elections")
def list_elections():
    conn = get_connection()

    elections = conn.execute("SELECT * FROM elections ORDER BY date DESC").fetchall()

    result = []
    for e in elections:
        promise_count = conn.execute(
            "SELECT COUNT(*) FROM promises WHERE election_id = ? AND is_valid = 1",
            (e["id"],),
        ).fetchone()[0]

        parties_covered = conn.execute(
            "SELECT COUNT(DISTINCT party_id) FROM promises WHERE election_id = ? AND is_valid = 1",
            (e["id"],),
        ).fetchone()[0]

        result.append({
            "id": e["id"],
            "type": e["type"],
            "date": e["date"],
            "description": e["description"],
            "discovery_window": json.loads(e["discovery_window"] or "{}"),
            "promise_count": promise_count,
            "parties_covered": parties_covered,
        })

    conn.close()
    return result
