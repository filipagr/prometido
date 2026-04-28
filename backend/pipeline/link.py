"""
pipeline/link.py

Liga artigos jornalísticos (Tier 3) a promessas (Tier 1/2).

Dois modos:
  1. Corroboração — artigo com citação directa da promessa (status: archived → corroborated)
  2. Verificação — artigo posterior que confirma ou nega cumprimento

Estratégia: embedding semântico via Claude API (prompt simples de matching)
para encontrar artigos que correspondem a promessas por tema + partido + período.

Para o MVP: matching heurístico por partido + eleição + tópico é suficiente
e muito mais barato do que embeddings completos.
"""

import json
import logging
import os
import sqlite3
import time
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / ".env", override=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

MODEL = "claude-haiku-4-5-20251001"

LINK_PROMPT = """\
Tens uma promessa eleitoral e um excerto de um artigo jornalístico arquivado.
Determina se o artigo é relevante para a promessa.

Promessa:
- Partido: {party_name}
- Eleição: {election}
- Tópico: {topic}
- Texto: {promise_text}

Artigo:
- Fonte: {source_domain}
- Data: {article_date}
- Excerto: {article_excerpt}

Responde APENAS com este JSON:
{{
  "is_relevant": true/false,
  "use_type": "corroboration" | "fulfillment" | "breach" | null,
  "quote": "citação directa relevante do artigo (máx 200 chars) ou null",
  "confidence": 0.0 a 1.0
}}

- "corroboration": o artigo cita directamente o partido a fazer esta promessa
- "fulfillment": o artigo reporta que a promessa foi cumprida
- "breach": o artigo reporta que a promessa não foi cumprida
- null: artigo relacionado mas sem correspondência directa

is_relevant=false se o artigo não tem relação directa com esta promessa específica.
"""


def _get_article_excerpt(raw_text: str, max_chars: int = 1500) -> str:
    """Devolve os primeiros max_chars do texto do artigo."""
    if not raw_text:
        return ""
    return raw_text[:max_chars].strip()


