import logging
logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO)
import json
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from heardle_telegram.ytmusic_library import Library
from heardle_telegram.process_song import ClipGenerator

def start(update: Update, context: CallbackContext) -> None:
    """Start a game when the command /start is issued."""
    logging.info("/start command received")
    
def help(update: Update, context: CallbackContext) -> None:
    """Help message"""
    logging.info("/help command received")
    update.message.reply_text(
        "Heardle telegram bot\n"
        "/start: Start playing current game\n"
        "/status: Check whether game is running\n"
        "/help: Get this help message\n"
    )

def status(update: Update, context: CallbackContext) -> None:
    """Check whether game is running and current game ID"""
    logging.info("/status command received")
    update.message.reply_text("Game running")


def main() -> None:
    # Pick a random song
    song = Library().get_random_song()
    # Download the song and generate clips
    clip_generator = ClipGenerator().prepare_song(song)

    # Configure Telegram API
    telegram_config = json.load(open('telegram_config.json'))

    # https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/echobot.py
    updater = Updater(telegram_config['api_token'])
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CommandHandler("status", status))

    # Start the Bot
    updater.start_polling()
    updater.idle()

    logging.info("New game is up")

if __name__ == '__main__':
    main()