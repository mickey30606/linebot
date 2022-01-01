import urllib.request
import re
from bs4 import BeautifulSoup

youtube_watch_url = "https://www.youtube.com/watch?v="
youtube_img_url_h = "https://i.ytimg.com/vi/"
youtube_img_url_t = "/hqdefault.jpg"

def youtube_crawler(music_name):
    html = urllib.request.urlopen("https://www.youtube.com/results?search_query="+urllib.parse.quote(music_name))
    video_name = []
    video_url = []
    video_img = []
    check = 0
    for i in re.finditer((r"watch\?v=(\S{11})"), html.read().decode()):
        check += 1
        tmp_url = youtube_watch_url + str(i.groups()[0])
        video_url.append(tmp_url)
        video_img.append(youtube_img_url_h + str(i.groups()[0]) + youtube_img_url_t)
        html2 = urllib.request.urlopen(tmp_url)
        for j in re.finditer((r"<title>(.*?)</title>"), html2.read().decode()):
            video_name.append(j.groups()[0])
            break
        if check == 3:
            break

    return video_name, video_url, video_img

def test_crawler(music_name):
    video_url = []
    html = urllib.request.urlopen("https://www.youtube.com/results?search_query="+urllib.parse.quote(music_name))
    check =0
    for i in re.finditer(r"(?:watch\?v=)(\S{11})", html.read().decode()):
        check += 1
        video_url.append(i.groups()[0])
        if check == 3:
            break

    print(video_url)


if __name__ == "__main__":
    youtube_crawler("飛鳥和蟬")
