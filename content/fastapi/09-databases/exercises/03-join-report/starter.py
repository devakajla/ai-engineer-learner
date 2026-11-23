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


def open_tasks_per_user(conn):
    pass


def busiest_users(conn, min_open):
    pass


def add_index(conn):
    pass
