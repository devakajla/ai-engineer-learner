import sqlite3
from contextlib import contextmanager

from app.repositories.base import Task

SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id          INTEGER PRIMARY KEY,
    title       TEXT    NOT NULL,
    description TEXT,
    priority    TEXT    NOT NULL DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high')),
    done        INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS ix_tasks_done ON tasks (done);
"""

COLUMNS = "id, title, description, priority, done"
UPDATABLE = {"title", "description", "priority", "done"}


class SqliteTaskRepository:
    """Raw-SQL storage. Opens a short-lived connection per operation (simple and thread-safe)."""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        with self._connect() as conn:
            conn.executescript(SCHEMA)

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            with conn:  # commit on success, rollback on error
                yield conn
        finally:
            conn.close()

    @staticmethod
    def _to_task(row: sqlite3.Row) -> Task:
        task = dict(row)
        task["done"] = bool(task["done"])
        return task

    def list(self, done: bool | None = None, priority: str | None = None, limit: int = 20) -> list[Task]:
        sql = f"SELECT {COLUMNS} FROM tasks WHERE 1 = 1"
        params: list = []
        if done is not None:
            sql += " AND done = ?"
            params.append(int(done))
        if priority is not None:
            sql += " AND priority = ?"
            params.append(priority)
        sql += " ORDER BY id LIMIT ?"
        params.append(limit)
        with self._connect() as conn:
            return [self._to_task(r) for r in conn.execute(sql, params).fetchall()]

    def get(self, task_id: int) -> Task | None:
        with self._connect() as conn:
            row = conn.execute(f"SELECT {COLUMNS} FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return self._to_task(row) if row else None

    def add(self, data: Task) -> Task:
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO tasks (title, description, priority, done) VALUES (?, ?, ?, ?)",
                (data["title"], data.get("description"), data.get("priority", "medium"), int(data.get("done", False))),
            )
            task_id = cur.lastrowid
        return self.get(task_id)

    def update(self, task_id: int, changes: Task) -> Task | None:
        fields = {k: v for k, v in changes.items() if k in UPDATABLE}
        if fields:
            assignments = ", ".join(f"{column} = ?" for column in fields)  # column names come from a whitelist
            values = [int(v) if k == "done" else v for k, v in fields.items()]
            with self._connect() as conn:
                conn.execute(f"UPDATE tasks SET {assignments} WHERE id = ?", (*values, task_id))
        return self.get(task_id)

    def delete(self, task_id: int) -> bool:
        with self._connect() as conn:
            return conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,)).rowcount == 1
