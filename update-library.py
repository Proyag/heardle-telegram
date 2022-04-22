import logging
import argparse
from heardle_telegram.ytmusic_library import Library

def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        description="Update library for and write to file for heardle-telegram",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=True
    )
    arg_parser.add_argument(
        "--cache",
        default='library_cache',
        help="File to write list of songs to"
    )
    return arg_parser.parse_args()

if __name__ == '__main__':
    logging.basicConfig(
        format='[%(asctime)s][%(levelname)s] %(message)s',
        datefmt='%Y/%m/%d %H:%M:%S',
        level=logging.INFO
    )
    options = parse_args()
    _ = Library(force_update=True, cache=options.cache)
