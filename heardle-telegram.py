import random
import logging
from heardle_telegram.ytmusic_library import Library
from heardle_telegram.download_song import download_song

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

songs = Library().get_song_list()

song = Song(random.choice(songs))
logging.info(f"Chosen song: {song}")

# Download the song
download_song(song.get_url())
