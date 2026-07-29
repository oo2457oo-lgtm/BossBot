import json
import os
import scheduler
print("=== LINE BOT START ===")

from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, request, abort

from linebot.v3 import WebhookHandler
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.exceptions import InvalidSignatureError

from command import register_boss, late_register
from database import get_all_boss, clear_all_boss

import database

print("DATABASE FILE:", database.__file__)

load_dotenv()


CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")


app = Flask(__name__)


configuration = Configuration(
    access_token=CHANNEL_ACCESS_TOKEN
)

handler = WebhookHandler(
    CHANNEL_SECRET
)



@app.route("/")
def home():

    return "BossBot is running!"



@app.route("/callback", methods=["POST"])
def callback():

    print("===== CALLBACK HIT =====")

    signature = request.headers.get(
        "X-Line-Signature"
    )

    body = request.get_data(
        as_text=True
    )


    try:

        handler.handle(
            body,
            signature
        )

    except InvalidSignatureError:

        abort(400)


    return "OK"




@handler.add(
    MessageEvent,
    message=TextMessageContent
)
def handle_message(event):


    print(
        json.dumps(
            event.to_dict(),
            indent=4,
            ensure_ascii=False
        )
    )


    text = event.message.text.strip()

    upper_text = text.upper()



    # KL 王
    if upper_text.startswith("KL "):

        boss_name = text[3:].strip()

        reply = late_register(
            boss_name
        )



    # K 王 或 K 王 HHMM

    elif upper_text.startswith("K "):

        content = text[2:].strip()

        parts = content.split()


        if (
            len(parts) >= 2
            and parts[-1].isdigit()
            and len(parts[-1]) == 4
        ):

            boss_name = " ".join(
                parts[:-1]
            )

            kill_time = parts[-1]


            reply = register_boss(
                boss_name,
                kill_time
            )


        else:

            boss_name = content

            reply = register_boss(
                boss_name
            )




    # KB

    elif upper_text == "KB":


        bosses = get_all_boss()


        if len(bosses) == 0:

            reply = "目前沒有任何首領資料"


        else:


            reply = "===== 首領列表 =====\n\n"


            for name, respawn, miss_count in bosses:


                time = datetime.strptime(
                    respawn,
                    "%Y-%m-%d %H:%M:%S"
                ).strftime("%H%M")


                if miss_count > 0:

                    reply += (
                        f"{name}　"
                        f"{time}"
                        f"【輪空×{miss_count}】\n"
                    )

                else:

                    reply += (
                        f"{name}　"
                        f"{time}\n"
                    )




    # KH

    elif upper_text == "KH":


        bosses = get_all_boss()


        if len(bosses) == 0:

            reply = "目前沒有任何首領資料"


        else:


            reply = "===== 首領倒數 =====\n\n"


            now = datetime.now()



            for name, respawn, miss_count in bosses:


                respawn_time = datetime.strptime(
                    respawn,
                    "%Y-%m-%d %H:%M:%S"
                )


                diff = respawn_time - now


                if diff.total_seconds() > 0:


                    total = int(
                        diff.total_seconds()
                    )


                    hours = total // 3600

                    minutes = (
                        total % 3600
                    ) // 60



                    if hours > 0:

                        remain = (
                            f"{hours}小時"
                            f"{minutes}分"
                        )

                    else:

                        remain = (
                            f"{minutes}分"
                        )



                    if miss_count > 0:

                        reply += (
                            f"{name}　"
                            f"剩餘{remain}"
                            f"【輪空×{miss_count}】\n"
                        )

                    else:

                        reply += (
                            f"{name}　"
                            f"剩餘{remain}\n"
                        )



                else:


                    reply += (
                        f"{name}　"
                        "已重生\n"
                    )




    # KC

    elif upper_text == "KC":


        clear_all_boss()

        reply = "✅ 已清除所有首領時間"



    else:

        return




    with ApiClient(configuration) as api_client:


        line_bot_api = MessagingApi(
            api_client
        )


        line_bot_api.reply_message(

            ReplyMessageRequest(

                reply_token=event.reply_token,

                messages=[

                    TextMessage(
                        text=reply
                    )

                ]

            )

        )




if __name__ == "__main__":


    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )


    app.run(
        host="0.0.0.0",
        port=port
    )