import sqlite3


def create_schema(conn):
    pass


def add_note(conn, title, body=""):
    cur = conn.execute(f"INSERT INTO notes (title, body) VALUES ('{title}', '{body}')")
    return cur.lastrowid


def get_note(conn, note_id):
    pass


def search(conn, text):
    pass
