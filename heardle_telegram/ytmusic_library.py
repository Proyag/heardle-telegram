import logging
import os
import json
import random
from ytmusicapi import YTMusic
from .process_song import Song

logging.basicConfig(level=logging.INFO)

class Library:
    def __init__(self) -> None:
        self.songs = []
        self.cache = 'library_cache'
        self.check_update_cache()

    def check_update_cache(self) -> None:
        # If empty, update
        # TODO: Maybe refresh if the file is old? But can't do that if we want to combine libraries
        if not os.path.exists(self.cache) or os.stat(self.cache).st_size == 0:
            self.update_cache()
        self.read_cache()

    def update_cache(self) -> None:
        logging.info("Updating cache from YTMusic")
        # Authenticate
        ytmusic = YTMusic('headers_auth.json')
        songs = ytmusic.get_library_songs(limit=999999)
        with open(self.cache, 'w') as cache_fh:
            for song in songs:
                json.dump(song, cache_fh)
                cache_fh.write('\n')

    def read_cache(self) -> list:
        logging.info(f"Reading cache from {self.cache}")
        with open(self.cache, 'r') as cache_fh:
            for line in cache_fh:
                line = line.strip()
                self.songs.append(Song(json.loads(line)))


    def get_song_list(self) -> list:
        return self.songs

    def get_random_song(self) -> Song:
        return random.choice(self.songs)
