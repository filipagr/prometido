"""
pipeline/fetch.py

Para cada página arquivada na DB (sem raw_text), faz fetch do HTML
via arquivo.pt/noFrame/replay e extrai texto limpo com trafilatura.

PDFs são ignorados nesta fase — extraídos depois com pdfminer se necessário.
"""

import logging
import re
import sqlite3
import time
from pathlib import Path

import httpx
import trafilatura

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

# Páginas que não vale a pena fazer fetch (recursos, tracking, etc.)
SKIP_PATTERNS = re.compile(
    r"\.(gif|png|jpg|jpeg|css|js|ico|swf|woff|woff2|ttf|eot|svg|zip|rar|exe|mp3|mp4|avi)$",
    re.IGNORECASE,
)

# Texto mínimo para considerar a página útil
MIN_TEXT_LENGTH = 100


def _should_skip(url: str, mime: str) -> bool:
    if SKIP_PATTERNS.search(url):
        return True
    mime = (mime or "").lower()
    # PDFs tratados separadamente
    if "pdf" in mime:
        return True
    return False


def _clean_text(raw: str | bytes) -> str | None:
    """Usa trafilatura para extrair texto relevante do HTML."""
    text = trafilatura.extract(
        raw,
        include_comments=False,
        include_tables=True,
        no_fallback=False,
    )
    if not text or len(text.strip()) < MIN_TEXT_LENGTH:
        return None
    # normalizar espaços e linhas
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)
    return text.strip()


def fetch_pages(
    conn: sqlite3.Connection,
    batch_size: int = 50,
    max_pages: int | None = None,
    party_id: str | None = None,
    election_id: str | None = None,
    tier: int | None = None,
    timeout: int = 30,
    delay: float = 0.5,
) -> dict:
    """
    Faz fetch e extrai texto das páginas archived_pages sem raw_text.

    Args:
        conn: conexão SQLite
        batch_size: páginas por batch (para commits intermédios)
        max_pages: limite total (None = sem limite)
        party_id: filtrar por partido
        election_id: filtrar por eleição
        tier: filtrar por tier
        timeout: timeout HTTP em segundos
        delay: pausa entre requests (ser gentil com o arquivo)

    Returns:
        dict com stats: fetched, skipped, failed, empty
    """
    where_clauses = ["raw_text IS NULL", "mime_type NOT LIKE '%pdf%'"]
    params: list = []

    if party_id:
        where_clauses.append("party_id = ?")
        params.append(party_id)
    if election_id:
        where_clauses.append("election_id = ?")
        params.append(election_id)
    if tier is not None:
        where_clauses.append("tier = ?")
        params.append(tier)

    where = " AND ".join(where_clauses)
    limit_clause = f"LIMIT {max_pages}" if max_pages else ""

    rows = conn.execute(
        f"SELECT id, url, archived_url, mime_type FROM archived_pages WHERE {where} {limit_clause}",
        params,
    ).fetchall()

    total = len(rows)
    log.info(f"Páginas a fazer fetch: {total}")

    stats = {"fetched": 0, "skipped": 0, "failed": 0, "empty": 0}
    client = httpx.Client(timeout=timeout, follow_redirects=True)

    try:
        for i, row in enumerate(rows):
            page_id = row["id"]
            url = row["url"]
            archived_url = row["archived_url"]
            mime = row["mime_type"] or ""

            if _should_skip(url, mime):
                conn.execute(
                    "UPDATE archived_pages SET raw_text = '' WHERE id = ?", (page_id,)
                )
                stats["skipped"] += 1
                continue

            try:
                resp = client.get(archived_url)
                resp.raise_for_status()

                # trafilatura precisa de HTML — verificar content-type da resposta
                ct = resp.headers.get("content-type", "").lower()
                if "html" not in ct:
                    conn.execute(
                        "UPDATE archived_pages SET raw_text = '' WHERE id = ?", (page_id,)
                    )
                    stats["skipped"] += 1
                    continue

                # passar bytes ao trafilatura — detecta encoding via meta charset
                text = _clean_text(resp.content)
                if text:
                    conn.execute(
                        "UPDATE archived_pages SET raw_text = ? WHERE id = ?",
                        (text, page_id),
                    )
                    stats["fetched"] += 1
                else:
                    conn.execute(
                        "UPDATE archived_pages SET raw_text = '' WHERE id = ?", (page_id,)
                    )
                    stats["empty"] += 1

            except httpx.HTTPStatusError as e:
                log.debug(f"HTTP {e.response.status_code}: {archived_url}")
                stats["failed"] += 1
            except Exception as e:
                log.debug(f"Erro: {archived_url} — {e}")
                stats["failed"] += 1

            # commit por batch
            if (i + 1) % batch_size == 0:
                conn.commit()
                log.info(
                    f"  {i+1}/{total} — fetched:{stats['fetched']} "
                    f"skip:{stats['skipped']} fail:{stats['failed']} empty:{stats['empty']}"
                )

            time.sleep(delay)

    finally:
        client.close()
        conn.commit()

    log.info(
        f"Fetch concluído: {stats['fetched']} com texto, "
        f"{stats['skipped']} skip, {stats['failed']} falhas, {stats['empty']} vazios"
    )
    return stats


