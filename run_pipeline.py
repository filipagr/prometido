"""
run_pipeline.py

Orquestrador do pipeline completo do Prometido.
Corre todos os passos em sequência com logging claro.

Uso rápido:
    # Pipeline completo
    venv/bin/python run_pipeline.py

    # Só um subset (para testar)
    venv/bin/python run_pipeline.py --parties PS PSD --elections leg_2005 leg_2009

    # A partir de um passo específico
    venv/bin/python run_pipeline.py --from extract

    # Só ver stats
    venv/bin/python run_pipeline.py --stats
"""

import argparse
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env", override=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("pipeline")

STEPS = ["discovery", "fetch", "extract", "validate", "link", "index"]


def run_step(name: str, fn, *args, **kwargs):
    log.info(f"\n{'─'*50}")
    log.info(f"  PASSO: {name.upper()}")
    log.info(f"{'─'*50}")
    t0 = time.time()
    result = fn(*args, **kwargs)
    elapsed = time.time() - t0
    log.info(f"  ✓ {name} concluído em {elapsed:.0f}s")
    return result


def main():
    parser = argparse.ArgumentParser(description="Pipeline completo do Prometido")
    parser.add_argument("--parties", nargs="+", help="Subset de partidos (PS PSD BE PCP ...)")
    parser.add_argument("--elections", nargs="+", help="Subset de eleições (leg_2005 leg_2009 ...)")
    parser.add_argument("--tiers", nargs="+", type=int, default=[1, 2, 3], help="Tiers a processar")
    parser.add_argument("--from", dest="from_step", choices=STEPS, default="discovery",
                        help="Começar a partir deste passo")
    parser.add_argument("--only", choices=STEPS, help="Correr apenas este passo")
    parser.add_argument("--dry-run", action="store_true", help="Extracção em dry-run (não escreve)")
    parser.add_argument("--stats", action="store_true", help="Mostrar stats e sair")
    parser.add_argument("--claude-linking", action="store_true",
                        help="Usar Claude API para linking (mais preciso, mais caro)")
    parser.add_argument("--reset-validation", action="store_true",
                        help="Limpa resultados de validação anteriores antes de re-validar")
    args = parser.parse_args()

    # Normalizar party_ids para uppercase (BD usa 'PS', 'PSD', etc.)
    if args.parties:
        args.parties = [p.upper() for p in args.parties]

    from backend.database import init_db, get_connection

    # Init DB sempre
    init_db()

    if args.stats:
        from backend.pipeline.index import print_stats
        conn = get_connection()
        print_stats(conn)
        conn.close()
        return

    steps_to_run = STEPS if not args.only else [args.only]
    if args.from_step and not args.only:
        start_idx = STEPS.index(args.from_step)
        steps_to_run = STEPS[start_idx:]

    log.info(f"Passos a correr: {' → '.join(steps_to_run)}")
    if args.parties:
        log.info(f"Partidos: {args.parties}")
    if args.elections:
        log.info(f"Eleições: {args.elections}")

    # --- DISCOVERY ---
    if "discovery" in steps_to_run:
        from backend.pipeline.discovery import run_discovery
        run_step("discovery", run_discovery,
                 tiers=args.tiers,
                 party_ids=args.parties,
                 election_ids=args.elections)

    # --- FETCH ---
    if "fetch" in steps_to_run:
        from backend.pipeline.fetch import fetch_pages, fetch_pdfs
        conn = get_connection()

        fetch_kwargs = dict(
            conn=conn,
            party_id=args.parties[0] if args.parties and len(args.parties) == 1 else None,
            election_id=args.elections[0] if args.elections and len(args.elections) == 1 else None,
            delay=0.5,
        )

        run_step("fetch (HTML)", fetch_pages, **fetch_kwargs)
        run_step("fetch (PDFs)", fetch_pdfs,
                 conn=conn,
                 party_id=fetch_kwargs["party_id"],
                 election_id=fetch_kwargs["election_id"])
        conn.close()

    # --- EXTRACT ---
    if "extract" in steps_to_run:
        from backend.pipeline.extract import run_extraction
        tier_subset = [t for t in args.tiers if t in (1, 2)]
        run_step("extract", run_extraction,
                 party_ids=args.parties,
                 election_ids=args.elections,
                 tiers=tier_subset,
                 dry_run=args.dry_run)

    # --- VALIDATE ---
    if "validate" in steps_to_run and not args.dry_run:
        from backend.pipeline.validate import run_validation
        if args.reset_validation:
            conn = get_connection()
            where = ""
            params = []
            if args.parties:
                where += f" AND party_id IN ({','.join('?'*len(args.parties))})"
                params.extend(args.parties)
            if args.elections:
                where += f" AND election_id IN ({','.join('?'*len(args.elections))})"
                params.extend(args.elections)
            conn.execute(
                f"UPDATE promises SET is_valid=NULL, validation_score=NULL, needs_human_review=NULL WHERE 1=1{where}",
                params
            )
            conn.commit()
            log.info(f"Validação resetada para {conn.total_changes} promessas")
            conn.close()
        run_step("validate", run_validation,
                 party_ids=args.parties,
                 election_ids=args.elections)

    # --- LINK ---
    if "link" in steps_to_run and not args.dry_run:
        from backend.pipeline.link import run_linking
        run_step("link", run_linking,
                 party_ids=args.parties,
                 election_ids=args.elections,
                 use_claude=args.claude_linking)

    # --- INDEX ---
    if "index" in steps_to_run and not args.dry_run:
        from backend.pipeline.index import run_index
        run_step("index", run_index)

    log.info("\n✓ Pipeline concluído.")


if __name__ == "__main__":
    main()
