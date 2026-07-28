from datetime import datetime
import os

from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler

from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    PushMessageRequest,
    TextMessage
)

from fixed_boss import FIXED_BOSS

load_dotenv()

CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")

# 記錄今天是否已推播
last_notify_date = None


def notify_fixed_boss():
    global last_notify_date

    today = datetime.now()

    # 同一天只推播一次
    if last_notify_date == today.date():
        return

    weekday = today.weekday()

    bosses = [
        boss for boss in FIXED_BOSS
        if weekday in boss["days"]
    ]

    if not bosses:
        return

    if not CHANNEL_ACCESS_TOKEN:
        print("❌ CHANNEL_ACCESS_TOKEN 未設定")
        return

    if not GROUP_ID:
        print("❌ GROUP_ID 未設定")
        return

    reply = "🔔 固定首領即將出現（5分鐘）\n\n"
    reply += f"🕒 {bosses[0]['time']}\n\n"

    for boss in bosses:
        reply += f"🔥 {boss['name']}\n"

    reply += "\n請準備集合！"

    configuration = Configuration(
        access_token=CHANNEL_ACCESS_TOKEN
    )

    try:
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)

            line_bot_api.push_message(
                PushMessageRequest(
                    to=GROUP_ID,
                    messages=[
                        TextMessage(text=reply)
                    ]
                )
            )

        last_notify_date = today.date()
        print("✅ 固定首領提醒已推播")

    except Exception as e:
        print("❌ 推播失敗")
        print(e)


scheduler = BackgroundScheduler()

# 正式使用
scheduler.add_job(
    notify_fixed_boss,
    trigger="cron",
    hour=14,
    minute=55
)

scheduler.start()