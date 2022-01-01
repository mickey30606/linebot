from pytube import YouTube
from moviepy.editor import *
from pydub import AudioSegment

def Cut(originfile, start, end, targetfile):
    song = AudioSegment.from_mp3(originfile)
    song[start:end].export(targetfile)

def GetYoutubeVideo(url, filename):
    YouTube(url).streams.get_highest_resolution().download(filename=filename)

def VideoToMusic(filename, targetname):
    video = VideoFileClip(filename)
    video.audio.write_audiofile(targetname)
    sound = AudioSegment.from_mp3(targetname)
    return sound.duration_seconds

if __name__ == "__main__":
    filename = "tmp.mp4"
    targetname = "tmp.mp3"
    url = "https://www.youtube.com/watch?v=_HxkMKb_EQs"
    GetYoutubeVideo(url, filename)
    print(VideoToMusic(filename, targetname))
