import sqlite3
import os

from datetime import datetime, timedelta

from boss_data import BOSS


# =========================
# Database 路徑追蹤
# =========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_NAME = os.path.join(
    BASE_DIR,
    "boss.db"
)

print("DATABASE PATH:", DB_NAME)


TIME_FORMAT = "%Y-%m-%d %H:%M:%S"



# =========================
# 初始化資料庫
# =========================

def init_db():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS boss (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        respawn_time TEXT,
        miss_count INTEGER DEFAULT 0
    )
    """)


    # 舊資料庫補欄位

    cursor.execute(
        "PRAGMA table_info(boss)"
    )

    columns = [
        row[1]
        for row in cursor.fetchall()
    ]


    if "miss_count" not in columns:

        cursor.execute("""
            ALTER TABLE boss
            ADD COLUMN miss_count INTEGER DEFAULT 0
        """)


    conn.commit()

    conn.close()



# =========================
# 登記王
# =========================

def save_boss(name, respawn_time):


    print(
        "SAVE:",
        name,
        respawn_time
    )


    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()



    cursor.execute("""
    INSERT INTO boss(
        name,
        respawn_time,
        miss_count
    )

    VALUES(?,?,0)


    ON CONFLICT(name)

    DO UPDATE SET

        respawn_time=excluded.respawn_time,

        miss_count=0
    """,
    (
        name,
        respawn_time
    ))



    conn.commit()

    conn.close()



# =========================
# 查詢所有王
# 自動輪空
# =========================

def get_all_boss():
    print(
        "READ DATABASE:",
        DB_NAME
    )


    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()


    now = datetime.now()



    cursor.execute("""
        SELECT
            name,
            respawn_time,
            miss_count

        FROM boss
    """)



    bosses = cursor.fetchall()



    result = []



    for name, respawn_time, miss_count in bosses:


        respawn = datetime.strptime(
            respawn_time,
            TIME_FORMAT
        )



        # 自動輪空

        while respawn <= now:


            miss_count += 1



            # 超過三次刪除

            if miss_count > 3:


                print(
                    "DELETE:",
                    name
                )


                cursor.execute(
                    """
                    DELETE FROM boss
                    WHERE name=?
                    """,
                    (name,)
                )


                break



            respawn += timedelta(
                hours=BOSS[name]
            )



        if miss_count <= 3:


            cursor.execute("""
                UPDATE boss

                SET
                    respawn_time=?,
                    miss_count=?

                WHERE name=?
            """,
            (
                respawn.strftime(
                    TIME_FORMAT
                ),
                miss_count,
                name
            ))



            result.append(
                (
                    name,
                    respawn.strftime(
                        TIME_FORMAT
                    ),
                    miss_count
                )
            )



    conn.commit()



    # 重生時間排序

    result.sort(
        key=lambda x:
        datetime.strptime(
            x[1],
            TIME_FORMAT
        )
    )



    conn.close()



    return result



# =========================
# 清除全部
# =========================

def clear_all_boss():

    print(
        "CLEAR DATABASE:",
        DB_NAME
    )

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM boss"
    )

    conn.commit()

    conn.close()

    print("CLEAR DONE")



# =========================
# 手動 KL
# =========================

def late_boss(name):


    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()



    cursor.execute("""
        SELECT
            respawn_time,
            miss_count

        FROM boss

        WHERE name=?
    """,
    (name,))



    row = cursor.fetchone()



    if row is None:


        conn.close()

        return None



    respawn = datetime.strptime(
        row[0],
        TIME_FORMAT
    )



    miss_count = row[1] + 1



    if miss_count > 3:


        cursor.execute(
            """
            DELETE FROM boss
            WHERE name=?
            """,
            (name,)
        )


        conn.commit()

        conn.close()


        return None



    new_respawn = respawn + timedelta(
        hours=BOSS[name]
    )



    cursor.execute("""
        UPDATE boss

        SET
            respawn_time=?,
            miss_count=?

        WHERE name=?
    """,
    (
        new_respawn.strftime(
            TIME_FORMAT
        ),
        miss_count,
        name
    ))



    conn.commit()

    conn.close()



    return new_respawn



# =========================
# 啟動自動初始化
# =========================

init_db()
