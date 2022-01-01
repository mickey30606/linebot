import os
import sys

from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, AudioMessage
from linebot.models import FollowEvent

from fsm import TocMachine
from utils import send_text_message, send_audio_message, send_flex_message, download_music, push_text_message, push_flex_message, push_audio_message

from crawl.crawl import youtube_crawler
from music_operator.GetMusic import Cut, GetYoutubeVideo, VideoToMusic

load_dotenv() # use to load .env file

user = dict()

fake_machine = TocMachine(
    states=["init_state", "find_music", "cut_music", "final_state"],
    transitions=[
        {
            "trigger": "youtube",
            "source": "init_state",
            "dest": "find_music",
            "conditions": "is_going_to_find_music",
        },
        {
            "trigger": "have_music",
            "source": "init_state",
            "dest": "cut_music",
        },
        {
            "trigger": "choose_number",
            "source": "find_music",
            "dest": "cut_music",
            "conditions": "is_going_to_cut_music",
        },
        {
            "trigger": "set_second",
            "source": "cut_music",
            "dest": "final_state",
            "conditions": "is_going_to_final_state"
        },
        {   "trigger": "go_back",
            "source": ["find_music", "cut_music"],
            "dest": "init_state",
            "conditions": "is_going_go_back",
        },
        {
            "trigger": "final_back",
            "source": "final_state",
            "dest": "init_state"
        },
    ],
    initial="init_state",
    auto_transitions=False,
    show_conditions=True,
)

def create_user(user_id):
    global user
    user[user_id] = dict()
    user[user_id]['avaliable'] = 1
    user[user_id]['video_title'] = []
    user[user_id]['video_url'] = []
    user[user_id]['video_img'] = []
    user[user_id]['music_name'] = 1
    user[user_id]['music_duration'] = 0
    #user[user_id]['tmp_video'] = "music/"+str(user_id)+"tmp.mp4"
    #user[user_id]['tmp_music'] = "music/"+str(user_id)+"tmp.mp3"
    #user[user_id]['output_music'] = "music/"+str(user_id)+"output.mp3"
    user[user_id]['tmp_video'] = str(user_id)+"tmp.mp4"
    user[user_id]['tmp_music'] = str(user_id)+"tmp.mp3"
    user[user_id]['output_music'] = str(user_id)+"output.mp3"
    user[user_id]['machine'] = TocMachine(
        states=["init_state", "find_music", "cut_music", "final_state"],
        transitions=[
            {
                "trigger": "youtube",
                "source": "init_state",
                "dest": "find_music",
                "conditions": "is_going_to_find_music",
            },
            {
                "trigger": "have_music",
                "source": "init_state",
                "dest": "cut_music",
            },
            {
                "trigger": "choose_number",
                "source": "find_music",
                "dest": "cut_music",
                "conditions": "is_going_to_cut_music",
            },
            {
                "trigger": "set_second",
                "source": "cut_music",
                "dest": "final_state",
                "conditions": "is_going_to_final_state"
            },
            {   "trigger": "go_back",
                "source": ["find_music", "cut_music"],
                "dest": "init_state",
                "conditions": "is_going_go_back",
            },
            {
                "trigger": "final_back",
                "source": "final_state",
                "dest": "init_state"
            },
        ],
        initial="init_state",
        auto_transitions=False,
        show_conditions=True,
    )
    return




file_url = os.getenv("FILE_HTTP", None)
print(file_url)

app = Flask(__name__, static_url_path="")


# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)


@app.route("/callback", methods=["POST"])
def callback():
    print("in callback")
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.message.text)
        )

    return "OK"


@app.route("/webhook", methods=["POST"])
def webhook_handler():
    global user
    print("in webhook")
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if isinstance(event , FollowEvent):
            send_text_message(event.reply_token,
                            ["如果需要使用 youtube 尋找音樂請輸入 YouTube ，也可以自行上傳音樂(電腦版限定)。"])
            continue
        user_id = event.source.user_id
        if user.get(user_id, 0) == 0:
            create_user(user_id)
            print("create user success")

        if user[user_id]['avaliable'] == 0:
            send_text_message(event.reply_token, ["快好了拉，不要催！"])
            continue

        print(f"\nFSM STATE: {user[user_id]['machine'].state}")

        if user[user_id]['machine'].state == 'init_state':
