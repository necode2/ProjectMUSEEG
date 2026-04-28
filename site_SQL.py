# want SQL database to look like this:
# TODO: add SQLCipher encryption before formal research publication
# TODO: migrate to PostgreSQL if concurrent users become an issue
"""
users
------
user_id        (hashed serial port)
genres         (their preferred genres)
moods          (their target moods)
consent        (True/False — did they agree to share?)
created_at     (when they first connected)
last_seen      (when they last connected)

sessions
---------
session_id     (the uuid we generate)
user_id        (links back to users table)
started_at     
ended_at

feedback
---------
id
session_id     (which session this happened in)
user_id        (which user)
track_id       (YouTube video ID)
track_title
type           (like/dislike)
mood_at_time   (EEG mood score when they clicked)
ts             (timestamp)

mood_readings
--------------
id
session_id
user_id
mood           (0.0 - 1.0)
ts
"""



import sqlite3
from datetime import datetime

DB = "museeg.db"  # name of our SQLite database file

def init_db():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    # table 1: users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id     TEXT PRIMARY KEY,
            nickname    TEXT,
            genres      TEXT,
            moods       TEXT,
            consent     INTEGER DEFAULT 0,
            created_at  TEXT,
            last_seen   TEXT
        )
    """)

    # table 2: sessions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id   TEXT PRIMARY KEY,
            user_id      TEXT,
            started_at   DATETIME,
            ended_at     DATETIME
        )
    """)
    
    # table 3: feedback
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id     TEXT,
            user_id        TEXT,
            track_id       TEXT,
            track_title    TEXT,
            type           TEXT,
            mood_at_time   REAL,
            ts             DATETIME
        )
    """)

    # table 4: mood_readings
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mood_readings (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id     TEXT,
            user_id        TEXT,
            mood           REAL,
            ts             DATETIME
        )
    """)

    conn.commit()
    conn.close()


def save_user(user_id, nickname, genres, moods):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    
    # insert a new row into users table
    cursor.execute("""
        INSERT OR IGNORE INTO users (user_id, nickname, genres, moods, consent, created_at, last_seen)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, nickname, ",".join(genres), ",".join(moods), 0, datetime.now(), datetime.now()))

    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    # query the users table for this user_id
    cursor.execute("""
        SELECT * FROM users WHERE user_id = ?
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row  # returns a tuple of the user's data or None if not found

def get_mood_history(user_id):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT mood, ts FROM mood_readings
        WHERE user_id = ?
        ORDER BY ts ASC
    """, (user_id,))
    
    rows = cursor.fetchall()  # returns list of tuples: [(0.6, "2024-..."), ...]
    conn.close()
    
    # convert rows into a list of dicts
    dicts = [{"mood": mood, "timestamp": ts} for mood, ts in rows]
    return dicts

def save_feedback(session_id, user_id, track_id, track_title, feedback_type, mood_at_time):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    
    # insert into feedback
    cursor.execute("""
        INSERT INTO feedback (session_id, user_id, track_id, track_title, type, mood_at_time, ts)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (session_id, user_id, track_id, track_title, feedback_type, mood_at_time, datetime.now()))
    
    conn.commit()
    conn.close()

def save_mood_reading(session_id, user_id, mood):
    conn   = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO mood_readings (session_id, user_id, mood, ts)
        VALUES (?, ?, ?, ?)
    """, (session_id, user_id, mood, datetime.now()))
    conn.commit()
    conn.close()

def update_consent(user_id, consent):
    conn   = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users SET consent = ? WHERE user_id = ?
    """, (1 if consent else 0, user_id))

    conn.commit()
    conn.close()