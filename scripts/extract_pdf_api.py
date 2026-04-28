"""
scripts/extract_pdf_api.py

Extrai promessas de PDFs e TXTs usando a Claude API com suporte nativo a documentos.
Processa todos os programas em data/programs/ que ainda não têm promessas na DB.

Uso:
    python3 scripts/extract_pdf_api.py
    python3 scripts/extract_pdf_api.py --year 2019
    python3 scripts/extract_pdf_api.py --year 2019 --party PS
    python3 scripts/extract_pdf_api.py --dry-run
    python3 scripts/extract_pdf_api.py --list   # mostra o que falta processar
"""

import argparse
import base64
import hashlib
import json
import logging
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import anthropic
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env", override=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

MODEL = "claude-sonnet-4-6"

# PDFs acima deste limite são enviados como texto extraído (pypdf) em vez de base64
PDF_NATIVE_MAX_BYTES = 10 * 1024 * 1024  # 10MB

# Chunks de texto para PDFs grandes
TEXT_CHUNK_CHARS = 60_000
TEXT_CHUNK_OVERLAP = 1_000

# Mapeamento de prefixo de ficheiro → party_id na DB
PARTY_MAP = {
    "PS": "PS",
    "PSD": "PSD",
    "AD": "PSD",       # AD = coligação liderada pelo PSD
    "PaF": "PSD",      # Portugal à Frente
    "BE": "BE",
    "PCP": "PCP",
    "CDU": "PCP",      # CDU = coligação liderada pelo PCP
    "CDS": "CDS",
    "IL": "IL",
    "CH": "Chega",
    "Chega": "Chega",
    "LV": "Livre",
    "Livre": "Livre",
    "PAN": "PAN",
}

PARTY_NAMES = {
    "PS": "Partido Socialista",
    "PSD": "Partido Social Democrata",
    "BE": "Bloco de Esquerda",
    "PCP": "Partido Comunista Português (CDU)",
    "CDS": "CDS – Partido Popular",
    "IL": "Iniciativa Liberal",
    "Chega": "Chega",
    "Livre": "Livre",
    "PAN": "Pessoas-Animais-Natureza",
}

TOPICS = [
    "habitação", "saúde", "educação", "economia", "emprego",
    "ambiente", "segurança", "justiça", "transportes", "tecnologia",
    "agricultura", "cultura", "desporto", "administração pública", "outros",
]

EXTRACTION_PROMPT = """\
És um analista político especializado em programas eleitorais portugueses.

Contexto:
- Partido: {party_name} ({party_id})
- Eleição: Legislativas {year}
- Tipo de fonte: programa eleitoral oficial (Tier 2)

Tarefa:
Identifica TODAS as promessas eleitorais concretas e verificáveis neste programa.

Para ser uma promessa válida, tem de ter pelo menos um destes elementos:
A) Um número ou valor concreto (ex: "aumentar para X%", "criar Y postos de trabalho", "investir Z milhões")
B) Um prazo específico (ex: "até 2013", "nos primeiros 100 dias", "durante a legislatura")
C) Uma acção singular e identificável (ex: "criar o programa X", "eliminar a taxa Y", "construir Z hospitais")
D) Uma lei, instituição ou medida nomeada concretamente

Excluir:
- Declarações de intenção vagas: "vamos apoiar", "iremos promover"
- Valores genéricos: "acreditamos em", "defendemos"
- Diagnósticos ou críticas sem proposta concreta
- Retórica política: "um Portugal melhor", "mais justo"

Para cada promessa, devolve um objecto JSON com:
- "text": a promessa nas palavras exactas do documento (máx. 300 chars)
- "context": frase anterior/seguinte para contextualizar (máx. 200 chars)
- "topic": um de {topics}
- "confidence": float 0.0 a 1.0

Devolve APENAS um JSON array. Se não houver promessas concretas, devolve [].
Não incluas texto fora do JSON.
"""


