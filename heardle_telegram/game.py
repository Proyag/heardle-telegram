import logging
from time import time

class UserGame:
    """One user playing one game"""
    def __init__(self, user_id, game_id) -> None:
        self.user_id = user_id
        self.game_id = game_id
        self.guesses = 0
        self.defeat = False
        self.success = False

    def __hash__(self):
        return hash(str(self.user_id) + str(self.game_id))

    def get_id(self) -> int:
        """Get user ID"""
        return self.user_id

    def pass_move(self) -> None:
        """User passes; guess used up"""
        self.guesses += 1

    def get_guesses(self) -> int:
        """Get the number of guesses taken by player"""
        return self.guesses

    def set_defeat(self) -> None:
        """Set user game as over"""
        logging.info(f"Setting game over for user {self.user_id}")
        self.defeat = True

    def set_success(self) -> None:
        """Set user game as won"""
        logging.info(f"User {self.user_id} won the game")
        self.success = True

    def check_done(self) -> bool:
        """Check if user game is finished"""
        return self.defeat or self.success

class Game:
    """One instance of a whole game, i.e. one song"""
    def __init__(self, song, clip_generator) -> None:
        self.start_time = time()
        self.song = song
        self.clip_generator = clip_generator
        self.user_games: dict[int, UserGame] = {}
        logging.info(f"Launching game at {self.start_time}")

    def __hash__(self):
        return hash(repr(self.song) + str(self.start_time))

    def check_user_started(self, user_id) -> bool:
        """Check if a user has started today's game"""
        return user_id in self.user_games.keys()

    def new_user_game(self, user_id) -> None:
        """Create a new user game"""
        self.user_games[user_id] = UserGame(user_id, self.__hash__())

    def get_clip_file(self, clip_num) -> str:
        """Get a specific clip of the song"""
        return self.clip_generator.get_clip_file(clip_num)

    def get_user_game(self, user_id) -> UserGame:
        """Get a specific user's game"""
        return self.user_games[user_id]

    def get_song_answer(self) -> tuple[str, str]:
        """Reveal the answer"""
        return (str(self.song), self.song.get_url())
