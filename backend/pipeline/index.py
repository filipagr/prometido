"""
pipeline/index.py

Passo final do pipeline:
1. Rebuild do índice FTS5 (para promessas adicionadas sem trigger)
2. Calcula e imprime stats finais da base de dados
"""

import logging
import sqlite3
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


def rebuild_fts(conn: sqlite3.Connection) -> None:
    """Reconstrói o índice FTS5 a partir do zero."""
    log.info("A reconstruir índice FTS5...")
    conn.execute("INSERT INTO promises_fts(promises_fts) VALUES('rebuild')")
    conn.commit()
    count = conn.execute("SELECT COUNT(*) FROM promises_fts").fetchone()[0]
    log.info(f"FTS5 reconstruído: {count} entradas")


def print_stats(conn: sqlite3.Connection) -> None:
    """Imprime um resumo completo do estado da base de dados."""
    total = conn.execute("SELECT COUNT(*) FROM promises").fetchone()[0]
    valid = conn.execute("SELECT COUNT(*) FROM promises WHERE is_valid = 1").fetchone()[0]
    invalid = conn.execute("SELECT COUNT(*) FROM promises WHERE is_valid = 0").fetchone()[0]
    pending = conn.execute("SELECT COUNT(*) FROM promises WHERE is_valid IS NULL").fetchone()[0]
    review = conn.execute("SELECT COUNT(*) FROM promises WHERE needs_human_review = 1").fetchone()[0]
    sources = conn.execute("SELECT COUNT(*) FROM verification_sources").fetchone()[0]

    print(f"\n{'='*55}")
    print(f"  PROMETIDO — Estado da base de dados")
    print(f"{'='*55}")
    print(f"  Promessas total:        {total:>6}")
    print(f"  Válidas (is_valid=1):   {valid:>6}")
    print(f"  Inválidas:              {invalid:>6}")
    print(f"  Por validar:            {pending:>6}")
    print(f"  Para revisão humana:    {review:>6}")
    print(f"  Fontes de verificação:  {sources:>6}")
    print(f"{'='*55}")

    # por partido e eleição
    rows = conn.execute("""
        SELECT party_id, election_id, COUNT(*) as total,
               SUM(CASE WHEN is_valid=1 THEN 1 ELSE 0 END) as valid,
               SUM(CASE WHEN status='corroborated' THEN 1 ELSE 0 END) as corroborated,
               SUM(CASE WHEN status='evidence_of_implementation' THEN 1 ELSE 0 END) as implemented
        FROM promises
        GROUP BY party_id, election_id
        ORDER BY party_id, election_id
    """).fetchall()

    if rows:
        print(f"\n  {'Partido':<8} {'Eleição':<12} {'Total':>6} {'Válidas':>8} {'Corrob.':>8} {'Cumpr.':>8}")
        print(f"  {'-'*54}")
        for r in rows:
            print(f"  {r['party_id'] or '-':<8} {r['election_id'] or '-':<12} {r['total']:>6} {r['valid']:>8} {r['corroborated']:>8} {r['implemented']:>8}")

    # tópicos mais comuns
    topics = conn.execute("""
        SELECT topic, COUNT(*) as n
        FROM promises WHERE is_valid = 1
        GROUP BY topic ORDER BY n DESC LIMIT 8
    """).fetchall()

    if topics:
        print(f"\n  Tópicos mais frequentes:")
        for t in topics:
            print(f"    {t['topic'] or 'outros':<25} {t['n']:>4}")

    # estados
    statuses = conn.execute("""
        SELECT status, COUNT(*) as n
        FROM promises WHERE is_valid = 1
        GROUP BY status ORDER BY n DESC
    """).fetchall()

    if statuses:
        print(f"\n  Estados:")
        for s in statuses:
            print(f"    {s['status']:<35} {s['n']:>4}")

    print()


def run_index(rebuild: bool = True) -> None:
    from backend.database import get_connection
    conn = get_connection()
    if rebuild:
        rebuild_fts(conn)
    print_stats(conn)
    conn.close()


if __name__ == "__main__":
    import argparse
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    parser = argparse.ArgumentParser(description="Indexação FTS5 e stats")
    parser.add_argument("--no-rebuild", action="store_true", help="Não reconstruir FTS5, só mostrar stats")
    args = parser.parse_args()

    run_index(rebuild=not args.no_rebuild)
