import logging
from heardle_telegram.ytmusic_library import Library
from heardle_telegram.process_song import Song, ClipGenerator

logging.basicConfig(level=logging.INFO)

# Pick a random song
song = Library().get_random_song()
logging.info(f"Chosen song: {song}")

clip_generator = ClipGenerator()
# Download the song
clip_generator.download_song(song)
# Generate short clips
clip_generator.generate_clips(song)
