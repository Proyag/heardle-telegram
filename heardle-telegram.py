import random
import logging
from heardle_telegram.ytmusic_library import Library
from heardle_telegram.download_song import Song, ClipGenerator

logging.basicConfig(level=logging.INFO)

# Get the full list of songs
songs = Library().get_song_list()

# Pick a random song
song = Song(random.choice(songs))
logging.info(f"Chosen song: {song}")

clip_generator = ClipGenerator()
# Download the song
clip_generator.download_song(song)
# Generate short clips
clip_generator.generate_clips(song)
