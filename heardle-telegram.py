import logging
logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO)
import json
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from heardle_telegram.ytmusic_library import Library
from heardle_telegram.process_song import ClipGenerator

def start(update: Update, context: CallbackContext) -> None:
    """Prepare a song when the command /start is issued."""
    logging.info("/start command received")
    update.message.reply_text("Preparing a song... Wait for a READY notification")
    # Pick a random song
    song = Library().get_random_song()
    # Download the song and generate clips
    clip_generator = ClipGenerator().prepare_song(song)
    update.message.reply_text("READY")


def main() -> None:
    # Configure Telegram API
    telegram_config = json.load(open('telegram_config.json'))

    # https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/echobot.py
    updater = Updater(telegram_config['api_token'])
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    # Add command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    # Start the Bot
    updater.start_polling()
    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()