def parse_filename(path: Path) -> tuple[str | None, str | None]:
    """Extrai party_id e year de um ficheiro. Ex: PSD-leg-2009.pdf → ('PSD', '2009')"""
    stem = path.stem
    parts = stem.split("-")
    if len(parts) < 3 or parts[1] != "leg":
        return None, None
    prefix = parts[0]
    year = parts[2]
    party_id = PARTY_MAP.get(prefix)
    if not party_id:
        log.warning(f"Prefixo desconhecido: {prefix} em {path.name}")
        return None, None
    return party_id, year


def page_id_for(party_id: str, election_id: str) -> str:
    return hashlib.sha256(f"{party_id}|{election_id}|tier2|pdf-manual".encode()).hexdigest()[:16]


def promise_id(page_id: str, text: str) -> str:
    return hashlib.sha256(f"{page_id}|{text}".encode()).hexdigest()[:16]


def already_extracted(conn, party_id: str, election_id: str) -> bool:
    count = conn.execute(
        "SELECT COUNT(*) FROM promises WHERE party_id = ? AND election_id = ?",
        (party_id, election_id),
    ).fetchone()[0]
    return count > 0


def discover_pending(programs_dir: Path, conn, year_filter=None, party_filter=None) -> list[Path]:
    """Devolve lista de ficheiros por processar (sem promessas na DB)."""
    pending = []
    for year_dir in sorted(programs_dir.iterdir()):
        if not year_dir.is_dir():
            continue
        year = year_dir.name
        if year_filter and year != str(year_filter):
            continue

        for f in sorted(year_dir.iterdir()):
            if f.suffix not in (".pdf", ".txt"):
                continue
            if f.suffix == ".txt" and f.stem.endswith(("_report", "REPORT")):
                continue

            party_id, file_year = parse_filename(f)
            if not party_id or not file_year:
                continue
            if party_filter and party_id != party_filter:
                continue

            election_id = f"leg_{file_year}"
            if already_extracted(conn, party_id, election_id):
                continue

            pending.append(f)

    return pending


def _parse_json_response(raw: str) -> list[dict]:
    """Extrai JSON array da resposta, tolerando code fences e arrays truncados."""
    # remover markdown code fences
    raw = re.sub(r"^```(?:json)?\s*", "", raw.strip(), flags=re.MULTILINE)
    raw = re.sub(r"\s*```\s*$", "", raw, flags=re.MULTILINE)
    raw = raw.strip()

    start = raw.find("[")
    if start == -1:
        log.warning(f"  Resposta sem JSON array: {raw[:200]}")
        return []

    end = raw.rfind("]") + 1
    if end == 0:
        # array truncado — recuperar objectos completos
        last_obj = raw.rfind("},")
        if last_obj == -1:
            last_obj = raw.rfind("}")
        if last_obj > start:
            try:
                return json.loads(raw[start : last_obj + 1] + "]")
            except json.JSONDecodeError:
                pass
        log.warning(f"  Array truncado e não recuperável ({len(raw)} chars)")
        return []

    try:
        return json.loads(raw[start:end])
    except json.JSONDecodeError as e:
        # tentar recuperar objectos completos antes do corte
        fragment = raw[start:end]
        last_obj = fragment.rfind("},")
        if last_obj == -1:
            last_obj = fragment.rfind("}")
        if last_obj > 0:
            try:
                recovered = json.loads(fragment[: last_obj + 1] + "]")
                log.warning(f"  JSON truncado — recuperados {len(recovered)} objectos (de {e})")
                return recovered
            except json.JSONDecodeError:
                pass
        log.warning(f"  JSON inválido e não recuperável: {e}")
        return []


def _extract_text_pypdf(pdf_path: Path) -> str:
    """Extrai texto de um PDF com pypdf."""
    import pypdf
    reader = pypdf.PdfReader(str(pdf_path))
    parts = []
    for page in reader.pages:
        try:
            parts.append(page.extract_text() or "")
        except Exception:
            pass
    return "\n".join(parts)


def _chunk_text(text: str, max_chars: int = TEXT_CHUNK_CHARS, overlap: int = TEXT_CHUNK_OVERLAP) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars
        if end < len(text):
            cut = text.rfind("\n\n", start, end)
            if cut == -1:
                cut = text.rfind(". ", start, end)
            if cut != -1:
                end = cut + 1
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


