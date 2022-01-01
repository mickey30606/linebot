from pydub import AudioSegment

def Cut(originfile, start, end, targetfile):
    song = AudioSegment.from_mp3(originfile)
    song[start:end].export(targetfile)

if __name__ == "__main__":
    Cut("tmp.mp3", 33*1000, 70*1000, "output.mp3")
    tmpsong = AudioSegment.from_mp3("output.mp3")
    print((len(tmpsong) / 1000.0))
