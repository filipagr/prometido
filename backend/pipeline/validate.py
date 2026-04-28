"""
pipeline/validate.py

Passo 2 do pipeline: validação automática de promessas extraídas.

Para cada promessa com is_valid=NULL, chama Claude API com um prompt diferente
para avaliar se é realmente uma promessa concreta e bem atribuída.

Output por promessa:
  - is_valid: bool
  - validation_score: float 0.0-1.0
  - needs_human_review: bool (casos ambíguos chegam à curadoria manual)
  - validation_reason: texto breve se is_valid=false ou needs_human_review=true

Critérios de needs_human_review=true:
  - extraction_confidence < 0.7 E validation_score > 0.5 (conflito)
  - validation_score entre 0.4 e 0.7 (zona cinzenta)
  - is_valid=true mas extraction_confidence < 0.5
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

MODEL = "claude-haiku-4-5-20251001"  # Haiku para validação — mais barato, suficiente para classificação binária

VALIDATION_PROMPT = """\
És um revisor de qualidade de dados políticos. Avalia se uma promessa eleitoral \
extraída automaticamente é concreta e verificável.

Promessa a avaliar:
- Texto: {promise_text}
- Contexto: {promise_context}
- Partido: {party_name}
- Data: {page_date}
- Tipo de fonte: {tier_desc}
- Confiança da extracção: {extraction_confidence:.2f}

Para ser VÁLIDA (is_valid=true), a promessa TEM DE TER pelo menos um destes elementos:
A) Um número ou valor concreto (ex: "aumentar para X%", "criar Y postos de trabalho", "investir Z milhões")
B) Um prazo específico (ex: "até 2027", "nos primeiros 100 dias", "até ao final da legislatura")
C) Uma acção singular e identificável (ex: "criar o programa X", "eliminar a taxa Y", "construir Z hospitais")
D) Uma lei, instituição ou medida nomeada concretamente

REJEITAR (is_valid=false) se:
- Declaração de intenção vaga: "vamos apoiar", "iremos promover", "trabalhamos para melhorar"
- Valores genéricos ou princípios: "acreditamos em", "defendemos", "o PS quer"
- Diagnóstico ou crítica: descreve problema mas não propõe acção concreta
- Retórica política: "um Portugal melhor", "mais justo", "mais competitivo"
- Duplicado ou fragmento: parte de uma promessa maior sem substância própria
- Muito curta e sem especificidade (menos de 10 palavras úteis)

Devolve APENAS este JSON (sem texto fora do JSON):
{{
  "is_valid": true/false,
  "validation_score": 0.0 a 1.0,
  "needs_human_review": true/false,
  "reason": "explicação em 1 frase se is_valid=false ou needs_human_review=true, senão null"
}}

