import os
import logging
import youtube_dl

logging.basicConfig(level=logging.INFO)

SONG_OUTPUT = 'song.%(ext)s'

dl_opts = {
    'format': 'bestaudio',
    'outtmpl': SONG_OUTPUT,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }]
}

def download_song(url):
    # Delete old song just to make sure
    if os.path.exists(SONG_OUTPUT):
        os.remove(SONG_OUTPUT)
    with youtube_dl.YoutubeDL(dl_opts) as ydl:
        ydl.download([url])
