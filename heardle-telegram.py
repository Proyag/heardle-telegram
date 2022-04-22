import argparse
import json
import logging
from telegram import (
    User,
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
    CallbackQueryHandler,
    ChosenInlineResultHandler
)
from heardle_telegram.ytmusic_library import Library
from heardle_telegram.process_song import ClipGenerator
from heardle_telegram.game import Game, UserGame

def start(update: Update, context: CallbackContext) -> None:
    """Start a game when the command /start is issued."""
    logging.info("/start command received")
    user = update.effective_user
    if game.check_user_started(user['id']):
        if game.get_user_game(user['id']).check_done():
            update.message.reply_markdown_v2(
                f"Game already finished for {user.mention_markdown_v2()}"
            )
            return
        else:
            logging.info(f"{user['username']} already started")
            update.message.reply_markdown_v2(
                f"{user.mention_markdown_v2()} has already started this game"
            )
    else:
        game.new_user_game(user)
        logging.info(f"Started game {hash(game)} for user {user['username']}")
        update.message.reply_markdown_v2(
            f"Started game for {user.mention_markdown_v2()}"
        )
        # Start with the first (shortest) clip
        update.message.reply_audio(
            open(game.get_clip_file(0), 'rb'),
            caption="Clip #1"
        )
    show_options(user)
    
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

def show_options(user: User) -> None:
    """Show options as an inline keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("Pass", callback_data="/pass"),
            InlineKeyboardButton("Give up", callback_data="/giveup")
        ],
        [
            InlineKeyboardButton("Guess", switch_inline_query_current_chat="Guess: ")
        ]
    ]
    user.send_message("Choose an option", reply_markup=InlineKeyboardMarkup(keyboard))

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
        user.send_audio(
            open(game.get_clip_file(user_game.get_guesses()), 'rb'),
            caption=f"Clip #{user_game.get_guesses() + 1}"
        )
        show_options(user)
    else:
        # Game over
        user_game.set_defeat()
        game.register_final_score(user['id'], user_game.get_guesses() + 1)
        user.send_message(
            f"{user.mention_markdown_v2()} lost the game",
            parse_mode='MarkdownV2'
        )
        send_answer(user, game)

def pass_move(update: CallbackQuery, context: CallbackContext) -> None:
    """Pass and get next clip"""
    logging.info("/pass command received")
    user = update.from_user
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
    user_game = game.get_user_game(user['id'])
    if user_game.check_done():
        user.send_message(
            f"Game already finished for {user.mention_markdown_v2()}",
            parse_mode='MarkdownV2'
        )
        return
    guess_id = update.chosen_inline_result.result_id
    logging.info(f"Guess from user {user['username']}: {guess_id}")
    if game.check_guess(guess_id) == (True, True):
        user_game.set_success()
        game.register_final_score(user['id'], user_game.get_guesses() + 1)
        user.send_message(
            f"{user.mention_markdown_v2()} finished in {user_game.get_guesses() + 1} moves\!",
            parse_mode='MarkdownV2'
        )
        send_answer(user, game)
    else:
        if game.check_guess(guess_id)[0]:
            user.send_message("You got the artist right")
        elif game.check_guess(guess_id)[1]:
            user.send_message("You got the title right")
        else:
            user.send_message("Wrong answer")
        increment_move(update, game, user_game)

def escape_answer_for_markdown(answer) -> tuple[str, str]:
    """Escape characters in answer for markdown response"""
    return (answer[0].replace('-', '\-').replace('(', '\(').replace(')', '\)').replace('.', '\.').replace(';', ' \-'), answer[1])

def send_answer(user: User, game: Game) -> None:
    """Sends the final answer"""
    answer = escape_answer_for_markdown(game.get_song_answer())
    user.send_message(
        f"The answer is: [{answer[0]}]({answer[1]})",
        disable_web_page_preview=True,
        parse_mode='MarkdownV2'
    )

def give_up(update: CallbackQuery, context: CallbackContext) -> None:
    """Give up and show the answer"""
    logging.info("/giveup command received")
    user = update.from_user
    user_game = game.get_user_game(user['id'])
    if user_game.check_done():
        update.message.reply_markdown_v2(
            f"Game already finished for {user.mention_markdown_v2()}"
        )
    else:
        user_game.set_defeat()
        game.register_final_score(user['id'], 7)
    send_answer(user, game)

def suggest_songs(update: Update, context: CallbackContext) -> None:
    """Autocomplete suggestions for guesses"""
    # Strip the first 7 characters: "Guess: "
    query = update.inline_query.query[7:]
    
    if query == "":
        return

    results = []
    for suggestion in library.get_song_suggestions(query):
        results.append(
            InlineQueryResultArticle(
                id=suggestion.get_id(),
                title=str(suggestion).replace(';', ' -'),
                input_message_content=InputTextMessageContent(f"Guess: {str(suggestion)}")
            )
        )

    update.inline_query.answer(results, auto_pagination=True)

def parse_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        description="Launch a game of heardle-telegram",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=True
    )
    arg_parser.add_argument(
        "--no-notify",
        action='store_true',
        help="Don't send notifications to subscribed telegram chats"
    )
    arg_parser.add_argument(
        "--log-file",
        default="logs/game.log",
        help="File to write logs"
    )
    return arg_parser.parse_args()


def main() -> None:
    logging.basicConfig(
        format='[%(asctime)s][%(levelname)s] %(message)s',
        datefmt='%d/%m/%Y %H:%M:%S',
        level=logging.INFO
    )
    options = parse_args()
    logging.getLogger().addHandler(logging.FileHandler(options.log_file))

    global library
    library = Library()
    # Pick a random song
    song = library.get_random_song()
    # Download the song and generate clips
    clip_generator = ClipGenerator()
    clip_generator.prepare_song(song)

    global game
    game = Game(song, clip_generator, library)

    # Configure Telegram API
    telegram_config = json.load(open('telegram_config.json'))
    telegram_api_token = telegram_config['api_token']

    updater = Updater(token=telegram_api_token)
    dispatcher = updater.dispatcher

    # Command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CommandHandler("status", status))
    dispatcher.add_handler(InlineQueryHandler(suggest_songs, pattern='Guess: .+'))
    dispatcher.add_handler(ChosenInlineResultHandler(guess))
    dispatcher.add_handler(CallbackQueryHandler(keyboard_callback))

    # Start the Bot
    updater.start_polling(drop_pending_updates=True)
    if not options.no_notify:
        for subscriber in telegram_config['subscribers']:
            updater.bot.send_message(
                chat_id=subscriber,
                text=f"Launched new game"
            )
    updater.idle()

    # End game
    scoreboard = game.show_scoreboard()
    logging.info(f"Final scores:\n{scoreboard}")
    # Send scoreboard to everyone who played
    for user_id in game.get_played_users():
        updater.bot.send_message(
            chat_id=user_id,
            text=f"Final scores:\n```\n{scoreboard}\n```",
            parse_mode='MarkdownV2'
        )

if __name__ == '__main__':
    main()
