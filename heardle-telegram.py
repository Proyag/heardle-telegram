from ast import Call
import logging
from uuid import uuid4
logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO)
from telegram import (
    CallbackQuery,
    InputTextMessageContent,
    Update,
    InlineQueryResultArticle,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
    InlineQueryHandler,
    CallbackQueryHandler
)
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
    show_options(update)
    
def help(update: Update, context: CallbackContext) -> None:
    """Help message"""
    logging.info("/help command received")
    update.message.reply_text(
        "Heardle telegram bot\n"
        "/help: Get this help message\n"
        "/start: Start playing current game\n"
        "/status: Check whether game is running\n"
        "Play using the chat buttons"
    )

def status(update: Update, context: CallbackContext) -> None:
    """Check whether game is running and current game ID"""
    logging.info("/status command received")
    update.message.reply_text(f"Game {hash(game)} running")

def show_options(update: Update) -> None:
    """Show options as an inline keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("Pass", callback_data="/pass"),
            InlineKeyboardButton("Give up", callback_data="/giveup")
        ],
        [
            InlineKeyboardButton("Guess", switch_inline_query_current_chat="/guess ")
        ]
    ]
    update.message.reply_text("Choose an option", reply_markup=InlineKeyboardMarkup(keyboard))

def keyboard_callback(update: Update, context: CallbackContext) -> None:
    if update.callback_query.data == "/pass":
        pass_move(update.callback_query, context)
    elif update.callback_query.data == "/giveup":
        give_up(update.callback_query, context)

def increment_move(update: CallbackQuery|Update, game: Game, user_game: UserGame) -> None:
    """Register a passed move when player passes or guesses wrong"""
    if hasattr(update, 'effective_user'):
        user = update.effective_user
    else:
        user = update.from_user
    user_game.pass_move()
    if user_game.get_guesses() < 6:
        # Send next clip
        update.message.reply_audio(
            open(game.get_clip_file(user_game.get_guesses()), 'rb'),
            caption=f"Clip #{user_game.get_guesses() + 1}"
        )
        show_options(update)
    else:
        # Game over
        user_game.set_defeat()
        update.message.reply_markdown_v2(
            f"{user.mention_markdown_v2()} lost the game"
        )
        send_answer(update, game)

def not_started_message(update: Update) -> None:
    """Reply that player has not started"""
    user = update.from_user
    logging.info(f"{user['id']} has not started this game")
    update.message.reply_markdown_v2(
        f"{user.mention_markdown_v2()} has not started this game"
    )

def pass_move(update: CallbackQuery, context: CallbackContext) -> None:
    """Pass and get next clip"""
    logging.info("/pass command received")
    user = update.from_user
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
    return (answer[0].replace('-', '\-').replace('(', '\(').replace(')', '\)').replace('.', '\.').replace(';', ' \-'), answer[1])

def send_answer(update: Update, game: Game) -> None:
    """Sends the final answer"""
    answer = escape_answer_for_markdown(game.get_song_answer())
    update.message.reply_markdown_v2(
        f"The answer is: [{answer[0]}]({answer[1]})",
        disable_web_page_preview=True
    )
    update.message.reply_audio(
        open(game.get_clip_file(), 'rb'),
        caption="Full song"
    )

def give_up(update: CallbackQuery, context: CallbackContext) -> None:
    """Give up and show the answer"""
    logging.info("/giveup command received")
    user = update.from_user
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

def suggest_songs(update: Update, context: CallbackContext) -> None:
    """Autocomplete suggestions for guesses"""
    # Strip the first 7 letters: "/guess "
    query = update.inline_query.query[7:]
    
    if query == "":
        return

    results = []
    for suggestion in library.get_song_suggestions(query):
        results.append(
            InlineQueryResultArticle(
                id=str(uuid4()),
                title=suggestion.replace(';', ' -'),
                input_message_content=InputTextMessageContent(f"/guess {suggestion}")
            )
        )

    update.inline_query.answer(results)


def main() -> None:
    global library
    library = Library()
    # Pick a random song
    song = library.get_random_song()
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
    dispatcher.add_handler(CommandHandler("guess", guess))
    dispatcher.add_handler(InlineQueryHandler(suggest_songs, pattern='\/guess .+'))
    dispatcher.add_handler(CallbackQueryHandler(keyboard_callback))

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
