import os
import logging
import youtube_dl

logging.basicConfig(level=logging.INFO)

class ClipGenerator:
    dl_opts = {
        'format': 'bestaudio',
        'outtmpl': 'song_clips/song_full.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }

    def __init__(self):
        pass

    def prepare_directory(self):
        song_dir = os.path.dirname(self.dl_opts['outtmpl'])
        if os.path.exists(song_dir):
            logging.info(f"Emptying directory {song_dir}")
            for filename in os.listdir(song_dir):
                os.remove(os.path.join(song_dir, filename))
        # Create the song_clips directory
        elif not os.path.exists(song_dir):
            logging.info(f"Creating directory {song_dir}")
            os.mkdir(song_dir)

    def download_song(self, song):
        self.prepare_directory()
        # Download
        with youtube_dl.YoutubeDL(self.dl_opts) as ydl:
            ydl.download([song.get_url()])

    def generate_clips(song):
        pass
