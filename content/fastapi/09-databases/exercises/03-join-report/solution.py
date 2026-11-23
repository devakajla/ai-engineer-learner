import sqlite3


def setup(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT NOT NULL UNIQUE);
        CREATE TABLE tasks (id INTEGER PRIMARY KEY, title TEXT NOT NULL, done INTEGER NOT NULL DEFAULT 0,
                            owner_id INTEGER NOT NULL REFERENCES users(id));
        INSERT INTO users (id, email) VALUES (1, 'dev@x.io'), (2, 'ana@x.io'), (3, 'zed@x.io');
        INSERT INTO tasks (title, done, owner_id) VALUES
            ('a', 0, 1), ('b', 1, 1), ('c', 0, 2), ('d', 0, 2), ('e', 1, 3);
        """
    )


def open_tasks_per_user(conn: sqlite3.Connection) -> list[tuple[str, int]]:
    return conn.execute(
        """
        SELECT u.email, COUNT(t.id) AS open_count
        FROM users u
        LEFT JOIN tasks t ON t.owner_id = u.id AND t.done = 0
        GROUP BY u.id
        ORDER BY open_count DESC, u.email ASC
        """
    ).fetchall()


def busiest_users(conn: sqlite3.Connection, min_open: int) -> list[str]:
    rows = conn.execute(
        """
        SELECT u.email
        FROM users u
        JOIN tasks t ON t.owner_id = u.id AND t.done = 0
        GROUP BY u.id
        HAVING COUNT(t.id) >= ?
        ORDER BY u.email
        """,
        (min_open,),
    ).fetchall()
    return [r[0] for r in rows]


def add_index(conn: sqlite3.Connection) -> None:
    conn.execute("CREATE INDEX IF NOT EXISTS ix_tasks_owner_done ON tasks (owner_id, done)")
