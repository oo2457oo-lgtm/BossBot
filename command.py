from datetime import datetime, timedelta
from boss_data import BOSS
from fixed_boss import FIXED_BOSS
from database import save_boss, late_boss


def register_boss(name, kill_time=None):

    if name not in BOSS:
        return "沒有這隻首領"

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

    respawn = now + timedelta(hours=BOSS[name])

    # 存入資料庫
    save_boss(name, respawn.strftime("%Y-%m-%d %H:%M:%S"))

    return f"""
✅ 登記成功

{name}

死亡

{now.strftime("%Y-%m-%d %H:%M:%S")}

重生

{respawn.strftime("%Y-%m-%d %H:%M:%S")}
"""


def late_register(name):
    """Boss 輪空，自動往下一個重生時間"""

    if name not in BOSS:
        return "沒有這隻首領"

    new_respawn = late_boss(name)

    if new_respawn is None:
        return "此首領尚未登記"

    return f"""
⚠ {name} 輪空

新的重生時間

{new_respawn.strftime("%Y-%m-%d %H:%M:%S")}
"""


def get_fixed_boss():

    today = datetime.now().weekday()

    result = []

    for boss in FIXED_BOSS:
        if today in boss["days"]:
            result.append(boss)

    return result