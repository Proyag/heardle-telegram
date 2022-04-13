import logging
logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO)
from heardle_telegram.ytmusic_library import Library

_ = Library(force_update=True)