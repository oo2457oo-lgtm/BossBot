import sqlite3
from datetime import datetime, timedelta
from boss_data import BOSS

DB_NAME = "boss.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS boss (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        respawn_time TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_boss(name, respawn_time):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR REPLACE INTO boss(name, respawn_time)
    VALUES(?,?)
    """, (name, respawn_time))

    conn.commit()
    conn.close()


def get_all_boss():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, respawn_time
        FROM boss
        ORDER BY datetime(respawn_time) ASC
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows


def clear_all_boss():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM boss")

    conn.commit()
    conn.close()


def late_boss(name):
    """Boss 輪空，重生時間往後加一個重生週期"""

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT respawn_time FROM boss WHERE name=?",
        (name,)
    )

    row = cursor.fetchone()

    if row is None:
        conn.close()
        return None

    respawn = datetime.strptime(
        row[0],
        "%Y-%m-%d %H:%M:%S"
    )

    # 根據 boss_data.py 的重生小時數往後推
    new_respawn = respawn + timedelta(hours=BOSS[name])

    cursor.execute(
        """
        UPDATE boss
        SET respawn_time=?
        WHERE name=?
        """,
        (
            new_respawn.strftime("%Y-%m-%d %H:%M:%S"),
            name
        )
    )

    conn.commit()
    conn.close()

    return new_respawn