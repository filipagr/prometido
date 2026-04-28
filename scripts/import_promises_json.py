"""
scripts/import_promises_json.py

Importa promessas extraídas manualmente (via cowork) para a DB.

Uso:
    .venv/bin/python3 scripts/import_promises_json.py data/programs/2009/PS-leg-2009.json

O ficheiro JSON deve seguir o formato:
[
  {
    "text": "...",
    "context": "...",
    "topic": "...",
    "confidence": 0.95
  },
  ...
]

O party_id e election_id são inferidos do nome do ficheiro: {PARTY}-leg-{YEAR}.json
"""

import hashlib
import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from backend.database import get_connection, init_db


def parse_filename(path: Path) -> tuple[str, str]:
    """Extrai party_id e election_id do nome do ficheiro. Ex: PS-leg-2009.json → ('PS', 'leg_2009')"""
    stem = path.stem  # PS-leg-2009
    parts = stem.split("-")
    party_id = parts[0]
    year = parts[2]
    election_id = f"leg_{year}"
    return party_id, election_id


def promise_id(page_id: str, text: str) -> str:
    return hashlib.sha256(f"{page_id}|{text}".encode()).hexdigest()[:16]


def page_id_for(party_id: str, election_id: str) -> str:
    return hashlib.sha256(f"{party_id}|{election_id}|tier2|pdf-manual".encode()).hexdigest()[:16]


def main():
    if len(sys.argv) < 2:
        print("Uso: .venv/bin/python3 scripts/import_promises_json.py <ficheiro.json>")
        sys.exit(1)

    json_path = Path(sys.argv[1])
    if not json_path.exists():
        print(f"Ficheiro não encontrado: {json_path}")
        sys.exit(1)

    party_id, election_id = parse_filename(json_path)
    year = election_id.split("_")[1]

    print(f"Partido: {party_id} | Eleição: {election_id}")

    promises = json.loads(json_path.read_text())
    print(f"Promessas no ficheiro: {len(promises)}")

    init_db()
    conn = get_connection()

    # Verificar que partido e eleição existem
    party = conn.execute("SELECT id FROM parties WHERE id = ?", (party_id,)).fetchone()
    election = conn.execute("SELECT id FROM elections WHERE id = ?", (election_id,)).fetchone()

    if not party:
        print(f"ERRO: partido '{party_id}' não existe na DB. Verifica o nome do ficheiro.")
        sys.exit(1)
    if not election:
        print(f"ERRO: eleição '{election_id}' não existe na DB.")
        sys.exit(1)

    # Criar página fonte se não existir
    pid = page_id_for(party_id, election_id)
    pdf_filename = f"{party_id}-leg-{year}.pdf"
    pdf_path = Path("data/programs") / year / pdf_filename

    existing_page = conn.execute("SELECT id FROM archived_pages WHERE id = ?", (pid,)).fetchone()
    if not existing_page:
        conn.execute("""
            INSERT INTO archived_pages (id, url, archived_url, timestamp, party_id, election_id,
                                        tier, mime_type, status_code, crawled_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """, (
            pid,
            f"file://{pdf_path.resolve()}",
            f"file://{pdf_path.resolve()}",
            f"{year}0101000000",
            party_id,
            election_id,
            2,
            "application/pdf",
            200,
        ))
        print(f"✓ Página fonte criada: {pid}")
    else:
        print(f"  Página fonte já existe: {pid}")

    # Inserir promessas
    inserted = 0
    skipped = 0

    for p in promises:
        text = p.get("text", "").strip()
        if not text:
            continue

        prom_id = promise_id(pid, text)
        existing = conn.execute("SELECT id FROM promises WHERE id = ?", (prom_id,)).fetchone()
        if existing:
            skipped += 1
            continue

        conn.execute("""
            INSERT INTO promises (id, page_id, party_id, election_id, text, context, topic,
                                  tier, extraction_confidence, extraction_model, extracted_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            prom_id,
            pid,
            party_id,
            election_id,
            text[:500],
            p.get("context", "")[:300] if p.get("context") else None,
            p.get("topic", "outros"),
            2,
            float(p.get("confidence", 0.8)),
            "manual-cowork",
            datetime.now().isoformat(),
        ))
        inserted += 1

    conn.commit()
    conn.close()

    print(f"\n✓ Importação concluída: {inserted} inseridas | {skipped} já existiam")


if __name__ == "__main__":
    main()
