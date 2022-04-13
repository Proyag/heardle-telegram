import logging
from time import time

class Game:
    """One instance of a whole game, i.e. one song"""
    def __init__(self, song) -> None:
        self.start_time = time()
        self.song = song
        self.user_games: dict[int, UserGame] = {}
        logging.info(f"Launching game at {self.start_time}")

    def __hash__(self):
        return hash(repr(self.song) + str(self.start_time))

    def check_user_played(self, user_id) -> bool:
        """Check if a user has started today's game"""
        return user_id in self.user_games.keys()

    def new_user_game(self, user_id) -> None:
        self.user_games[user_id] = UserGame(user_id, self.__hash__())

class UserGame:
    """One user playing one game"""
    def __init__(self, user_id, game_id) -> None:
        self.user_id = user_id
        self.game_id = game_id
        self.guesses = 0
        self.done = False

    def __hash__(self):
        return hash(str(self.user_id) + str(self.game_id))

    def get_id(self) -> int:
        """Get user ID"""
        return self.user_id

    def get_score(self) -> int:
        """Get the number of guesses taken by player"""
        return self.guesses
