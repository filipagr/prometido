"""
scripts/add_promises.py

Adiciona promessas à DB a partir de um JSON no formato ChatGPT.

Uso:
    python3 scripts/add_promises.py <PARTIDO> <ANO> <ficheiro.json>

Exemplos:
    python3 scripts/add_promises.py PSD 2025 data/imports/ad_2025_saude.json
    python3 scripts/add_promises.py PS  2025 data/imports/ps_2025_habitacao.json

Partidos válidos: PS, PSD, BE, PCP, IL, CH, LV, PAN, CDS
Anos válidos:     2002, 2005, 2009, 2011, 2015, 2019, 2022, 2024, 2025

Formato do JSON:
[
  {
    "categoria": "educação",                          -- string ou array: ["educação", "economia"]
    "tipo": "medida_concreta",                        -- ignorado
    "texto_original": "Texto da promessa...",
    "confianca_extracao": 0.98
  },
  ...
]

Se "categoria" for um array, o primeiro elemento é o tópico primário (topic)
e todos ficam guardados em topics (JSON array). O campo "tipo" e "nivel" são ignorados.
Promessas duplicadas são ignoradas automaticamente (não dão erro).
"""

import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "prometido.db"


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)

    party_id   = sys.argv[1]  # preserve case (Chega, Livre) — validated against DB below
    year       = sys.argv[2]
    json_path  = Path(sys.argv[3])
    election_id = f"leg_{year}"

    if not json_path.exists():
        print(f"Erro: ficheiro não encontrado — {json_path}")
        sys.exit(1)

    import sqlite3
    conn = sqlite3.connect(DB_PATH)

    # Validar partido e eleição
    if not conn.execute("SELECT 1 FROM parties WHERE id = ?", (party_id,)).fetchone():
        print(f"Erro: partido '{party_id}' não existe. Partidos válidos: PS, PSD, BE, PCP, IL, Chega, Livre, PAN, CDS")
        sys.exit(1)
    if not conn.execute("SELECT 1 FROM elections WHERE id = ?", (election_id,)).fetchone():
        print(f"Erro: eleição '{election_id}' não existe.")
        sys.exit(1)

    data = json.loads(json_path.read_text())
    print(f"Partido: {party_id} | Eleição: {election_id} | Promessas no ficheiro: {len(data)}")

    # Garantir que a página fonte existe
    page_id = hashlib.sha256(f"{party_id}|{election_id}|tier2|pdf-manual".encode()).hexdigest()[:16]
    if not conn.execute("SELECT 1 FROM archived_pages WHERE id = ?", (page_id,)).fetchone():
        conn.execute("""
            INSERT INTO archived_pages (id, url, archived_url, timestamp, party_id, election_id,
                                        tier, mime_type, status_code, crawled_at)
            VALUES (?, ?, ?, ?, ?, ?, 2, 'application/pdf', 200, datetime('now'))
        """, (
            page_id,
            f"file://data/programs/{year}/{party_id}-leg-{year}.pdf",
            f"file://data/programs/{year}/{party_id}-leg-{year}.pdf",
            f"{year}0101000000",
            party_id, election_id,
        ))

    inserted = skipped = 0
    for p in data:
        text = p.get("texto_original", "").strip()
        if not text:
            continue
        # normalizar formatação
        text = text[0].upper() + text[1:] if text else text
        if text and text[-1] not in ".!?":
            text += "."

        # categoria pode ser string ou array
        cat = p.get("categoria", "outros")
        if isinstance(cat, list):
            topic = cat[0] if cat else "outros"
            topics = json.dumps(cat, ensure_ascii=False)
        else:
            topic = cat
            topics = json.dumps([cat], ensure_ascii=False)

        prom_id = hashlib.sha256(f"{page_id}|{text}".encode()).hexdigest()[:16]
        result = conn.execute("""
            INSERT OR IGNORE INTO promises
            (id, page_id, party_id, election_id, text, topic, topics, tier,
             extraction_confidence, is_valid, extraction_model, extracted_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 2, ?, 1, 'chatgpt-manual', ?)
        """, (
            prom_id, page_id, party_id, election_id,
            text[:500],
            topic,
            topics,
            float(p.get("confianca_extracao", 0.9)),
            datetime.now().isoformat(),
        ))
        if result.rowcount:
            inserted += 1
        else:
            skipped += 1

    # Reconstruir índice FTS5
    conn.execute("INSERT INTO promises_fts(promises_fts) VALUES('rebuild')")
    conn.commit()

    n = conn.execute(
        "SELECT COUNT(*) FROM promises WHERE party_id=? AND election_id=?",
        (party_id, election_id)
    ).fetchone()[0]
    total = conn.execute("SELECT COUNT(*) FROM promises WHERE is_valid=1").fetchone()[0]

    print(f"✓ Inseridas: {inserted} | Já existiam (skip): {skipped}")
    print(f"  {party_id} {election_id}: {n} promessas | Total DB: {total}")
    print()
    print("Não te esqueças de fazer commit:")
    print(f"  git add data/prometido.db && git commit -m 'add: {party_id} {year} promessas' && git push")

    conn.close()


if __name__ == "__main__":
    main()
