"""
GET /api/promise/{id}     — promessa completa + fontes de verificação
GET /api/promises         — lista de promessas (para curadoria interna)
PATCH /api/promise/{id}/status  — actualizar status manualmente (curadoria)
"""

import json

from fastapi import APIRouter, HTTPException, Body

from backend.database import get_connection

router = APIRouter()

VALID_STATUSES = {
    "archived",
    "corroborated",
    "evidence_of_implementation",
    "evidence_of_non_implementation",
    "partial_implementation",
    "untracked",
}


@router.get("/promise/{promise_id}")
def get_promise(promise_id: str):
    conn = get_connection()

    p = conn.execute(
        """SELECT p.*, pg.archived_url, pg.timestamp, pg.url as source_url, pg.source_type,
                  pt.name as party_name, pt.color as party_color, pt.short_name,
                  e.date as election_date, e.description as election_desc
           FROM promises p
           LEFT JOIN archived_pages pg ON p.page_id = pg.id
           LEFT JOIN parties pt ON p.party_id = pt.id
           LEFT JOIN elections e ON p.election_id = e.id
           WHERE p.id = ? AND p.is_valid = 1""",
        (promise_id,),
    ).fetchone()

    if not p:
        raise HTTPException(status_code=404, detail="Promessa não encontrada")

    # fontes de verificação
    sources = conn.execute(
        """SELECT * FROM verification_sources WHERE promise_id = ? ORDER BY source_date""",
        (promise_id,),
    ).fetchall()

    conn.close()
    return {
        "id": p["id"],
        "text": p["text"],
        "context": p["context"],
        "topic": p["topic"],
        "topics": json.loads(p["topics"]) if p["topics"] else [p["topic"]],
        "tier": p["tier"],
        "status": p["status"],
        "status_note": p["status_note"],
        "confidence": {
            "extraction": p["extraction_confidence"],
            "validation": p["validation_score"],
        },
        "party": {
            "id": p["party_id"],
            "name": p["party_name"],
            "short_name": p["short_name"],
            "color": p["party_color"],
        },
        "election": {
            "id": p["election_id"],
            "date": p["election_date"],
            "description": p["election_desc"],
        },
        "source": {
            "archived_url": p["archived_url"],
            "original_url": p["source_url"],
            "archived_date": p["timestamp"][:8] if p["timestamp"] else None,
            "archived_datetime": p["timestamp"],
            "source_type": p["source_type"] or "arquivo_pt",
        },
        "verification_sources": [
            {
                "id": s["id"],
                "archived_url": s["archived_url"],
                "source_domain": s["source_domain"],
                "date": s["source_date"],
                "use_type": s["use_type"],
                "quote": s["quote"],
                "added_by": s["added_by"],
            }
            for s in sources
        ],
    }


@router.patch("/promise/{promise_id}/status")
def update_promise_status(
    promise_id: str,
    status: str = Body(..., embed=True),
    status_note: str | None = Body(None, embed=True),
):
    """Endpoint de curadoria: actualiza o status de uma promessa manualmente."""
    if status not in VALID_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Status inválido. Valores aceites: {', '.join(sorted(VALID_STATUSES))}",
        )

    conn = get_connection()
    existing = conn.execute("SELECT id FROM promises WHERE id = ?", (promise_id,)).fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Promessa não encontrada")

    conn.execute(
        "UPDATE promises SET status = ?, status_note = ? WHERE id = ?",
        (status, status_note, promise_id),
    )
    conn.commit()
    conn.close()
    return {"id": promise_id, "status": status, "status_note": status_note}
