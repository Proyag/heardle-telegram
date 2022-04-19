import os
import logging
import youtube_dl
from pydub import AudioSegment

class Song:
    def __init__(self, song_info: dict):
        self.title = song_info['title']
        self.artist = song_info['artists'][0]['name']
        self.id = song_info['videoId']
        self.url = f"https://music.youtube.com/watch?v={self.id}"

    def get_id(self) -> str:
        """Get the unique ID for song"""
        return self.id

    def get_url(self) -> str:
        """Get Youtube Music URL for song"""
        return self.url

    def get_artist(self) -> str:
        """Get the artist"""
        return self.artist

    def get_title(self) -> str:
        """Get the song title"""
        return self.title

    def __str__(self):
        return f"{self.artist}; {self.title}"

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
        """Download a song from Youtube Music"""
        with youtube_dl.YoutubeDL(self.dl_opts) as ydl:
            ydl.download([song.get_url()])

    def generate_clips(self):
        """Generate shorter clips from the full song"""
        full_song = AudioSegment.from_mp3(self.full_song)
        logging.info(f"Full song length: {full_song.duration_seconds}")
        logging.info(f"Generating clips of lengths (in seconds): {','.join(map(str, self.clip_durations))}")
        for l in self.clip_durations:
            clip = full_song[:l*1000]
            clip.export(os.path.join(self.song_dir, f"clip_{l:d}s.mp3"), format='mp3')

    def prepare_song(self, song):
        """Download song and generate clips to prepare a new game"""
        self.download_song(song)
        self.generate_clips()

    def get_clip_file(self, clip_num=None):
        """Get a specific clip of the song"""
        if clip_num is not None and clip_num < len(self.clip_durations):
            return os.path.join(self.song_dir, f"clip_{self.clip_durations[clip_num]:d}s.mp3")
        else:
            return self.full_song