def _call_text_chunk(client: anthropic.Anthropic, chunk: str, party_id: str, year: str, chunk_n: int, total: int) -> list[dict]:
    party_name = PARTY_NAMES.get(party_id, party_id)
    prompt = EXTRACTION_PROMPT.format(
        party_name=party_name,
        party_id=party_id,
        year=year,
        topics=", ".join(TOPICS),
    )
    full = f"{prompt}\n\nTexto do programa (parte {chunk_n}/{total}):\n{chunk}"
    msg = client.messages.create(
        model=MODEL,
        max_tokens=8192,
        messages=[{"role": "user", "content": full}],
    )
    return _parse_json_response(msg.content[0].text)


def call_api_pdf(client: anthropic.Anthropic, pdf_path: Path, party_id: str, year: str) -> list[dict]:
    """Extrai promessas de um PDF ou TXT. PDFs grandes são processados via texto+chunks."""
    party_name = PARTY_NAMES.get(party_id, party_id)
    prompt = EXTRACTION_PROMPT.format(
        party_name=party_name,
        party_id=party_id,
        year=year,
        topics=", ".join(TOPICS),
    )

    file_size = pdf_path.stat().st_size

    if pdf_path.suffix == ".txt":
        text = pdf_path.read_text(encoding="utf-8", errors="replace")
        chunks = _chunk_text(text)
        if len(chunks) == 1:
            content = [{"type": "text", "text": f"{prompt}\n\nTexto do programa:\n{text}"}]
            msg = client.messages.create(model=MODEL, max_tokens=8192,
                                         messages=[{"role": "user", "content": content}])
            return _parse_json_response(msg.content[0].text)
        # múltiplos chunks
        all_promises: list[dict] = []
        seen: set[str] = set()
        for i, chunk in enumerate(chunks, 1):
            log.info(f"  chunk {i}/{len(chunks)}")
            for p in _call_text_chunk(client, chunk, party_id, year, i, len(chunks)):
                t = (p.get("text") or "").strip()
                if t and t not in seen:
                    seen.add(t)
                    all_promises.append(p)
            if i < len(chunks):
                time.sleep(1)
        return all_promises

    if file_size > PDF_NATIVE_MAX_BYTES:
        # PDF grande — extrair texto e chunkar
        log.info(f"  PDF grande ({file_size // 1_048_576}MB) — a extrair texto com pypdf")
        text = _extract_text_pypdf(pdf_path)
        if not text.strip():
            log.warning("  pypdf não extraiu texto (PDF digitalizado?)")
            return []
        log.info(f"  {len(text):,} chars extraídos")
        chunks = _chunk_text(text)
        log.info(f"  {len(chunks)} chunks")
        all_promises: list[dict] = []
        seen: set[str] = set()
        for i, chunk in enumerate(chunks, 1):
            log.info(f"  chunk {i}/{len(chunks)}")
            for p in _call_text_chunk(client, chunk, party_id, year, i, len(chunks)):
                t = (p.get("text") or "").strip()
                if t and t not in seen:
                    seen.add(t)
                    all_promises.append(p)
            if i < len(chunks):
                time.sleep(1)
        return all_promises

    # PDF pequeno — enviar nativo como base64
    pdf_data = base64.standard_b64encode(pdf_path.read_bytes()).decode("utf-8")
    content = [
        {
            "type": "document",
            "source": {"type": "base64", "media_type": "application/pdf", "data": pdf_data},
        },
        {"type": "text", "text": prompt},
    ]
    msg = client.messages.create(model=MODEL, max_tokens=8192,
                                 messages=[{"role": "user", "content": content}])
    return _parse_json_response(msg.content[0].text)


