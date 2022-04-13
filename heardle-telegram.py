import logging
logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO)
import json
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from heardle_telegram.ytmusic_library import Library
from heardle_telegram.process_song import ClipGenerator
from heardle_telegram.game import Game

def start(update: Update, context: CallbackContext) -> None:
    """Start a game when the command /start is issued."""
    logging.info("/start command received")
    user = update.effective_user
    if game.check_user_played(user['id']):
        logging.info(f"User {user['id']} already started")
        update.message.reply_markdown_v2(
            f"User {user.mention_markdown_v2()} has already started this game"
        )
    else:
        game.new_user_game(user['id'])
        logging.info(f"Started game {hash(game)} for user {user['id']}")
        update.message.reply_markdown_v2(
            f"Started game for {user.mention_markdown_v2()}"
        )
        # Start with the first (shortest) clip
        update.message.reply_audio(open(game.get_clip_file(0), 'rb'), caption="Clip #1")
    
def help(update: Update, context: CallbackContext) -> None:
    """Help message"""
    logging.info("/help command received")
    update.message.reply_text(
        "Heardle telegram bot\n"
        "/help: Get this help message\n"
        "/start: Start playing current game\n"
        "/status: Check whether game is running\n"
        "/pass: Pass move and get the next clip\n"
        "/guess: Take a guess\n"
        "/giveup: Give up and see the answer\n"
    )

def status(update: Update, context: CallbackContext) -> None:
    """Check whether game is running and current game ID"""
    logging.info("/status command received")
    update.message.reply_text(f"Game {hash(game)} running")

def pass_move(update: Update, context: CallbackContext) -> None:
    """Pass and get next clip"""
    logging.info("/pass command received")

def guess(update: Update, context: CallbackContext) -> None:
    """Take a guess"""
    logging.info("/guess command received")

def give_up(update: Update, context: CallbackContext) -> None:
    """Give up and show the answer"""
    logging.info("/giveup command received")

def main() -> None:
    # Pick a random song
    song = Library().get_random_song()
    # Download the song and generate clips
    clip_generator = ClipGenerator()
    clip_generator.prepare_song(song)

    global game
    game = Game(song, clip_generator)

    # Configure Telegram API
    telegram_api_token = open('telegram_api_token').read().strip()

    updater = Updater(token=telegram_api_token)
    dispatcher = updater.dispatcher

    # Command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CommandHandler("status", status))
    dispatcher.add_handler(CommandHandler("pass", pass_move))
    dispatcher.add_handler(CommandHandler("guess", guess))
    dispatcher.add_handler(CommandHandler("giveup", give_up))

    # Start the Bot
    updater.start_polling()
    updater.idle()

    logging.info("New game is up")

if __name__ == '__main__':
    main()