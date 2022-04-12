import os
import logging
import youtube_dl

logging.basicConfig(level=logging.INFO)

SONG_OUTPUT = 'song_clips/song_full.%(ext)s'

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
    song_dir = os.path.dirname(SONG_OUTPUT)
    if os.path.exists(SONG_OUTPUT):
        os.remove(SONG_OUTPUT)
    # Create the song_clips directory
    elif not os.path.exists(song_dir):
        os.mkdir(song_dir)
    # Download
    with youtube_dl.YoutubeDL(dl_opts) as ydl:
        ydl.download([url])
