import logging
logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO)

from heardle_telegram.ytmusic_library import Library
from heardle_telegram.process_song import ClipGenerator

if __name__ == '__main__':
    # Pick a random song
    song = Library().get_random_song()

    # Download the song and generate clips
    clip_generator = ClipGenerator().prepare_song(song)
