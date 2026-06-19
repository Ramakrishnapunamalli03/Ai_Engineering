"""SQLite persistence for chat threads and messages."""
import sqlite3, time, uuid
from contextlib import contextmanager

DB_PATH = "chat.db"

@contextmanager
def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    with _conn() as c:
        c.executescript(
            """
            CREATE TABLE IF NOT EXISTS threads (
                id         TEXT PRIMARY KEY,
                title      TEXT NOT NULL,
                model      TEXT NOT NULL,
                created_at REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS messages (
                id         TEXT PRIMARY KEY,
                thread_id  TEXT NOT NULL REFERENCES threads(id) ON DELETE CASCADE,
                role       TEXT NOT NULL,
                content    TEXT NOT NULL,
                created_at REAL NOT NULL
            );
            """
        )

def create_thread(title: str, model: str) -> str:
    tid = "thread_" + uuid.uuid4().hex[:12]
    with _conn() as c:
        c.execute(
            "INSERT INTO threads (id, title, model, created_at) VALUES (?, ?, ?, ?)",
            (tid, (title or "New chat")[:60], model, time.time()),
        )
    return tid

def list_threads() -> list:
    with _conn() as c:
        rows = c.execute("SELECT * FROM threads ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]

def get_messages(thread_id: str) -> list:
    with _conn() as c:
        rows = c.execute(
            "SELECT role, content FROM messages WHERE thread_id = ? ORDER BY created_at",
            (thread_id,),
        ).fetchall()
        return [dict(r) for r in rows]

def add_message(thread_id: str, role: str, content: str) -> None:
    with _conn() as c:
        c.execute(
            "INSERT INTO messages (id, thread_id, role, content, created_at) VALUES (?, ?, ?, ?, ?)",
            ("msg_" + uuid.uuid4().hex[:12], thread_id, role, content, time.time()),
        )

def delete_thread(thread_id: str) -> None:
    with _conn() as c:
        c.execute("DELETE FROM threads WHERE id = ?", (thread_id,))


def get_thread(thread_id: str) -> dict | None:
    with _conn() as c:
        row = c.execute("SELECT * FROM threads WHERE id = ?", (thread_id,)).fetchone()
        return dict(row) if row else None


def test_db() -> dict:
    with _conn() as c:
        thread_count = c.execute("SELECT COUNT(*) AS count FROM threads").fetchone()["count"]
        message_count = c.execute("SELECT COUNT(*) AS count FROM messages").fetchone()["count"]
    return {"threads": thread_count, "messages": message_count}
