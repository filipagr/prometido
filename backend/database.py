import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "prometido.db"
SEEDS_PATH = Path(__file__).parent.parent / "data" / "seeds"

SCHEMA = """
CREATE TABLE IF NOT EXISTS parties (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    short_name  TEXT NOT NULL,
    color       TEXT,
    founded     DATE,
    domains     TEXT,   -- JSON array
    notes       TEXT
);

CREATE TABLE IF NOT EXISTS elections (
    id                  TEXT PRIMARY KEY,
    type                TEXT NOT NULL,
    date                DATE NOT NULL,
    description         TEXT,
    discovery_window    TEXT  -- JSON {"from": "YYYYMMDD", "to": "YYYYMMDD"}
);

CREATE TABLE IF NOT EXISTS archived_pages (
    id              TEXT PRIMARY KEY,   -- sha256(url + timestamp)[:16]
    url             TEXT NOT NULL,
    archived_url    TEXT NOT NULL,
    timestamp       TEXT NOT NULL,      -- YYYYMMDDHHMMSS
    party_id        TEXT REFERENCES parties(id),
    election_id     TEXT REFERENCES elections(id),
    raw_text        TEXT,
    tier            INTEGER NOT NULL,   -- 1, 2, ou 3
    mime_type       TEXT,
    status_code     INTEGER,
    crawled_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS promises (
    id                      TEXT PRIMARY KEY,   -- sha256(page_id + text)[:16]
    page_id                 TEXT REFERENCES archived_pages(id),
    party_id                TEXT REFERENCES parties(id),
    election_id             TEXT REFERENCES elections(id),
    text                    TEXT NOT NULL,
    context                 TEXT,
    topic                   TEXT,               -- tópico primário
    topics                  TEXT,               -- JSON array com todos os tópicos (ex: ["habitação","economia"])
    tier                    INTEGER,
    extraction_confidence   REAL,
    validation_score        REAL,
    is_valid                INTEGER,            -- 0/1 (SQLite boolean)
    needs_human_review      INTEGER DEFAULT 0,
    status                  TEXT DEFAULT 'archived',
    status_note             TEXT,
    extraction_model        TEXT,
    extracted_at            TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS election_governments (
    election_id TEXT REFERENCES elections(id),
    party_id    TEXT REFERENCES parties(id),
    role        TEXT NOT NULL,  -- 'prime_minister' | 'coalition_partner' | 'confidence_supply'
    PRIMARY KEY (election_id, party_id)
);

CREATE TABLE IF NOT EXISTS verification_sources (
    id              TEXT PRIMARY KEY,
    promise_id      TEXT REFERENCES promises(id),
    archived_url    TEXT NOT NULL,
    source_domain   TEXT,
    source_date     TEXT,
    use_type        TEXT,               -- corroboration | fulfillment | breach
    quote           TEXT,
    added_by        TEXT DEFAULT 'pipeline'
);

CREATE VIRTUAL TABLE IF NOT EXISTS promises_fts USING fts5(
    text,
    topic,
    content=promises,
    content_rowid=rowid
);

CREATE TRIGGER IF NOT EXISTS promises_fts_insert AFTER INSERT ON promises BEGIN
    INSERT INTO promises_fts(rowid, text, topic) VALUES (new.rowid, new.text, new.topic);
END;

CREATE TRIGGER IF NOT EXISTS promises_fts_delete AFTER DELETE ON promises BEGIN
    INSERT INTO promises_fts(promises_fts, rowid, text, topic) VALUES ('delete', old.rowid, old.text, old.topic);
END;

CREATE TRIGGER IF NOT EXISTS promises_fts_update AFTER UPDATE ON promises BEGIN
    INSERT INTO promises_fts(promises_fts, rowid, text, topic) VALUES ('delete', old.rowid, old.text, old.topic);
    INSERT INTO promises_fts(rowid, text, topic) VALUES (new.rowid, new.text, new.topic);
END;
"""


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    conn = get_connection()
    conn.executescript(SCHEMA)
    conn.commit()
    _seed(conn)
    conn.close()
    print(f"DB iniciada em {DB_PATH}")


def _seed(conn: sqlite3.Connection) -> None:
    parties_file = SEEDS_PATH / "parties.json"
    elections_file = SEEDS_PATH / "elections.json"

    parties = json.loads(parties_file.read_text())
    for p in parties:
        conn.execute(
            """INSERT OR IGNORE INTO parties (id, name, short_name, color, founded, domains, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                p["id"],
                p["name"],
                p["short_name"],
                p.get("color"),
                p.get("founded"),
                json.dumps(p.get("domains", [])),
                p.get("notes"),
            ),
        )

    elections = json.loads(elections_file.read_text())
    for e in elections:
        conn.execute(
            """INSERT OR IGNORE INTO elections (id, type, date, description, discovery_window)
               VALUES (?, ?, ?, ?, ?)""",
            (
                e["id"],
                e["type"],
                e["date"],
                e.get("description"),
                json.dumps(e.get("discovery_window", {})),
            ),
        )

    govs_file = SEEDS_PATH / "election_governments.json"
    govs = json.loads(govs_file.read_text())
    for g in govs:
        conn.execute(
            """INSERT OR IGNORE INTO election_governments (election_id, party_id, role)
               VALUES (?, ?, ?)""",
            (g["election_id"], g["party_id"], g["role"]),
        )

    conn.commit()
    print(f"  {len(parties)} partidos, {len(elections)} eleições e {len(govs)} registos de governo carregados.")


if __name__ == "__main__":
    init_db()