def fetch_pdfs(
    conn: sqlite3.Connection,
    max_pages: int | None = None,
    party_id: str | None = None,
    election_id: str | None = None,
    timeout: int = 60,
    delay: float = 1.0,
) -> dict:
    """
    Faz fetch de PDFs e extrai texto com pdfminer.
    Apenas PDFs — HTML é tratado em fetch_pages().
    """
    try:
        from pdfminer.high_level import extract_text as pdf_extract
        from io import BytesIO
    except ImportError:
        log.warning("pdfminer não instalado — a saltar PDFs. pip install pdfminer.six")
        return {"fetched": 0, "skipped": 0, "failed": 0}

    where_clauses = ["raw_text IS NULL", "mime_type LIKE '%pdf%'"]
    params: list = []
    if party_id:
        where_clauses.append("party_id = ?")
        params.append(party_id)
    if election_id:
        where_clauses.append("election_id = ?")
        params.append(election_id)

    where = " AND ".join(where_clauses)
    limit_clause = f"LIMIT {max_pages}" if max_pages else ""

    rows = conn.execute(
        f"SELECT id, archived_url FROM archived_pages WHERE {where} {limit_clause}",
        params,
    ).fetchall()

    log.info(f"PDFs a processar: {len(rows)}")
    stats = {"fetched": 0, "skipped": 0, "failed": 0}
    client = httpx.Client(timeout=timeout, follow_redirects=True)

    try:
        for row in rows:
            page_id = row["id"]
            archived_url = row["archived_url"]
            try:
                resp = client.get(archived_url)
                resp.raise_for_status()
                text = pdf_extract(BytesIO(resp.content))
                text = text.strip() if text else ""
                if len(text) >= MIN_TEXT_LENGTH:
                    conn.execute(
                        "UPDATE archived_pages SET raw_text = ? WHERE id = ?",
                        (text, page_id),
                    )
                    stats["fetched"] += 1
                else:
                    conn.execute(
                        "UPDATE archived_pages SET raw_text = '' WHERE id = ?", (page_id,)
                    )
                    stats["skipped"] += 1
            except Exception as e:
                log.debug(f"PDF erro: {archived_url} — {e}")
                stats["failed"] += 1
            time.sleep(delay)
    finally:
        client.close()
        conn.commit()

    log.info(f"PDFs: {stats['fetched']} com texto, {stats['skipped']} skip, {stats['failed']} falhas")
    return stats


if __name__ == "__main__":
    import argparse
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    parser = argparse.ArgumentParser(description="Fetch de páginas arquivadas")
    parser.add_argument("--party", help="Filtrar por partido (PS, PSD, ...)")
    parser.add_argument("--election", help="Filtrar por eleição (leg_2005, ...)")
    parser.add_argument("--tier", type=int, help="Filtrar por tier (1, 2, 3)")
    parser.add_argument("--max", type=int, help="Máximo de páginas")
    parser.add_argument("--pdfs", action="store_true", help="Processar PDFs (requer pdfminer.six)")
    parser.add_argument("--delay", type=float, default=0.5, help="Pausa entre requests (segundos)")
    args = parser.parse_args()

    from backend.database import get_connection

    conn = get_connection()

    if args.pdfs:
        fetch_pdfs(conn, max_pages=args.max, party_id=args.party, election_id=args.election)
    else:
        fetch_pages(
            conn,
            max_pages=args.max,
            party_id=args.party,
            election_id=args.election,
            tier=args.tier,
            delay=args.delay,
        )

    conn.close()
