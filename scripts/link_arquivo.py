"""
scripts/link_arquivo.py

Liga cada programa eleitoral local a uma URL arquivada no Arquivo.pt.

Estratégia por camadas:
1. URL exacta conhecida → pesquisa CDX directamente → link perfeito
2. Pesquisa CDX por PDFs no domínio → download dos candidatos → comparação SHA1
3. Fallback: homepage do partido no Arquivo.pt na data da eleição
4. Fallback final: URL do Wayback Machine (se conhecida)

Uso:
    python3 scripts/link_arquivo.py --dry-run   # só mostra o que faria
    python3 scripts/link_arquivo.py             # actualiza DB
    python3 scripts/link_arquivo.py --report    # estado actual na DB
    python3 scripts/link_arquivo.py --party PS --election leg_2009
"""

import argparse
import base64
import hashlib
import json
import sys
import time
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).parent.parent))

CDX    = "https://arquivo.pt/wayback/cdx"
REPLAY = "https://arquivo.pt/noFrame/replay/{ts}/{url}"

# URLs originais conhecidas (de program_sources.md) — pesquisa CDX directa
KNOWN_URLS: dict[tuple, str] = {
    ("PCP",   "leg_2009"): "http://www.pcp.pt/dmfiles/programa-eleitoral-ar2009.pdf",
    ("PCP",   "leg_2011"): "https://www.pcp.pt/sites/default/files/documentos/2011_compromisso_eleitoral_pcp_legistativas.pdf",
    ("IL",    "leg_2019"): "https://portugal.liberal.pt/asset/5:iniciativa-liberal---programa-politico",
    ("IL",    "leg_2024"): "https://iniciativaliberal.pt/wp-content/uploads/2024/02/Por-um-Portugal-com-Futuro-Programa-Eleitoral-IL-2024.pdf",
    ("Chega", "leg_2022"): "https://partidochega.pt/programa-politico-chega/",
    ("PAN",   "leg_2015"): "http://www.pan.com.pt/eleicoes/propostas-pan.html",
}

# Fallback Wayback Machine quando Arquivo.pt não tem
WAYBACK_FALLBACKS: dict[tuple, str] = {
    ("PCP",   "leg_2009"): "https://web.archive.org/web/20090926082751/http://www.pcp.pt/dmfiles/programa-eleitoral-ar2009.pdf",
    ("IL",    "leg_2019"): "https://web.archive.org/web/20190531122322/https://portugal.liberal.pt/asset/5:iniciativa-liberal---programa-politico",
    ("IL",    "leg_2024"): "https://web.archive.org/web/20240203214607/https://iniciativaliberal.pt/wp-content/uploads/2024/02/Por-um-Portugal-com-Futuro-Programa-Eleitoral-IL-2024.pdf",
    ("Chega", "leg_2022"): "https://web.archive.org/web/20211206200845/https://partidochega.pt/programa-politico-chega/",
    ("PAN",   "leg_2015"): "https://web.archive.org/web/20151005220909/http://www.pan.com.pt/eleicoes/propostas-pan.html",
}

# Domínio principal por partido (e overrides por eleição)
DOMAINS: dict[tuple, list[str]] = {
    ("PS",    None):   ["ps.pt"],
    ("PSD",   None):   ["psd.pt"],
    ("PSD",   "2015"): ["portugalafrente.pt", "psd.pt"],
    ("PSD",   "2024"): ["adportugal.pt", "psd.pt"],
    ("PSD",   "2025"): ["adportugal.pt", "psd.pt"],
    ("BE",    None):   ["bloco.org"],
    ("PCP",   None):   ["pcp.pt", "cdu.pt"],
    ("CDS",   None):   ["cds.pt", "partido-cds.pt"],
    ("IL",    None):   ["iniciativaliberal.pt"],
    ("IL",    "2019"): ["portugal.liberal.pt", "iniciativaliberal.pt"],
    ("Chega", None):   ["chega.pt", "partidochega.pt"],
    ("Livre", None):   ["partidolivre.pt"],
    ("PAN",   None):   ["pan.com.pt"],
}

# Janela de pesquisa CDX: 9 meses antes até 2 meses depois da eleição
WINDOWS: dict[str, tuple[str, str]] = {
    "leg_2002": ("20010601", "20020430"),
    "leg_2005": ("20040401", "20050430"),
    "leg_2009": ("20090101", "20091130"),
    "leg_2011": ("20101001", "20110731"),
    "leg_2015": ("20150101", "20151201"),
    "leg_2019": ("20190101", "20191201"),
    "leg_2022": ("20210401", "20220301"),
    "leg_2024": ("20230601", "20240501"),
    "leg_2025": ("20241001", "20250701"),
}


