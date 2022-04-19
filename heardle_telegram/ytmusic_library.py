import logging
import os
import json
import random
from ytmusicapi import YTMusic
from .process_song import Song

class Library:
    def __init__(self, force_update=False) -> None:
        self.songs = dict()
        self.cache = 'library_cache'
        if force_update:
            self.update_cache()
        else:
            self.check_update_cache()

    def check_update_cache(self) -> None:
        """Update cache if it's non-existent/empty and load it"""
        if not os.path.exists(self.cache) or os.stat(self.cache).st_size == 0:
            self.update_cache()
        self.read_cache()

    def update_cache(self) -> None:
        """Update cache of songs from YTMusic"""
        logging.info("Updating cache from YTMusic")
        # Authenticate
        ytmusic = YTMusic('headers_auth.json')
        songs = ytmusic.get_library_songs(limit=999999)
        with open(self.cache, 'w') as cache_fh:
            for song in songs:
                json.dump(song, cache_fh)
                cache_fh.write('\n')

    def read_cache(self) -> list:
        """Read song list from cache"""
        logging.info(f"Reading cache from {self.cache}")
        with open(self.cache, 'r') as cache_fh:
            for line in cache_fh:
                line = line.strip()
                song_entry = json.loads(line)
                self.songs[song_entry['videoId']] = Song(song_entry)

    def get_artist_by_song_id(self, id) -> str:
        """Get artist for a specific song ID"""
        return self.songs[id].get_artist()

    def get_title_by_song_id(self, id) -> str:
        """Get title for a specific song ID"""
        return self.songs[id].get_title()

    def get_song_list(self) -> list:
        """Get list of songs"""
        return self.songs

    def get_random_song(self) -> Song:
        """Get a random song"""
        song = random.choice(list(self.songs.values()))
        logging.info(f"Chosen song: {song}")
        return song

    def get_song_suggestions(self, substr, max_results=10):
        """Find songs (artist + title) matching a substring"""
        n_results = 0
        substr = substr.lower()
        logging.info(f"Suggesting songs matching {substr}")
        for (_, song) in self.songs.items():
            if substr in str(song).lower():
                n_results += 1
                yield song
                if n_results >= max_results:
                    break
