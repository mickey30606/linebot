import os
import json

from linebot import LineBotApi, WebhookParser
from linebot.models import MessageEvent, TextMessage, TextSendMessage, AudioSendMessage, FlexSendMessage


channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)


def send_text_message(reply_token, text):
    print("send text message")
    for i in text:
        print(i)
    line_bot_api = LineBotApi(channel_access_token)
    message = []
    for i in text:
        message.append(TextSendMessage(text=i))
    line_bot_api.reply_message(reply_token, message)

    return "OK"

def push_text_message(user_id, text):
    line_bot_api = LineBotApi(channel_access_token)
    message = []
    for i in text:
        message.append(TextSendMessage(text=i))
    line_bot_api.push_message(user_id, message)

    return "OK"


def send_audio_message(reply_token, music_url, duration, targetfile, text):
    message = []
    url = str(music_url) + '/' + targetfile
    line_bot_api = LineBotApi(channel_access_token)
    message.append(AudioSendMessage(url, duration*1000))
    with open("./download_link.json") as f:
        data = json.load(f)
    data['body']['contents'][0]['action']['uri'] = url
    message.append(FlexSendMessage(alt_text='hello', contents=data))
    for i in text:
        message.append(TextSendMessage(text=i))
    line_bot_api.reply_message(reply_token, message)

    return "OK"

def push_audio_message(user_id, music_url, duration, targetfile, text):
    message = []
    url = str(music_url) + '/' + targetfile
    line_bot_api = LineBotApi(channel_access_token)
    message.append(AudioSendMessage(url, duration*1000))
    with open("./download_link.json") as f:
        data = json.load(f)
    data['body']['contents'][0]['action']['uri'] = url
    message.append(FlexSendMessage(alt_text='hello', contents=data))
    for i in text:
        message.append(TextSendMessage(text=i))
    line_bot_api.push_message(user_id, message)

    return "OK"

def send_flex_message(reply_token, video_title, video_url, video_img, text):
    message = []
    with open('./flex_message.json') as f:
        data = json.load(f)

    for i in range(0, 3):
        print(video_img[i])
        print(video_url[i])
        print(video_title[i])
        data['body']['contents'][i]['contents'][0]['text'] = str(video_title[i])
        data['body']['contents'][i]['contents'][0]['action']['uri'] = str(video_url[i])
        data['body']['contents'][i]['contents'][1]['url'] = str(video_img[i])
        data['body']['contents'][i]['contents'][1]['action']['uri'] = str(video_url[i])

    message.append(FlexSendMessage(alt_text='hello', contents=data))
    for i in text:
        message.append(TextSendMessage(text=i))
    # flex_message = FlexSendMessage(alt_text='hello', contents=data)
    line_bot_api = LineBotApi(channel_access_token)
    line_bot_api.reply_message(reply_token, message)

    return "OK"

def push_flex_message(user_id, video_title, video_url, video_img, text):
    message = []
    with open('./flex_message.json') as f:
        data = json.load(f)

    for j in range(0, 3):
        i = j
        if len(video_title) < 3:
            i = len(video_title) - 1
        print(video_img[i])
        print(video_url[i])
        print(video_title[i])
        data['body']['contents'][i]['contents'][0]['text'] = str(video_title[i])
        data['body']['contents'][i]['contents'][0]['action']['uri'] = str(video_url[i])
        data['body']['contents'][i]['contents'][1]['url'] = str(video_img[i])
        data['body']['contents'][i]['contents'][1]['action']['uri'] = str(video_url[i])

    message.append(FlexSendMessage(alt_text='hello', contents=data))
    for i in text:
        message.append(TextSendMessage(text=i))
    # flex_message = FlexSendMessage(alt_text='hello', contents=data)
    line_bot_api = LineBotApi(channel_access_token)
    line_bot_api.push_message(user_id, message)

    return "OK"

def download_music(targetfile, message_id):
    targetfile = "./music/"+targetfile
    line_bot_api = LineBotApi(channel_access_token)
    print(message_id)
    message_content = line_bot_api.get_message_content(message_id)
    with open(targetfile, 'wb') as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)

    return "OK"





"""
def send_image_url(id, img_url):
    pass

def send_button_message(id, text, buttons):
    pass
"""