needs_human_review deve ser true APENAS se:
- A promessa é válida mas a verificabilidade é genuinamente ambígua
- validation_score entre 0.5 e 0.75 (incerteza real, não casos óbvios)
"""


def _validate_promise(
    client: anthropic.Anthropic,
    promise: sqlite3.Row,
    party_name: str,
) -> dict:
    """Chama Claude API para validar uma promessa. Devolve dict com campos de validação."""
    tier = promise["tier"]
    tier_desc = {
        1: "site oficial do partido",
        2: "programa de governo",
        3: "artigo jornalístico",
    }.get(tier, "desconhecido")

    timestamp = promise["extracted_at"] or ""
    page_date = timestamp[:10] if timestamp else "desconhecida"

    prompt = VALIDATION_PROMPT.format(
        promise_text=promise["text"],
        promise_context=promise["context"] or "(sem contexto)",
        party_name=party_name,
        page_date=page_date,
        tier_desc=tier_desc,
        extraction_confidence=promise["extraction_confidence"] or 0.5,
    )

    msg = client.messages.create(
        model=MODEL,
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = msg.content[0].text.strip()

    # extrair JSON
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError(f"Resposta sem JSON: {raw[:100]}")

    result = json.loads(raw[start:end])

    # normalizar campos
    is_valid = bool(result.get("is_valid", False))
    validation_score = float(result.get("validation_score", 0.5))
    needs_review = bool(result.get("needs_human_review", False))
    reason = result.get("reason")

    # regra adicional: se extraction_confidence baixa mas validation_score alta → review
    ext_conf = promise["extraction_confidence"] or 0.5
    if is_valid and ext_conf < 0.5 and validation_score > 0.6:
        needs_review = True
        reason = reason or "Conflito entre confiança de extracção baixa e validação alta"

    return {
        "is_valid": is_valid,
        "validation_score": validation_score,
        "needs_human_review": needs_review,
        "reason": reason,
    }


def run_validation(
    party_ids: list[str] | None = None,
    election_ids: list[str] | None = None,
    max_promises: int | None = None,
    dry_run: bool = False,
) -> dict:
    """
    Valida todas as promessas com is_valid=NULL.

    Args:
        party_ids: subset de partidos
        election_ids: subset de eleições
        max_promises: limite de promessas
        dry_run: não escreve na DB

    Returns:
        dict com stats: validated, valid, invalid, needs_review, errors
    """
    from backend.database import get_connection

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY não definida.")

    client = anthropic.Anthropic(api_key=api_key)
    conn = get_connection()

    where_clauses = ["p.is_valid IS NULL"]
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
        f"""SELECT p.id, p.text, p.context, p.party_id, p.election_id, p.tier,
                   p.extraction_confidence, p.extracted_at,
                   pt.name as party_name
            FROM promises p
            LEFT JOIN parties pt ON p.party_id = pt.id
            WHERE {where}
            ORDER BY p.party_id, p.election_id
            {limit_clause}""",
        params,
    ).fetchall()

    total = len(promises)
    log.info(f"Promessas a validar: {total}")

    stats = {"validated": 0, "valid": 0, "invalid": 0, "needs_review": 0, "errors": 0}

    for i, promise in enumerate(promises):
        try:
            result = _validate_promise(client, promise, promise["party_name"] or promise["party_id"])

            if dry_run:
                status = "✓" if result["is_valid"] else "✗"
                review = " ⚠ REVIEW" if result["needs_human_review"] else ""
                log.info(
                    f"  {status} [{result['validation_score']:.2f}]{review} "
                    f"{promise['text'][:80]}"
                )
                if result["reason"]:
                    log.info(f"    → {result['reason']}")
            else:
                conn.execute(
                    """UPDATE promises SET
                        is_valid = ?,
                        validation_score = ?,
                        needs_human_review = ?,
                        status_note = ?
                       WHERE id = ?""",
                    (
                        1 if result["is_valid"] else 0,
                        result["validation_score"],
                        1 if result["needs_human_review"] else 0,
                        result["reason"],
                        promise["id"],
                    ),
                )

            stats["validated"] += 1
            if result["is_valid"]:
                stats["valid"] += 1
            else:
                stats["invalid"] += 1
            if result["needs_human_review"]:
                stats["needs_review"] += 1

            if (i + 1) % 20 == 0:
                if not dry_run:
                    conn.commit()
                log.info(
                    f"  {i+1}/{total} | válidas:{stats['valid']} "
                    f"inválidas:{stats['invalid']} review:{stats['needs_review']}"
                )

            time.sleep(0.3)

        except anthropic.RateLimitError:
            log.warning("Rate limit — a aguardar 60s")
            time.sleep(60)
        except Exception as e:
            log.error(f"Erro na promessa {promise['id']}: {e}")
            stats["errors"] += 1

    if not dry_run:
        conn.commit()

    conn.close()
    log.info(
        f"\nValidação concluída: {stats['validated']} avaliadas | "
        f"{stats['valid']} válidas | {stats['invalid']} inválidas | "
        f"{stats['needs_review']} para revisão humana | {stats['errors']} erros"
    )
    return stats


def print_review_queue(conn: sqlite3.Connection | None = None) -> None:
    """Mostra as promessas que precisam de revisão humana."""
    from backend.database import get_connection

    close = False
    if conn is None:
        conn = get_connection()
        close = True

    promises = conn.execute("""
        SELECT p.id, p.party_id, p.election_id, p.text, p.topic,
               p.extraction_confidence, p.validation_score, p.status_note
        FROM promises p
        WHERE p.needs_human_review = 1
        ORDER BY p.party_id, p.election_id
    """).fetchall()

    print(f"\nFila de revisão humana: {len(promises)} promessas\n")
    for p in promises:
        print(f"[{p['id']}] {p['party_id']} / {p['election_id']} / {p['topic']}")
        print(f"  Texto: {p['text'][:120]}")
        print(f"  Conf. extracção: {p['extraction_confidence']:.2f} | Validação: {p['validation_score']:.2f}")
        if p["status_note"]:
            print(f"  Razão: {p['status_note']}")
        print()

    if close:
        conn.close()


if __name__ == "__main__":
    import argparse
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    parser = argparse.ArgumentParser(description="Validação automática de promessas (Passo 2)")
    parser.add_argument("--parties", nargs="+", help="Subset de partidos")
    parser.add_argument("--elections", nargs="+", help="Subset de eleições")
    parser.add_argument("--max", type=int, help="Máximo de promessas a validar")
    parser.add_argument("--dry-run", action="store_true", help="Não escrever na DB")
    parser.add_argument("--review-queue", action="store_true", help="Mostrar fila de revisão")
    args = parser.parse_args()

    if args.review_queue:
        print_review_queue()
    else:
        run_validation(
            party_ids=args.parties,
            election_ids=args.elections,
            max_promises=args.max,
            dry_run=args.dry_run,
        )
