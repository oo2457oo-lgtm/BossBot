from database import init_db, get_all_boss
from command import register_boss

init_db()

while True:

    text = input("BossBot > ")

    if text == "exit":
        break
    if text == "KB":
        bosses = get_all_boss()

        print("\n===== 首領列表 =====")

        if len(bosses) == 0:
            print("目前沒有任何資料")

        else:
            for boss in bosses:
                print(f"{boss[0]}  {boss[1]}")
    if text.startswith("K "):

        boss = text[2:]

        print(register_boss(boss))