from datetime import datetime, timedelta

from boss_data import BOSS
from fixed_boss import FIXED_BOSS
from database import save_boss, late_boss


TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def register_boss(name, kill_time=None):

    if name not in BOSS:
        return "沒有這隻首領"


    # 有輸入 K 王 HHMM
    if kill_time:

        hour = int(kill_time[:2])
        minute = int(kill_time[2:])

        now = datetime.now().replace(
            hour=hour,
            minute=minute,
            second=0,
            microsecond=0
        )

    else:

        now = datetime.now()



    respawn = now + timedelta(
        hours=BOSS[name]
    )


    # 登記新的擊殺
    # database 會自動清除 miss_count
    save_boss(
        name,
        respawn.strftime(TIME_FORMAT)
    )


    return (
        f"✅ {name}　"
        f"{respawn.strftime('%H%M')}"
    )



def late_register(name):

    """
    KL 王
    手動輪空用

    自動輪空主要由 database.py 處理
    """

    if name not in BOSS:
        return "沒有這隻首領"


    new_respawn = late_boss(name)


    if new_respawn is None:

        return (
            f"⚠ {name}\n"
            "尚未登記"
        )


    return (
        f"⚠ {name}　"
        f"{new_respawn.strftime('%H%M')}"
    )



def get_fixed_boss():

    today = datetime.now().weekday()

    result = []


    for boss in FIXED_BOSS:

        if today in boss["days"]:

            result.append(boss)


    return result