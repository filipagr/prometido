"""
pipeline/extract.py

Passo 1 do pipeline: extracção de promessas de páginas arquivadas (Tier 1 e 2).
Usa Claude API com o modelo claude-sonnet-4-6.

Para cada página com raw_text, extrai promessas candidatas e guarda na tabela promises.
Páginas já processadas são saltadas (idempotente).
"""

import hashlib
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

MODEL = "claude-sonnet-4-6"

# Páginas muito longas são truncadas — Claude tem limite de contexto e programas
# eleitorais podem ter 300K chars. Estratégia: dividir em chunks de 8000 chars
# com sobreposição de 500 chars para não perder promessas no limite.
MAX_CHUNK_CHARS = 8_000
CHUNK_OVERLAP = 500

TOPICS = [
    "habitação", "saúde", "educação", "economia", "emprego",
    "ambiente", "segurança", "justiça", "transportes", "tecnologia",
    "agricultura", "cultura", "desporto", "administração pública", "outros",
]

EXTRACTION_PROMPT = """\
És um analista político especializado em programas eleitorais portugueses.

Contexto:
- Partido: {party_name}
- Data da página: {page_date}
- Eleição: {election}
- Tipo de fonte: {tier_desc}

Texto a analisar:
{page_text}

Tarefa:
Identifica TODAS as promessas eleitorais concretas e verificáveis neste texto.

Definição operacional de promessa:
Uma declaração prospetiva de uma ação ou resultado específico que pode ser verificado.
Inclui: "vamos criar", "iremos implementar", "comprometemo-nos a", "será criado", etc.
Exclui: retórica vaga ("queremos um Portugal melhor"), diagnósticos, críticas ao adversário.

Para cada promessa encontrada, devolve um objecto JSON com estes campos:
- "text": a promessa nas palavras exactas do documento (máx. 300 chars)
- "context": frase anterior e/ou seguinte para contextualizar (máx. 200 chars)
- "topic": um de {topics}
- "confidence": float 0.0 a 1.0 (certeza de que é uma promessa concreta e verificável)
- "is_direct_quote": true se são palavras literais do partido, false se paráfrase

Devolve APENAS um JSON array. Se não houver promessas concretas, devolve [].
Não incluas texto fora do JSON.
"""

EXTRACTION_PROMPT_TIER3 = """\
És um analista político especializado em cobertura jornalística de eleições portuguesas.

Contexto:
- Fonte: {source_domain}
- Data do artigo: {page_date}
- Eleição: {election}

Texto do artigo:
{page_text}

Tarefa:
Identifica citações directas de políticos a fazer promessas eleitorais e referências
a cumprimento/incumprimento de promessas anteriores.

Inclui APENAS:
1. Citações directas entre aspas onde um político promete algo concreto
2. Declarações que confirmam ou negam que uma promessa foi cumprida

Exclui:
- Paráfrases jornalísticas de posições (ex: "o partido defende...")
- Análises e opiniões do jornalista
- Promessas vagas sem acção específica

Para cada resultado, devolve um objecto JSON com:
- "text": a citação ou declaração exacta (máx. 300 chars)
- "context": contexto do artigo (máx. 200 chars)
- "topic": um de {topics}
- "confidence": float 0.0 a 1.0
- "is_direct_quote": true (só incluir citações directas)
- "party_mentioned": nome do partido ou político mencionado (ou null)
- "use_type": "corroboration" (promessa) ou "fulfillment" (cumprida) ou "breach" (não cumprida)

Devolve APENAS um JSON array. Se não houver citações relevantes, devolve [].
"""


def _promise_id(page_id: str, text: str) -> str:
    return hashlib.sha256(f"{page_id}|{text}".encode()).hexdigest()[:16]


