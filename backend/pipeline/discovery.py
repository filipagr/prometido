"""
pipeline/discovery.py

Descobre páginas arquivadas no Arquivo.pt para todos os domínios alvo
(Tier 1: partidos, Tier 2: governo, Tier 3: notícias) nas janelas
temporais de cada eleição legislativa.

Usa o endpoint CDX: https://arquivo.pt/wayback/cdx
textsearch está em baixo (HTTP 500).

Campos relevantes na resposta CDX:
  urlkey, timestamp, url, mimetype, statuscode, digest, length
"""

import hashlib
import json
import logging
import sqlite3
import time
from pathlib import Path
from typing import Iterator

import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

CDX_BASE = "https://arquivo.pt/wayback/cdx"

# Tier 1 — sites dos partidos
PARTY_DOMAINS: dict[str, list[str]] = {
    "PS":    ["ps.pt", "partido-socialista.pt"],
    "PSD":   ["psd.pt", "ppd-psd.pt"],
    "BE":    ["bloco.org", "blockesquerda.net"],
    "PCP":   ["pcp.pt", "cdu.pt"],
    "CDS":   ["cds.pt", "partido-cds.pt"],
    "IL":    ["iniciativaliberal.pt"],
    "Chega": ["chega.pt"],
    "Livre": ["partidolivre.pt"],
    "PAN":   ["pan.com.pt"],
}

# Tier 2 — programas de governo
GOVERNMENT_DOMAINS: list[str] = [
    "portugal.gov.pt",
    "programa.gov.pt",
    "republica.pt",
]

# Tier 3 — notícias
NEWS_DOMAINS: dict[str, str] = {
    "Público":            "publico.pt",
    "Expresso":           "expresso.pt",
    "Observador":         "observador.pt",
    "Jornal de Negócios": "jornaldenegocios.pt",
    "RTP":                "rtp.pt",
    "SIC Notícias":       "sicnoticias.pt",
}

SEEDS_PATH = Path(__file__).parent.parent.parent / "data" / "seeds"


def _page_id(url: str, timestamp: str) -> str:
    return hashlib.sha256(f"{url}|{timestamp}".encode()).hexdigest()[:16]


def _cdx_query(
    domain: str,
    from_date: str,
    to_date: str,
    limit: int = 500,
    timeout: int = 90,
) -> list[dict]:
    """
    Faz uma query ao CDX e devolve lista de resultados como dicts.

    A API devolve NDJSON (text/x-ndjson): uma linha por resultado.
    Campos: url, timestamp, mimetype, status (não statuscode).
    """
    params = {
        "url": f"{domain}/*",
        "output": "json",
        "limit": str(limit),
        "from": from_date,
        "to": to_date,
        "collapse": "urlkey",
        "filter": "status:200",
        "fl": "url,timestamp,mime,status",
    }
    try:
        resp = httpx.get(CDX_BASE, params=params, timeout=timeout)
        resp.raise_for_status()
        results = []
        for line in resp.text.splitlines():
            line = line.strip()
            if line:
                results.append(json.loads(line))
        return results
    except httpx.HTTPStatusError as e:
        log.warning(f"CDX HTTP {e.response.status_code} para {domain} ({from_date}-{to_date})")
        return []
    except Exception as e:
        log.warning(f"CDX erro para {domain}: {e}")
        return []


def _is_relevant(row: dict) -> bool:
    """Filtra apenas HTML e PDF com status 200. (pré-filtrado na query CDX, mas por segurança)"""
    mime = (row.get("mime") or "").lower()
    status = str(row.get("status") or "")
    return status == "200" and ("html" in mime or "pdf" in mime)


def _archived_url(url: str, timestamp: str) -> str:
    return f"https://arquivo.pt/noFrame/replay/{timestamp}/{url}"


def discover_party(
    conn: sqlite3.Connection,
    party_id: str,
    domains: list[str],
    election_id: str,
    from_date: str,
    to_date: str,
    tier: int = 1,
) -> int:
    """Descobre páginas de um partido para uma eleição e guarda na DB. Devolve contagem inserida."""
    inserted = 0
    for domain in domains:
        log.info(f"  {party_id} | {domain} | {from_date}–{to_date}")
        rows = _cdx_query(domain, from_date, to_date)
        relevant = [r for r in rows if _is_relevant(r)]
        log.info(f"    {len(rows)} resultados → {len(relevant)} relevantes")

        for r in relevant:
            url = r["url"]
            ts = r["timestamp"]
            page_id = _page_id(url, ts)
            archived_url = _archived_url(url, ts)
            mime = r.get("mime", "")

            try:
                conn.execute(
                    """INSERT OR IGNORE INTO archived_pages
                       (id, url, archived_url, timestamp, party_id, election_id, tier, mime_type, status_code)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (page_id, url, archived_url, ts, party_id, election_id, tier, mime, 200),
                )
                inserted += conn.execute(
                    "SELECT changes()"
                ).fetchone()[0]
            except sqlite3.IntegrityError:
                pass

        time.sleep(0.3)  # ser gentil com a API

    conn.commit()
    return inserted


def discover_domain(
    conn: sqlite3.Connection,
    domain: str,
    label: str,
    election_id: str,
    from_date: str,
    to_date: str,
    tier: int,
    party_id: str | None = None,
) -> int:
    """Versão genérica para Tier 2 e Tier 3."""
    log.info(f"  {label} | {domain} | {from_date}–{to_date}")
    rows = _cdx_query(domain, from_date, to_date)
    relevant = [r for r in rows if _is_relevant(r)]
    log.info(f"    {len(rows)} resultados → {len(relevant)} relevantes")

    inserted = 0
    for r in relevant:
        url = r["url"]
        ts = r["timestamp"]
        page_id = _page_id(url, ts)
        archived_url = _archived_url(url, ts)
        mime = r.get("mimetype", "")

        try:
            conn.execute(
                """INSERT OR IGNORE INTO archived_pages
                   (id, url, archived_url, timestamp, party_id, election_id, tier, mime_type, status_code)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (page_id, url, archived_url, ts, party_id, election_id, tier, mime, 200),
            )
            inserted += conn.execute("SELECT changes()").fetchone()[0]
        except sqlite3.IntegrityError:
            pass

    conn.commit()
    time.sleep(0.3)
    return inserted


