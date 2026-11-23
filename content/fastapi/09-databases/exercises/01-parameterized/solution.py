import sqlite3


def create_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        "CREATE TABLE IF NOT EXISTS notes ("
        " id INTEGER PRIMARY KEY,"
        " title TEXT NOT NULL,"
        " body TEXT NOT NULL DEFAULT '')"
    )
    conn.commit()


def _to_dict(row) -> dict:
    return {"id": row[0], "title": row[1], "body": row[2]}


def add_note(conn: sqlite3.Connection, title: str, body: str = "") -> int:
    cur = conn.execute("INSERT INTO notes (title, body) VALUES (?, ?)", (title, body))
    conn.commit()
    return cur.lastrowid


def get_note(conn: sqlite3.Connection, note_id: int) -> dict | None:
    row = conn.execute("SELECT id, title, body FROM notes WHERE id = ?", (note_id,)).fetchone()
    return _to_dict(row) if row else None


def search(conn: sqlite3.Connection, text: str) -> list[dict]:
    rows = conn.execute(
        "SELECT id, title, body FROM notes WHERE title LIKE ? ORDER BY id", (f"%{text}%",)
    ).fetchall()
    return [_to_dict(r) for r in rows]