#            del user[event.source.user_id]
#            create_user(event.source.user_id)
            user[user_id]['music_name'] = 1
            user[user_id]['music_duration'] = 0
            user[user_id]['video_img'] = []
            user[user_id]['video_url'] = []
            user[user_id]['video_title'] = []
            if isinstance(event.message, AudioMessage):
                # special go to cut music
                user[user_id]['music_duration'] = event.message.duration / 1000.0
                if event.message.content_provider.type =="line":
                    user[user_id]['avaliable'] = 0
                    send_text_message(event.reply_token, ["下載音樂中..."])
                    download_music(user[user_id]['tmp_music'], event.message.id)
                    # go to cut music
                    user[user_id]['machine'].have_music(event)
                    push_text_message(user_id,
                                    ["音樂總長度為"+str(int(user[user_id]['music_duration']))+"秒",
                                    "請輸入想要剪的秒數範圍，請以半形逗號或半形波浪號做為分隔，例如 20, 100 或是 0 ~ 90",
                                    "如果不需要剪歌，請輸入 不用 或 不需要。",
                                    "如果想重新選擇，請輸入 從頭再來一次。"])
                    user[user_id]['avaliable'] = 1
                    continue
                else:
                    send_text_message(event.reply_token,
                                    ["請從本地端上傳音樂！",
                                     "如果需要使用 youtube 尋找音樂請輸入 YouTube ，也可以自行上傳音樂。"])
                    continue
            else:
                if isinstance(event, MessageEvent):
                    if isinstance(event.message, TextMessage):
                        if isinstance(event.message.text, str):
                            response = user[user_id]['machine'].youtube(event)
                            if response == True:
                                send_text_message(event.reply_token,
                                                ["請輸入想尋找的音樂名稱，伺服器將從 youtube 上搜尋",
                                                "如果想重新選擇，請輸入 從頭再來一次。"])
                                continue

            send_text_message(event.reply_token,
                            ["如果需要使用 youtube 尋找音樂請輸入 YouTube ，也可以自行上傳音樂(電腦版限定)。"])
        elif user[user_id]['machine'].state == 'find_music':
            if isinstance(event, MessageEvent):
                if isinstance(event.message, TextMessage):
                    if isinstance(event.message.text, str):
                        response = user[user_id]['machine'].go_back(event)
                        if response:
                            send_text_message(event.reply_token,
                                            ["如果需要使用 youtube 尋找音樂請輸入 YouTube ，也可以自行上傳音樂。"])
                            continue
                        response = user[user_id]['machine'].choose_number(event)
                        if response == 0:
                            user[user_id]['music_name'] = event.message.text
                            # 爬蟲
                            user[user_id]['avaliable'] = 0
                            send_text_message(event.reply_token, ["音樂搜尋中..."])
                            user[user_id]['video_title'], user[user_id]['video_url'], user[user_id]['video_img'] = youtube_crawler(user[user_id]['music_name'])
                            push_flex_message(user_id, user[user_id]['video_title'], user[user_id]['video_url'], user[user_id]['video_img'],
                                            ["選擇後需要等待一小段時間，伺服器會自動幫你下載音樂喔～",
                                            "如果想重新選擇，請輸入 從頭再來一次。"])
                            user[user_id]['avaliable'] = 1
                            user[user_id]['music_name'] = -1
                            continue
                        else:
                            user[user_id]['music_name'] = int(event.message.text)
                            user[user_id]['music_name'] -= 1
                            user[user_id]['avaliable'] = 0
                            send_text_message(event.reply_token, ["影片檔案下載中..."])
                            GetYoutubeVideo(user[user_id]['video_url'][user[user_id]['music_name']], user[user_id]['tmp_video'])
                            push_text_message(user_id, ["轉換為音檔中..."])
                            user[user_id]['music_duration'] = VideoToMusic(user[user_id]['tmp_video'], user[user_id]['tmp_music'])
                            push_text_message(user_id,
                                            ["音樂總長度為"+str(int(user[user_id]['music_duration']))+"秒",
                                            "請輸入想要剪的秒數範圍，請以半形逗號或半形波浪號做為分隔，例如 20, 100 或是 0 ~ 90",
                                            "如果不需要剪歌，請輸入 不用 或 不需要。",
                                            "如果想重新選擇，請輸入 從頭再來一次。"])
                            user[user_id]['avaliable'] = 1
                            continue
            send_text_message(event.reply_token,
                                ["請輸入想尋找的音樂名稱，伺服器將從 youtube 上搜尋",
                                "如果想重新選擇，請輸入 從頭再來一次。"])
        elif user[user_id]['machine'].state == 'cut_music':
            if isinstance(event, MessageEvent):
                if isinstance(event.message, TextMessage):
                    if isinstance(event.message.text, str):
                        response = user[user_id]['machine'].go_back(event)
                        if response:
                            send_text_message(event.reply_token,
                                            ["如果需要使用 youtube 尋找音樂請輸入 YouTube ，也可以自行上傳音樂。"])
                            continue

                        start = 0
                        end = 0
                        if event.message.text == "不用" or event.message.text == "不需要":
                            send_text_message(event.reply_token, ["處理中..."])
                            user[user_id]['avaliable'] = 0
                            start = 0
                            end = user[user_id]['music_duration']
                            user[user_id]['music_duration'] = end- start
                            user[user_id]['machine'].set_second(start, end, user[user_id]['music_duration'])
                            push_audio_message(user_id, file_url, user[user_id]['music_duration'], user[user_id]['tmp_music'],
                                            ["如果需要使用 youtube 尋找音樂請輸入 YouTube ，也可以自行上傳音樂(電腦版限定)。"])
                            user[user_id]['machine'].final_back()
                            user[user_id]['avaliable'] = 1
                            del user[user_id]
                            continue
                        else:
                            result = event.message.text
                            result = result.split(',')
                            if len(result) == 1:
                                result = result[0].split('~')
                            if len(result) == 1:
                                result = result[0].split('～')
                            if len(result) == 1:
                                result = result[0].split('，')
                            try:
                                start = int(result[0])
                                end = int(result[1])
                            except ValueError as e:
                                send_text_message(event.reply_token,
                                                ["音樂總長度為"+str(int(user[user_id]['music_duration']))+"秒",
                                                "請輸入想要剪的秒數範圍，請以半形逗號或半形波浪號做為分隔，例如 20, 100 或是 0 ~ 90",
                                                "如果不需要剪歌，請輸入 不用 或 不需要。",
                                                "如果想重新選擇，請輸入 從頭再來一次。"])
                                continue
                        response = user[user_id]['machine'].set_second(start, end, user[user_id]['music_duration'])
                        if response == 0:
                            send_text_message(event.reply_token,
                                            ["音樂總長度為"+str(int(user[user_id]['music_duration']))+"秒",
                                            "請輸入想要剪的秒數範圍，請以半形逗號或半形波浪號做為分隔，例如 20, 100 或是 0 ~ 90",
                                            "如果不需要剪歌，請輸入 不用 或 不需要。",
                                            "如果想重新選擇，請輸入 從頭再來一次。"])
                            continue
                        else:
                            user[user_id]['avaliable'] = 0
                            send_text_message(event.reply_token, ["進行中，請稍等..."])
                            # 剪音樂
                            Cut(user[user_id]['tmp_music'], start*1000, end*1000, user[user_id]['output_music'])
                            user[user_id]['music_duration'] = end- start
                            push_audio_message(user_id, file_url, user[user_id]['music_duration'], user[user_id]['output_music'],
                                            ["如果需要使用 youtube 尋找音樂請輸入 YouTube ，也可以自行上傳音樂(電腦版限定)。"])
                            user[user_id]['machine'].final_back()
                            user[user_id]['avaliable'] = 1
                            del user[user_id]
                            continue
            send_text_message(event.reply_token,
                            ["音樂總長度為"+str(int(user[user_id]['music_duration']))+"秒",
                            "請輸入想要剪的秒數範圍，請以半形逗號或半形波浪號做為分隔，例如 20, 100 或是 0 ~ 90",
                            "如果不需要剪歌，請輸入 不用 或 不需要。",
                            "如果想重新選擇，請輸入 從頭再來一次。"])

        elif user[user_id]['machine'].state == 'final_state':
            send_text_message(event.reply_token, "I'm in final state!!!")
        else:
            send_text_message(event.reply_token, "啥東西？")

    return "OK"


@app.route("/show-fsm", methods=["GET"])
def show_fsm():
    fake_machine.get_graph().draw("fsm.png", prog="dot", format="png")
    return send_file("fsm.png", mimetype="image/png")


if __name__ == "__main__":
    port = os.environ.get("PORT", 8000)
    app.run(host="0.0.0.0", port=port, debug=True)