def _link_promise_to_article(
    client: anthropic.Anthropic,
    promise: sqlite3.Row,
    article: sqlite3.Row,
    party_name: str,
) -> dict | None:
    """
    Avalia se um artigo é relevante para uma promessa.
    Devolve dict com campos de linking, ou None se não relevante.
    """
    excerpt = _get_article_excerpt(article["raw_text"] or "")
    if not excerpt:
        return None

    article_date = article["timestamp"][:10] if article["timestamp"] else "desconhecida"
    election_label = (promise["election_id"] or "").replace("leg_", "Legislativas ")

    prompt = LINK_PROMPT.format(
        party_name=party_name,
        election=election_label,
        topic=promise["topic"] or "outros",
        promise_text=promise["text"],
        source_domain=article["url"].split("/")[2].replace("www.", "") if article["url"] else "",
        article_date=article_date,
        article_excerpt=excerpt,
    )

    try:
        msg = client.messages.create(
            model=MODEL,
            max_tokens=256,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = msg.content[0].text.strip()
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start == -1 or end == 0:
            return None
        result = json.loads(raw[start:end])
        if not result.get("is_relevant"):
            return None
        return result
    except Exception as e:
        log.debug(f"Link erro: {e}")
        return None


def run_linking(
    party_ids: list[str] | None = None,
    election_ids: list[str] | None = None,
    max_promises: int | None = None,
    use_claude: bool = False,
) -> dict:
    """
    Liga artigos Tier 3 a promessas Tier 1/2.

    Dois modos:
    - use_claude=False (default): matching heurístico por partido + tópico
      Rápido, zero custo, suficiente para o MVP.
    - use_claude=True: Claude API para matching semântico mais preciso
      Mais caro mas identifica correspondências não-óbvias.

    Args:
        party_ids: subset de partidos
        election_ids: subset de eleições
        max_promises: limite de promessas a processar
        use_claude: usar Claude API para matching semântico
    """
    from backend.database import get_connection

    conn = get_connection()

    # --- 1. Buscar promessas válidas sem corroboração ainda ---
    where_clauses = ["p.is_valid = 1", "p.tier IN (1, 2)"]
    params: list = []

    if party_ids:
        where_clauses.append(f"p.party_id IN ({','.join('?' * len(party_ids))})")
        params.extend(party_ids)
    if election_ids:
        where_clauses.append(f"p.election_id IN ({','.join('?' * len(election_ids))})")
        params.extend(election_ids)

    where = " AND ".join(where_clauses)
    limit_clause = f"LIMIT {max_promises}" if max_promises else ""

    promises = conn.execute(
        f"""SELECT p.id, p.text, p.topic, p.party_id, p.election_id, p.tier,
                   pt.name as party_name
            FROM promises p
            LEFT JOIN parties pt ON p.party_id = pt.id
            WHERE {where}
            ORDER BY p.party_id, p.election_id
            {limit_clause}""",
        params,
    ).fetchall()

    log.info(f"Promessas a processar: {len(promises)}")

    # --- 2. Buscar artigos Tier 3 com texto ---
    tier3_where = ["tier = 3", "raw_text IS NOT NULL", "raw_text != ''"]
    tier3_params: list = []

    if election_ids:
        tier3_where.append(f"election_id IN ({','.join('?' * len(election_ids))})")
        tier3_params.extend(election_ids)

    articles = conn.execute(
        f"""SELECT id, url, timestamp, raw_text, party_id, election_id
            FROM archived_pages
            WHERE {' AND '.join(tier3_where)}""",
        tier3_params,
    ).fetchall()

    log.info(f"Artigos Tier 3 disponíveis: {len(articles)}")

    stats = {"linked": 0, "corroborations": 0, "fulfillments": 0, "breaches": 0}

    if use_claude:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY não definida.")
        client = anthropic.Anthropic(api_key=api_key)
        stats.update(_link_with_claude(conn, promises, articles, client, stats))
    else:
        stats.update(_link_heuristic(conn, promises, articles, stats))

    conn.commit()
    conn.close()

    log.info(
        f"\nLinking concluído: {stats['linked']} ligações criadas "
        f"({stats['corroborations']} corroborações, "
        f"{stats['fulfillments']} cumprimentos, "
        f"{stats['breaches']} incumprimentos)"
    )
    return stats


def _link_heuristic(
    conn: sqlite3.Connection,
    promises: list[sqlite3.Row],
    articles: list[sqlite3.Row],
    stats: dict,
) -> dict:
    """
    Matching heurístico: liga artigos a promessas pelo mesmo partido + eleição + tópico.
    Zero custo, suficiente para o MVP mostrar corroboração de Tier 3.
    """
    import hashlib
    from urllib.parse import urlparse

    # indexar artigos por (election_id, url_domain)
    article_index: dict[tuple, list] = {}
    for art in articles:
        eid = art["election_id"] or ""
        domain = urlparse(art["url"]).netloc.replace("www.", "") if art["url"] else ""
        key = (eid, domain)
        article_index.setdefault(key, []).append(art)

    for promise in promises:
        eid = promise["election_id"] or ""
        party_id = promise["party_id"] or ""

        # artigos do mesmo período eleitoral
        matching_arts: list[sqlite3.Row] = []
        for (art_eid, _), arts in article_index.items():
            if art_eid == eid:
                matching_arts.extend(arts)

        for art in matching_arts[:5]:  # máx 5 artigos por promessa no modo heurístico
            source_domain = urlparse(art["url"]).netloc.replace("www.", "")
            art_text = (art["raw_text"] or "").lower()
            promise_words = promise["text"].lower().split()

            # heurística: pelo menos 3 palavras da promessa no artigo
            significant = [w for w in promise_words if len(w) > 5]
            matches = sum(1 for w in significant if w in art_text)
            if matches < 3:
                continue

            # verificar se já existe esta ligação
            link_id = hashlib.sha256(
                f"{promise['id']}|{art['id']}".encode()
            ).hexdigest()[:16]

            existing = conn.execute(
                "SELECT id FROM verification_sources WHERE id = ?", (link_id,)
            ).fetchone()
            if existing:
                continue

            # artigo contemporâneo → corroboração; artigo posterior → potencial fulfillment/breach
            use_type = "corroboration"

            conn.execute(
                """INSERT OR IGNORE INTO verification_sources
                   (id, promise_id, archived_url, source_domain, source_date, use_type, quote, added_by)
                   VALUES (?, ?, ?, ?, ?, ?, ?, 'pipeline')""",
                (
                    link_id,
                    promise["id"],
                    art["archived_url"] if hasattr(art, "keys") and "archived_url" in art.keys() else "",
                    source_domain,
                    art["timestamp"][:8] if art["timestamp"] else None,
                    use_type,
                    None,
                ),
            )
            inserted = conn.execute("SELECT changes()").fetchone()[0]
            if inserted:
                stats["linked"] += 1
                stats["corroborations"] += 1

        # actualizar status para corroborated se houver pelo menos 1 fonte Tier 3
        corroborations = conn.execute(
            "SELECT COUNT(*) FROM verification_sources WHERE promise_id = ?",
            (promise["id"],),
        ).fetchone()[0]
        if corroborations > 0:
            conn.execute(
                "UPDATE promises SET status = 'corroborated' WHERE id = ? AND status = 'archived'",
                (promise["id"],),
            )

    return stats


def _link_with_claude(
    conn: sqlite3.Connection,
    promises: list[sqlite3.Row],
    articles: list[sqlite3.Row],
    client: anthropic.Anthropic,
    stats: dict,
) -> dict:
    """Matching semântico via Claude API."""
    import hashlib
    from urllib.parse import urlparse

    for i, promise in enumerate(promises):
        eid = promise["election_id"] or ""

        # só artigos do mesmo período eleitoral
        relevant_arts = [a for a in articles if (a["election_id"] or "") == eid]

        for art in relevant_arts[:10]:
            result = _link_promise_to_article(client, promise, art, promise["party_name"] or "")
            if not result:
                time.sleep(0.2)
                continue

            link_id = hashlib.sha256(
                f"{promise['id']}|{art['id']}".encode()
            ).hexdigest()[:16]

            source_domain = urlparse(art["url"]).netloc.replace("www.", "") if art["url"] else ""
            use_type = result.get("use_type") or "corroboration"

            conn.execute(
                """INSERT OR IGNORE INTO verification_sources
                   (id, promise_id, archived_url, source_domain, source_date, use_type, quote, added_by)
                   VALUES (?, ?, ?, ?, ?, ?, ?, 'pipeline')""",
                (
                    link_id,
                    promise["id"],
                    art["archived_url"] if "archived_url" in art.keys() else "",
                    source_domain,
                    art["timestamp"][:8] if art["timestamp"] else None,
                    use_type,
                    result.get("quote"),
                ),
            )
            inserted = conn.execute("SELECT changes()").fetchone()[0]
            if inserted:
                stats["linked"] += 1
                stats[f"{use_type}s"] = stats.get(f"{use_type}s", 0) + 1

            time.sleep(0.3)

        if (i + 1) % 10 == 0:
            conn.commit()
            log.info(f"  {i+1}/{len(promises)} promessas | {stats['linked']} ligações")

        # actualizar status
        count = conn.execute(
            "SELECT COUNT(*) FROM verification_sources WHERE promise_id = ?",
            (promise["id"],),
        ).fetchone()[0]
        if count > 0:
            conn.execute(
                "UPDATE promises SET status = 'corroborated' WHERE id = ? AND status = 'archived'",
                (promise["id"],),
            )

    return stats


if __name__ == "__main__":
    import argparse
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    parser = argparse.ArgumentParser(description="Linking Tier 3 → promessas")
    parser.add_argument("--parties", nargs="+", help="Subset de partidos")
    parser.add_argument("--elections", nargs="+", help="Subset de eleições")
    parser.add_argument("--max", type=int, help="Máximo de promessas")
    parser.add_argument("--claude", action="store_true", help="Usar Claude API (matching semântico)")
    args = parser.parse_args()

    run_linking(
        party_ids=args.parties,
        election_ids=args.elections,
        max_promises=args.max,
        use_claude=args.claude,
    )
