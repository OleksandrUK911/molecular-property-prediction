"""History storage, isolated from FastAPI (same pattern as inference.py).

SQLite for now - per backend/TODO_database.md's note that MVP can start
with SQLite locally and move to Postgres later without changing the
calling code, since these functions are the only place that touches SQL.
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent.parent / "app.db"


@contextmanager
def get_connection():
    # sqlite3's own context manager only commits/rolls back on exit, it
    # does NOT close the connection - wrap it so callers can't leak file
    # handles (showed up as ResourceWarning: unclosed database in tests).
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        with conn:
            yield conn
    finally:
        conn.close()


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS history (
                id TEXT PRIMARY KEY,
                smiles TEXT NOT NULL,
                predicted_target REAL NOT NULL,
                model_version TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


def insert_history(id: str, smiles: str, predicted_target: float, model_version: str, created_at: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO history (id, smiles, predicted_target, model_version, created_at) VALUES (?, ?, ?, ?, ?)",
            (id, smiles, predicted_target, model_version, created_at),
        )


def list_history(limit: int = 50) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, smiles, predicted_target, model_version, created_at FROM history ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]
