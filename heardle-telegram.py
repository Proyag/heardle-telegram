import logging
logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO)
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from heardle_telegram.ytmusic_library import Library
from heardle_telegram.process_song import ClipGenerator
from heardle_telegram.game import Game, UserGame

def start(update: Update, context: CallbackContext) -> None:
    """Start a game when the command /start is issued."""
    logging.info("/start command received")
    user = update.effective_user
    if game.check_user_started(user['id']):
        logging.info(f"{user['id']} already started")
        update.message.reply_markdown_v2(
            f"{user.mention_markdown_v2()} has already started this game"
        )
    else:
        game.new_user_game(user['id'])
        logging.info(f"Started game {hash(game)} for user {user['id']}")
        update.message.reply_markdown_v2(
            f"Started game for {user.mention_markdown_v2()}"
        )
        # Start with the first (shortest) clip
        update.message.reply_audio(
            open(game.get_clip_file(0), 'rb'),
            caption="Clip #1"
        )
    
def help(update: Update, context: CallbackContext) -> None:
    """Help message"""
    logging.info("/help command received")
    update.message.reply_text(
        "Heardle telegram bot\n"
        "/help: Get this help message\n"
        "/start: Start playing current game\n"
        "/status: Check whether game is running\n"
        "/pass: Pass move and get the next clip\n"
        "/guess: Take a guess in the format Artist;Song\n"
        "/giveup: Give up and see the answer\n"
    )

def status(update: Update, context: CallbackContext) -> None:
    """Check whether game is running and current game ID"""
    logging.info("/status command received")
    update.message.reply_text(f"Game {hash(game)} running")

def increment_move(update: Update, game: Game, user_game: UserGame) -> None:
    """Register a passed move when player passes or guesses wrong"""
    user = update.effective_user
    user_game.pass_move()
    if user_game.get_guesses() < 6:
        # Send next clip
        update.message.reply_audio(
            open(game.get_clip_file(user_game.get_guesses()), 'rb'),
            caption=f"Clip #{user_game.get_guesses() + 1}"
        )
    else:
        # Game over
        user_game.set_defeat()
        update.message.reply_markdown_v2(
            f"{user.mention_markdown_v2()} lost the game"
        )
        update.message.reply_audio(
            open(game.get_clip_file(user_game.get_guesses()), 'rb'),
            caption="Full song"
        )
        send_answer(update, game)

def not_started_message(update: Update) -> None:
    """Reply that player has not started"""
    user = update.effective_user
    logging.info(f"{user['id']} has not started this game")
    update.message.reply_markdown_v2(
        f"{user.mention_markdown_v2()} has not started this game"
    )

def pass_move(update: Update, context: CallbackContext) -> None:
    """Pass and get next clip"""
    logging.info("/pass command received")
    user = update.effective_user
    if not game.check_user_started(user['id']):
        not_started_message(update)
        return
    user_game = game.get_user_game(user['id'])
    if user_game.check_done():
        update.message.reply_markdown_v2(
            f"Game already finished for {user.mention_markdown_v2()}"
        )
        return
    increment_move(update, game, user_game)

def guess(update: Update, context: CallbackContext) -> None:
    """Take a guess"""
    logging.info("/guess command received")
    user = update.effective_user
    if not game.check_user_started(user['id']):
        not_started_message(update)
        return
    user_game = game.get_user_game(user['id'])
    if user_game.check_done():
        update.message.reply_markdown_v2(
            f"Game already finished for {user.mention_markdown_v2()}"
        )
        return
    guess_str = ' '.join(context.args)
    logging.info(f"Guess from user {user['id']}: {guess_str}")
    if game.check_guess(guess_str) == (True, True):
        user_game.set_success()
        update.message.reply_markdown_v2(
            f"{user.mention_markdown_v2()} finished in {user_game.get_guesses() + 1} moves\!"
        )
        send_answer(update, game)
    else:
        if game.check_guess(guess_str)[0]:
            update.message.reply_markdown_v2(
                f"You got the artist right"
            )
        elif game.check_guess(guess_str)[1]:
            update.message.reply_markdown_v2(
                f"You got the title right"
            )
        else:
            update.message.reply_markdown_v2(
                f"Wrong answer"
            )
        increment_move(update, game, user_game)

def escape_answer_for_markdown(answer) -> tuple[str, str]:
    """Escape characters in answer for markdown response"""
    return (answer[0].replace('-', '\-').replace('(', '\(').replace(')', '\)').replace('.', '\.'), answer[1])

def send_answer(update: Update, game: Game) -> None:
    """Sends the final answer"""
    answer = escape_answer_for_markdown(game.get_song_answer())
    update.message.reply_markdown_v2(
        f"The answer is: [{answer[0]}]({answer[1]})",
        disable_web_page_preview=True
    )

def give_up(update: Update, context: CallbackContext) -> None:
    """Give up and show the answer"""
    logging.info("/giveup command received")
    user = update.effective_user
    if not game.check_user_started(user['id']):
        not_started_message(update)
        return
    user_game = game.get_user_game(user['id'])
    if user_game.check_done():
        update.message.reply_markdown_v2(
            f"Game already finished for {user.mention_markdown_v2()}"
        )
    else:
        user_game.set_defeat()
    send_answer(update, game)


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

if __name__ == '__main__':
    main()