def _chunk_text(text: str, max_chars: int = MAX_CHUNK_CHARS, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Divide texto em chunks com sobreposição para não perder promessas no limite."""
    if len(text) <= max_chars:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars
        # tentar cortar num parágrafo ou frase
        if end < len(text):
            cut = text.rfind("\n\n", start, end)
            if cut == -1:
                cut = text.rfind(". ", start, end)
            if cut != -1:
                end = cut + 1
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


def _extract_from_chunk(
    client: anthropic.Anthropic,
    chunk: str,
    party_name: str,
    page_date: str,
    election: str,
    tier: int,
    source_domain: str | None = None,
) -> list[dict]:
    """Chama Claude API para extrair promessas de um chunk de texto."""
    tier_desc = {
        1: "site oficial do partido (fonte primária directa)",
        2: "programa de governo oficial",
        3: f"artigo jornalístico ({source_domain or 'notícias'})",
    }.get(tier, "fonte desconhecida")

    if tier == 3:
        prompt = EXTRACTION_PROMPT_TIER3.format(
            source_domain=source_domain or "desconhecido",
            page_date=page_date,
            election=election,
            page_text=chunk,
            topics=", ".join(TOPICS),
        )
    else:
        prompt = EXTRACTION_PROMPT.format(
            party_name=party_name,
            page_date=page_date,
            election=election,
            tier_desc=tier_desc,
            page_text=chunk,
            topics=", ".join(TOPICS),
        )

    try:
        msg = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = msg.content[0].text.strip()

        # extrair o JSON mesmo que haja texto à volta (por segurança)
        start = raw.find("[")
        end = raw.rfind("]") + 1
        if start == -1 or end == 0:
            return []
        return json.loads(raw[start:end])
    except json.JSONDecodeError as e:
        log.warning(f"JSON inválido da Claude API: {e}")
        return []
    except anthropic.APIError as e:
        log.error(f"Claude API erro: {e}")
        raise


def extract_page(
    conn: sqlite3.Connection,
    client: anthropic.Anthropic,
    page: sqlite3.Row,
    dry_run: bool = False,
) -> int:
    """
    Extrai promessas de uma página e guarda na DB.
    Devolve número de promessas inseridas.
    """
    page_id = page["id"]
    raw_text = page["raw_text"]
    party_id = page["party_id"] or ""
    election_id = page["election_id"] or ""
    tier = page["tier"]
    timestamp = page["timestamp"]
    url = page["url"]

    if not raw_text or len(raw_text.strip()) < 100:
        return 0

    # data legível a partir do timestamp YYYYMMDDHHMMSS
    page_date = f"{timestamp[:4]}-{timestamp[4:6]}-{timestamp[6:8]}" if timestamp else "desconhecida"
    election_label = election_id.replace("leg_", "Legislativas ") if election_id else "desconhecida"

    # nome do partido
    party_row = conn.execute("SELECT name FROM parties WHERE id = ?", (party_id,)).fetchone()
    party_name = party_row["name"] if party_row else party_id

    # domínio da fonte (para Tier 3)
    source_domain = None
    if tier == 3:
        from urllib.parse import urlparse
        source_domain = urlparse(url).netloc.replace("www.", "")

    chunks = _chunk_text(raw_text)
    log.debug(f"  {party_id}/{election_id} | {len(raw_text)} chars → {len(chunks)} chunks")

    all_promises: list[dict] = []
    seen_texts: set[str] = set()

    for chunk in chunks:
        promises = _extract_from_chunk(
            client, chunk, party_name, page_date, election_label, tier, source_domain
        )
        # deduplicar por texto
        for p in promises:
            text = (p.get("text") or "").strip()
            if text and text not in seen_texts:
                seen_texts.add(text)
                all_promises.append(p)
        time.sleep(0.5)  # rate limiting

    if dry_run:
        log.info(f"  [DRY RUN] {len(all_promises)} promessas encontradas em {url}")
        for p in all_promises[:3]:
            log.info(f"    [{p.get('topic')}] {p.get('text', '')[:100]}")
        return len(all_promises)

    inserted = 0
    for p in all_promises:
        text = (p.get("text") or "").strip()
        if not text:
            continue
        promise_id = _promise_id(page_id, text)
        confidence = float(p.get("confidence", 0.5))

        try:
            conn.execute(
                """INSERT OR IGNORE INTO promises
                   (id, page_id, party_id, election_id, text, context, topic, tier,
                    extraction_confidence, extraction_model, is_valid, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, 'archived')""",
                (
                    promise_id,
                    page_id,
                    party_id,
                    election_id,
                    text,
                    p.get("context"),
                    p.get("topic", "outros"),
                    tier,
                    confidence,
                    MODEL,
                ),
            )
            inserted += conn.execute("SELECT changes()").fetchone()[0]
        except sqlite3.IntegrityError:
            pass

    # marcar a página como processada (para idempotência)
    conn.execute(
        "UPDATE archived_pages SET crawled_at = crawled_at WHERE id = ?", (page_id,)
    )
    conn.commit()
    return inserted


def run_extraction(
    party_ids: list[str] | None = None,
    election_ids: list[str] | None = None,
    tiers: list[int] | None = None,
    max_pages: int | None = None,
    dry_run: bool = False,
    skip_extracted: bool = True,
) -> dict:
    """
    Corre a extracção em todas as páginas com texto, sem promessas ainda extraídas.

    Args:
        party_ids: subset de partidos
        election_ids: subset de eleições
        tiers: subset de tiers (default [1, 2])
        max_pages: limite de páginas
        dry_run: não escreve na DB, só mostra o que encontraria
        skip_extracted: salta páginas cujo page_id já tem promessas na DB
    """
    from backend.database import get_connection

    if tiers is None:
        tiers = [1, 2]

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY não definida. Adicionar ao ficheiro .env")

    client = anthropic.Anthropic(api_key=api_key)
    conn = get_connection()

    where_clauses = [
        "raw_text IS NOT NULL",
        "raw_text != ''",
        f"tier IN ({','.join('?' * len(tiers))})",
    ]
    params: list = list(tiers)

    if party_ids:
        where_clauses.append(f"party_id IN ({','.join('?' * len(party_ids))})")
        params.extend(party_ids)
    if election_ids:
        where_clauses.append(f"election_id IN ({','.join('?' * len(election_ids))})")
        params.extend(election_ids)
    if skip_extracted:
        where_clauses.append(
            "id NOT IN (SELECT DISTINCT page_id FROM promises WHERE page_id IS NOT NULL)"
        )

    where = " AND ".join(where_clauses)
    limit_clause = f"LIMIT {max_pages}" if max_pages else ""

    pages = conn.execute(
        f"""SELECT id, url, archived_url, timestamp, party_id, election_id,
                   tier, raw_text, mime_type
            FROM archived_pages
            WHERE {where}
            ORDER BY party_id, election_id, timestamp
            {limit_clause}""",
        params,
    ).fetchall()

    total_pages = len(pages)
    log.info(f"Páginas a processar: {total_pages}")

    stats = {"pages_processed": 0, "promises_extracted": 0, "pages_skipped": 0}

    for i, page in enumerate(pages):
        try:
            n = extract_page(conn, client, page, dry_run=dry_run)
            stats["promises_extracted"] += n
            stats["pages_processed"] += 1
            if (i + 1) % 10 == 0:
                log.info(
                    f"  {i+1}/{total_pages} páginas | "
                    f"{stats['promises_extracted']} promessas até agora"
                )
        except anthropic.RateLimitError:
            log.warning("Rate limit atingido — a aguardar 60s")
            time.sleep(60)
        except anthropic.APIError as e:
            log.error(f"API erro em {page['url']}: {e}")
            stats["pages_skipped"] += 1

    conn.close()
    log.info(
        f"\nExtracção concluída: {stats['pages_processed']} páginas, "
        f"{stats['promises_extracted']} promessas extraídas, "
        f"{stats['pages_skipped']} páginas com erro"
    )
    return stats


if __name__ == "__main__":
    import argparse
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    parser = argparse.ArgumentParser(description="Extracção de promessas com Claude API")
    parser.add_argument("--parties", nargs="+", help="Subset de partidos (PS PSD ...)")
    parser.add_argument("--elections", nargs="+", help="Subset de eleições (leg_2005 ...)")
    parser.add_argument("--tiers", nargs="+", type=int, default=[1, 2], help="Tiers (1 2)")
    parser.add_argument("--max", type=int, help="Máximo de páginas a processar")
    parser.add_argument("--dry-run", action="store_true", help="Não escrever na DB")
    parser.add_argument("--stats", action="store_true", help="Mostrar stats de promessas e sair")
    args = parser.parse_args()

    from backend.database import get_connection

    if args.stats:
        conn = get_connection()
        rows = conn.execute("""
            SELECT party_id, election_id, topic, COUNT(*) as n
            FROM promises
            GROUP BY party_id, election_id, topic
            ORDER BY party_id, election_id, n DESC
        """).fetchall()
        total = conn.execute("SELECT COUNT(*) FROM promises").fetchone()[0]
        valid = conn.execute("SELECT COUNT(*) FROM promises WHERE is_valid = 1").fetchone()[0]
        review = conn.execute("SELECT COUNT(*) FROM promises WHERE needs_human_review = 1").fetchone()[0]
        print(f"\nTotal promessas: {total} | válidas: {valid} | para revisão: {review}\n")
        print(f"{'Partido':<10} {'Eleição':<12} {'Tópico':<25} {'N'}")
        print("-" * 55)
        for r in rows:
            print(f"{r['party_id'] or '-':<10} {r['election_id'] or '-':<12} {r['topic'] or '-':<25} {r['n']}")
        conn.close()
    else:
        run_extraction(
            party_ids=args.parties,
            election_ids=args.elections,
            tiers=args.tiers,
            max_pages=args.max,
            dry_run=args.dry_run,
        )
