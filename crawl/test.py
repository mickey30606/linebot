import urllib
import requests
from bs4 import BeautifulSoup
def youtube_page(keyword):
    url = "https://www.youtube.com/results?search_query="+urllib.parse.quote(keyword)
    request = requests.get(url)
    content = request.content
    soup = BeautifulSoup(content, "html.parser")
    for vid in soup.select(".yt-lockup-video"):
        data = vid.select("a[rel='spf-prefetch']")
        print(data[0].get("title"))

if __name__ == "__main__":
    youtube_page("飛鳥和蟬")