# ── helpers ──────────────────────────────────────────────────────────────────

def sha1_b32(data: bytes) -> str:
    return base64.b32encode(hashlib.sha1(data).digest()).decode()


def cdx_query(params: dict, timeout: int = 90) -> list[dict]:
    try:
        r = httpx.get(CDX, params={**params, "output": "json"}, timeout=timeout)
        r.raise_for_status()
        out = []
        for line in r.text.strip().splitlines():
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
        return out
    except Exception as e:
        print(f"      CDX erro: {e}")
        return []


def fetch_bytes(url: str, timeout: int = 60) -> bytes | None:
    try:
        r = httpx.get(url, follow_redirects=True, timeout=timeout)
        r.raise_for_status()
        return r.content
    except Exception as e:
        print(f"      fetch erro: {e}")
        return None


def domains_for(party_id: str, year: str) -> list[str]:
    return (
        DOMAINS.get((party_id, year))
        or DOMAINS.get((party_id, None))
        or []
    )


# ── estratégias ──────────────────────────────────────────────────────────────

def try_known_url(party_id: str, election_id: str) -> str | None:
    """Camada 1: URL exacta conhecida → pesquisa CDX → link Arquivo.pt."""
    known = KNOWN_URLS.get((party_id, election_id))
    if not known:
        return None
    print(f"    [1] URL conhecida: {known[:70]}")
    entries = cdx_query({"url": known, "limit": "10", "status": "200"})
    if entries:
        e = entries[0]
        url = REPLAY.format(ts=e["timestamp"], url=e["url"])
        print(f"    ✓ Arquivo.pt: {url[:80]}")
        return url
    print(f"    não encontrada no CDX")
    return None


def try_sha1_match(party_id: str, election_id: str, local_path: Path) -> str | None:
    """Camada 2: pesquisa CDX por PDFs no domínio → download → SHA1."""
    if local_path.suffix != ".pdf":
        return None

    year = election_id.split("_")[1]
    from_date, to_date = WINDOWS.get(election_id, ("20000101", "20260101"))
    local_sha1 = sha1_b32(local_path.read_bytes())
    local_size  = local_path.stat().st_size
    print(f"    [2] SHA1 local: {local_sha1}  ({local_size//1024}KB)")

    for domain in domains_for(party_id, year):
        print(f"    CDX {domain} [{from_date}–{to_date}]", end=" ", flush=True)
        entries = cdx_query({
            "url": f"{domain}/*",
            "from": from_date,
            "to": to_date,
            "limit": "1000",
            "collapse": "digest",
            "status": "200",
        })
        # filtrar por URL com .pdf e tamanho razoável (compressed > 30KB)
        pdf_entries = [
            e for e in entries
            if ".pdf" in e.get("url", "").lower()
            and int(e.get("length", 0)) > 30_000
        ]
        print(f"→ {len(entries)} entradas, {len(pdf_entries)} PDFs candidatos")

        # ordenar por tamanho decrescente (programas são grandes)
        pdf_entries.sort(key=lambda e: int(e.get("length", 0)), reverse=True)

        for e in pdf_entries[:8]:  # máx 8 downloads por domínio
            replay_url = REPLAY.format(ts=e["timestamp"], url=e["url"])
            print(f"      download {e['url'][-60:]} ({int(e['length'])//1024}KB comprimido)… ", end="", flush=True)
            data = fetch_bytes(replay_url, timeout=45)
            if data is None:
                print("erro")
                continue
            remote_sha1 = sha1_b32(data)
            if remote_sha1 == local_sha1:
                print(f"✓ MATCH")
                return replay_url
            print(f"✗ ({len(data)//1024}KB raw)")
            time.sleep(0.5)

        time.sleep(1)

    return None


def try_homepage(party_id: str, election_id: str) -> str | None:
    """Camada 3: homepage do partido no Arquivo.pt próxima da eleição."""
    year = election_id.split("_")[1]
    from_date, to_date = WINDOWS.get(election_id, ("20000101", "20260101"))

    for domain in domains_for(party_id, year):
        entries = cdx_query({
            "url": f"{domain}/",
            "from": from_date,
            "to": to_date,
            "limit": "50",
            "status": "200",
            "collapse": "digest",
        })
        if not entries:
            # tentar sem trailing slash
            entries = cdx_query({
                "url": domain,
                "from": from_date,
                "to": to_date,
                "limit": "50",
                "status": "200",
                "collapse": "digest",
            })
        if entries:
            # pegar a entrada mais próxima do dia da eleição (última do período)
            e = entries[-1]
            url = REPLAY.format(ts=e["timestamp"], url=e["url"])
            print(f"    [3] homepage {domain}: {e['timestamp']}")
            return url
        time.sleep(0.5)

    return None


