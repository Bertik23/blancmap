import sqlite3
import os


def connect():
    """Makes connection to database.

    Returns: Tuple(connection, cursor)"""
    new_db = False
    if not os.path.exists("database.db"):
        new_db = True
    con = sqlite3.connect("database.db")
    cur = con.cursor()

    if new_db:
        cur.execute(
            "CREATE TABLE users "
            "("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "username TEXT, "
            "password TEXT, "
            "email TEXT, "
            "settings TEXT"
            ")"
        )
        con.commit()
    return con, cur


def close(con: sqlite3.Connection, cur: sqlite3.Cursor):
    cur.close()
    con.close()
