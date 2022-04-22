import logging
logging.basicConfig(
    format='[%(asctime)s][%(levelname)s] %(message)s',
    datefmt='%Y/%m/%d %H:%M:%S',
    level=logging.INFO
)
from heardle_telegram.ytmusic_library import Library

_ = Library(force_update=True)