def import_promises(conn, promises: list[dict], party_id: str, election_id: str, year: str, source_path: Path) -> int:
    """Insere promessas na DB. Devolve número inserido."""
    pid = page_id_for(party_id, election_id)

    existing_page = conn.execute("SELECT id FROM archived_pages WHERE id = ?", (pid,)).fetchone()
    if not existing_page:
        conn.execute("""
            INSERT INTO archived_pages (id, url, archived_url, timestamp, party_id, election_id,
                                        tier, mime_type, status_code, crawled_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """, (
            pid,
            f"file://{source_path.resolve()}",
            f"file://{source_path.resolve()}",
            f"{year}0101000000",
            party_id,
            election_id,
            2,
            "application/pdf" if source_path.suffix == ".pdf" else "text/plain",
            200,
        ))

    inserted = 0
    for p in promises:
        text = (p.get("text") or "").strip()
        if not text:
            continue
        prom_id = promise_id(pid, text)
        existing = conn.execute("SELECT id FROM promises WHERE id = ?", (prom_id,)).fetchone()
        if existing:
            continue
        conn.execute("""
            INSERT INTO promises (id, page_id, party_id, election_id, text, context, topic,
                                  tier, extraction_confidence, extraction_model, extracted_at, is_valid)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (
            prom_id, pid, party_id, election_id,
            text[:500],
            p.get("context", "")[:300] if p.get("context") else None,
            p.get("topic", "outros"),
            2,
            float(p.get("confidence", 0.8)),
            MODEL,
            datetime.now().isoformat(),
        ))
        inserted += 1

    conn.commit()
    return inserted


def save_json(promises: list[dict], source_path: Path):
    """Guarda o JSON ao lado do PDF para referência futura."""
    json_path = source_path.with_suffix(".json")
    json_path.write_text(json.dumps(promises, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Extrai promessas de PDFs via Claude API")
    parser.add_argument("--year", help="Processar só este ano (ex: 2019)")
    parser.add_argument("--party", help="Processar só este partido (ex: PS, PSD)")
    parser.add_argument("--dry-run", action="store_true", help="Não escrever na DB, só mostrar o que faria")
    parser.add_argument("--list", action="store_true", help="Listar ficheiros por processar e sair")
    args = parser.parse_args()

    from backend.database import get_connection, init_db

    init_db()
    conn = get_connection()

    programs_dir = Path(__file__).parent.parent / "data" / "programs"
    pending = discover_pending(programs_dir, conn, year_filter=args.year, party_filter=args.party)

    if not pending:
        print("Nenhum ficheiro por processar.")
        conn.close()
        return

    print(f"\nFicheiros por processar: {len(pending)}")
    for f in pending:
        party_id, year = parse_filename(f)
        print(f"  {f.relative_to(programs_dir)}  →  {party_id} / leg_{year}")

    if args.list:
        conn.close()
        return

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERRO: ANTHROPIC_API_KEY não definida no .env")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    total_inserted = 0
    errors = []

    for i, f in enumerate(pending, 1):
        party_id, year = parse_filename(f)
        election_id = f"leg_{year}"
        party_name = PARTY_NAMES.get(party_id, party_id)
        size_kb = f.stat().st_size // 1024

        print(f"\n[{i}/{len(pending)}] {party_name} {year} ({f.name}, {size_kb}KB)")

        if args.dry_run:
            print("  [DRY RUN] saltado")
            continue

        try:
            promises = call_api_pdf(client, f, party_id, year)
            print(f"  → {len(promises)} promessas extraídas")

            save_json(promises, f)

            inserted = import_promises(conn, promises, party_id, election_id, year, f)
            print(f"  → {inserted} inseridas na DB")
            total_inserted += inserted

            time.sleep(2)

        except anthropic.RateLimitError:
            log.warning("  Rate limit — a aguardar 60s")
            time.sleep(60)
            # retry uma vez
            try:
                promises = call_api_pdf(client, f, party_id, year)
                save_json(promises, f)
                inserted = import_promises(conn, promises, party_id, election_id, year, f)
                print(f"  → {inserted} inseridas na DB (retry)")
                total_inserted += inserted
            except Exception as e:
                log.error(f"  ERRO no retry: {e}")
                errors.append(f.name)

        except json.JSONDecodeError as e:
            log.error(f"  JSON inválido: {e}")
            errors.append(f.name)

        except Exception as e:
            log.error(f"  ERRO: {e}")
            errors.append(f.name)
            time.sleep(5)

    conn.close()

    print(f"\n{'='*50}")
    print(f"Concluído: {total_inserted} promessas inseridas no total")
    if errors:
        print(f"Erros em {len(errors)} ficheiros: {', '.join(errors)}")


if __name__ == "__main__":
    main()