def run_discovery(
    tiers: list[int] | None = None,
    party_ids: list[str] | None = None,
    election_ids: list[str] | None = None,
) -> None:
    """
    Corre o discovery completo.

    Args:
        tiers: lista de tiers a correr (default: [1, 2, 3])
        party_ids: subset de partidos (default: todos)
        election_ids: subset de eleições (default: todas)
    """
    from backend.database import get_connection

    if tiers is None:
        tiers = [1, 2, 3]

    conn = get_connection()

    elections = json.loads((SEEDS_PATH / "elections.json").read_text())
    if election_ids:
        elections = [e for e in elections if e["id"] in election_ids]

    total = 0

    for election in elections:
        eid = election["id"]
        window = election["discovery_window"]
        from_date = window["from"]
        to_date = window["to"]

        log.info(f"\n=== {election['description']} ({from_date} – {to_date}) ===")

        # Tier 1 — partidos
        if 1 in tiers:
            for pid, domains in PARTY_DOMAINS.items():
                if party_ids and pid not in party_ids:
                    continue
                # verificar se o partido participou nesta eleição
                parties_data = json.loads((SEEDS_PATH / "parties.json").read_text())
                party = next((p for p in parties_data if p["id"] == pid), None)
                if party and eid not in party.get("elections", []):
                    continue
                n = discover_party(conn, pid, domains, eid, from_date, to_date, tier=1)
                total += n
                log.info(f"    → {n} páginas inseridas")

        # Tier 2 — governo
        if 2 in tiers:
            for domain in GOVERNMENT_DOMAINS:
                n = discover_domain(conn, domain, "GOV", eid, from_date, to_date, tier=2)
                total += n
                log.info(f"    → {n} páginas inseridas ({domain})")

        # Tier 3 — notícias
        if 3 in tiers:
            for label, domain in NEWS_DOMAINS.items():
                n = discover_domain(conn, domain, label, eid, from_date, to_date, tier=3)
                total += n
                log.info(f"    → {n} páginas inseridas ({domain})")

    conn.close()
    log.info(f"\nDiscovery concluído. Total inserido: {total} páginas.")


def stats(conn: sqlite3.Connection | None = None) -> None:
    """Imprime estatísticas do discovery."""
    from backend.database import get_connection

    close = False
    if conn is None:
        conn = get_connection()
        close = True

    rows = conn.execute("""
        SELECT party_id, election_id, tier, COUNT(*) as n
        FROM archived_pages
        GROUP BY party_id, election_id, tier
        ORDER BY election_id, party_id, tier
    """).fetchall()

    print(f"\n{'Partido':<10} {'Eleição':<12} {'Tier':<6} {'Páginas'}")
    print("-" * 40)
    for r in rows:
        print(f"{r['party_id'] or 'GOV/NEWS':<10} {r['election_id'] or '-':<12} {r['tier']:<6} {r['n']}")

    total = conn.execute("SELECT COUNT(*) FROM archived_pages").fetchone()[0]
    print(f"\nTotal: {total} páginas arquivadas")

    if close:
        conn.close()


if __name__ == "__main__":
    import argparse
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    parser = argparse.ArgumentParser(description="Discovery de páginas arquivadas")
    parser.add_argument("--tiers", nargs="+", type=int, default=[1, 2, 3], help="Tiers a correr (1 2 3)")
    parser.add_argument("--parties", nargs="+", help="Subset de partidos (PS PSD BE ...)")
    parser.add_argument("--elections", nargs="+", help="Subset de eleições (leg_2005 leg_2009 ...)")
    parser.add_argument("--stats", action="store_true", help="Mostrar estatísticas e sair")
    args = parser.parse_args()

    from backend.database import get_connection, init_db

    init_db()

    if args.stats:
        stats()
    else:
        run_discovery(
            tiers=args.tiers,
            party_ids=args.parties,
            election_ids=args.elections,
        )
        stats()
