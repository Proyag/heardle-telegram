import os
import logging
import youtube_dl
from pydub import AudioSegment

logging.basicConfig(level=logging.INFO)

class Song:
    def __init__(self, song_info: dict):
        self.title = song_info['title']
        self.artist = song_info['artists'][0]['name']
        self.id = song_info['videoId']
        self.url = f"https://music.youtube.com/watch?v={self.id}"

    def get_url(self) -> str:
        return self.url

    def __str__(self):
        return f"{self.title} - {self.artist}"

    def __repr__(self):
        return f"Song: {self.title}; Artist: {self.artist}; ID: {self.id}"

class ClipGenerator:
    song_dir = 'song_clips'
    full_song = os.path.join(song_dir, 'song_full.mp3')

    dl_opts = {
        'format': 'bestaudio',
        'outtmpl': os.path.join(song_dir, 'song_full.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }

    clip_durations = [1, 2, 3, 5, 10, 20]

    def __init__(self):
        if os.path.exists(self.song_dir):
            logging.info(f"Emptying directory {self.song_dir}")
            for filename in os.listdir(self.song_dir):
                os.remove(os.path.join(self.song_dir, filename))
        # Create the song_clips directory
        elif not os.path.exists(self.song_dir):
            logging.info(f"Creating directory {self.song_dir}")
            os.mkdir(self.song_dir)

    def download_song(self, song):
        # Download
        with youtube_dl.YoutubeDL(self.dl_opts) as ydl:
            ydl.download([song.get_url()])

    def generate_clips(self, song):
        full_song = AudioSegment.from_mp3(self.full_song)
        logging.info(f"Full song length: {full_song.duration_seconds}")
        logging.info(f"Generating clips of lengths (in seconds): {','.join(map(str, self.clip_durations))}")
        for l in self.clip_durations:
            clip = full_song[:l*1000]
            clip.export(os.path.join(self.song_dir, f"clip_{l:d}s.mp3"), format='mp3')
