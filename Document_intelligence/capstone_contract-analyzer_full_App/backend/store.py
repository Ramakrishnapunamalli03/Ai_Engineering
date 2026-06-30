"""SQLite store for parsed documents (pages + audit), keyed by doc_id."""
import json, sqlite3, time, uuid
from contextlib import contextmanager

DB_PATH = "contracts.db"


@contextmanager
def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with _conn() as c:
        c.execute(
            "CREATE TABLE IF NOT EXISTS docs ("
            " id TEXT PRIMARY KEY, name TEXT, pages TEXT, audit TEXT, created_at REAL)"
        )


def save_doc(name: str, pages: list, audit: list) -> str:
    doc_id = "doc_" + uuid.uuid4().hex[:12]
    with _conn() as c:
        c.execute(
            "INSERT INTO docs (id, name, pages, audit, created_at) VALUES (?, ?, ?, ?, ?)",
            (doc_id, name, json.dumps(pages), json.dumps(audit), time.time()),
        )
    return doc_id


def get_doc(doc_id: str):
    with _conn() as c:
        row = c.execute("SELECT * FROM docs WHERE id = ?", (doc_id,)).fetchone()
        if not row:
            return None
        return {
            "id": row["id"], "name": row["name"],
            "pages": json.loads(row["pages"]), "audit": json.loads(row["audit"]),
        }