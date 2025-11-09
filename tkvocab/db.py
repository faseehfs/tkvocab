import sqlite3
import os
from datetime import datetime, timedelta


DB_PATH = os.path.join(os.path.dirname(__file__), "tkvocab.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS words (
    word TEXT PRIMARY KEY,
    comment TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    next_review_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    interval_days INTEGER NOT NULL
);
"""


def get_conn():
    conn = sqlite3.connect(
        DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
    )
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.executescript(SCHEMA)
    conn.commit()
    conn.close()


def add_word(word, comment):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO words (word, comment, interval_days, next_review_date, created_at) VALUES (?,?,?,?,?)",
            (word, comment, 1, datetime.now(), datetime.now()),
        )
        conn.commit()
        return True, None
    except sqlite3.IntegrityError as e:
        return False, str(e)
    finally:
        conn.close()


def get_all_words():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM words ORDER BY word;")
    rows = cur.fetchall()
    conn.close()
    return rows


def delete_word(word):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM words WHERE word = ?;", (word,))
    conn.commit()
    conn.close()


def update_review_date(word, interval_days):
    conn = get_conn()
    cur = conn.cursor()
    next_date = datetime.now() + timedelta(days=interval_days)
    cur.execute(
        "UPDATE words SET interval_days = ?, next_review_date = ? WHERE word = ?;",
        (interval_days, next_date, word),
    )
    conn.commit()
    conn.close()


def get_review_word_row():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM words WHERE next_review_date < ? ORDER BY next_review_date ASC LIMIT 1;",
        (datetime.now(),),
    )
    row = cur.fetchone()
    conn.close()
    return row