def try_wayback(party_id: str, election_id: str) -> str | None:
    """Camada 4: fallback Wayback Machine."""
    url = WAYBACK_FALLBACKS.get((party_id, election_id))
    if url:
        print(f"    [4] Wayback fallback")
    return url


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run",  action="store_true")
    parser.add_argument("--report",   action="store_true")
    parser.add_argument("--party",    help="ex: PS")
    parser.add_argument("--election", help="ex: leg_2009")
    args = parser.parse_args()

    from backend.database import get_connection, init_db
    init_db()
    conn = get_connection()

    if args.report:
        rows = conn.execute("""
            SELECT ap.party_id, ap.election_id, ap.archived_url,
                   COUNT(p.id) as n
            FROM archived_pages ap
            JOIN promises p ON p.page_id = ap.id
            WHERE ap.tier = 2
            GROUP BY ap.id
            ORDER BY ap.election_id, ap.party_id
        """).fetchall()
        print(f"\n{'Partido':<8} {'Eleição':<12} {'N':>6}  URL")
        print("-" * 80)
        for r in rows:
            u = r["archived_url"] or ""
            if "arquivo.pt" in u:          tag = "✓ arquivo.pt"
            elif "archive.org" in u:       tag = "~ wayback"
            elif u.startswith("http"):     tag = "~ directo"
            else:                          tag = "✗ local"
            print(f"{r['party_id']:<8} {r['election_id']:<12} {r['n']:>6}  {tag}")
        conn.close()
        return

    programs_dir = Path(__file__).parent.parent / "data" / "programs"

    # carregar páginas tier 2
    pages = conn.execute("""
        SELECT id, party_id, election_id, archived_url
        FROM archived_pages WHERE tier = 2
        ORDER BY election_id, party_id
    """).fetchall()

    summary = {"arquivo": 0, "wayback": 0, "homepage": 0, "sem_url": 0}

    for row in pages:
        page_id, party_id, election_id, current_url = (
            row["id"], row["party_id"], row["election_id"], row["archived_url"]
        )

        if args.party and party_id != args.party:
            continue
        if args.election and election_id != args.election:
            continue

        print(f"\n{'─'*60}")
        print(f"{party_id} / {election_id}")

        # já tem URL arquivada?
        if current_url and ("arquivo.pt" in current_url or "archive.org" in current_url):
            print(f"  ✓ já tem: {current_url[:80]}")
            summary["arquivo"] += 1
            continue

        # encontrar ficheiro local
        year = election_id.split("_")[1]
        local_path = None
        from scripts.extract_pdf_api import parse_filename
        year_dir = programs_dir / year
        if year_dir.exists():
            for f in sorted(year_dir.iterdir()):
                if f.suffix not in (".pdf", ".txt"):
                    continue
                fp, fy = parse_filename(f)
                if fp == party_id and fy == year:
                    local_path = f
                    break
        if local_path:
            print(f"  ficheiro: {local_path.name}")

        # tentar camadas
        new_url = (
            try_known_url(party_id, election_id)
            or (try_sha1_match(party_id, election_id, local_path) if local_path else None)
            or try_wayback(party_id, election_id)
            or try_homepage(party_id, election_id)
        )

        if new_url:
            kind = "arquivo.pt" if "arquivo.pt" in new_url else "wayback" if "archive.org" in new_url else "homepage"
            print(f"  → {kind}: {new_url[:80]}")
            if kind == "arquivo.pt":
                summary["arquivo"] += 1
            elif kind == "wayback":
                summary["wayback"] += 1
            else:
                summary["homepage"] += 1
            if not args.dry_run:
                conn.execute("UPDATE archived_pages SET archived_url = ? WHERE id = ?", (new_url, page_id))
                conn.commit()
        else:
            print(f"  ✗ sem URL arquivada")
            summary["sem_url"] += 1

        time.sleep(1)

    conn.close()
    print(f"\n{'='*60}")
    print(f"Arquivo.pt:  {summary['arquivo']}")
    print(f"Wayback:     {summary['wayback']}")
    print(f"Homepage:    {summary['homepage']}")
    print(f"Sem URL:     {summary['sem_url']}")


if __name__ == "__main__":
    main()
