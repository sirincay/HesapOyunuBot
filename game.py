# -*- coding: utf-8 -*-
import random
from datetime import datetime, timedelta

import settings
import time


class User:
    def __init__(self, user_id, username):
        self.user_id: int = user_id
        self.username: str = username
        self.puan = 0

    def update_puan(self):
        self.puan += 1

    def get_puan(self):
        return self.puan

    def get_puan_str(self):
        return self.username + ": " + str(self.puan) + " Puan🎈\n"


class Game:
    def __init__(self):
        self._ogretmen_user_id = 0
        self._word_list = []
        self._current_word = ''
        self._game_started = False
        self._users = {}
        self.winner = 0
        self._ogretmen_start_time: datetime = datetime.now()
        self.timedelta = 60

    def start(self):
        self._word_list = settings.word_list.copy()
        self._ogretmen_user_id = 0
        self._game_started = True
        self._users = {}

    def is_game_started(self):
        return self._game_started

    def get_ogretmen_time_left(self) -> int:
        return self.timedelta - (datetime.now() - self._ogretmen_start_time).seconds

    def is_ogretmen_time_left(self):
        return (datetime.now() - self._ogretmen_start_time).seconds >= self.timedelta

    def set_ogretmen(self, user_id):
        self._create_word()
        self._ogretmen_user_id = user_id
        self._ogretmen_start_time = datetime.now()

    def is_ogretmen(self, user_id: int):
        return user_id == self._ogretmen_user_id

    def _create_word(self):
        self._current_word = random.choice(self._word_list)
        del self._word_list[self._word_list.index(self._current_word)]

    def get_word(self, user_id: int):
        if self.is_ogretmen(user_id):
            return self._current_word
        else:
            return ''

    def change_word(self, user_id: int):
        if self.is_ogretmen(user_id):
            self._create_word()
            return self._current_word
        else:
            return ''

    def is_word_answered(self, user_id, text):
        if not self.is_ogretmen(user_id):
            if text.lower() == self._current_word.lower():
                self._ogretmen_user_id = user_id
                return True
        return False

    def get_current_word(self):
        return self._current_word

    def update_puan(self, user_id, username):
        if user_id not in self._users:
            self._users[user_id] = User(user_id, username)

        self._users[user_id].update_puan()

    def get_str_puan(self):
        puan_str = ''
        for user_id in self._users:
            puan_str += self._users[user_id].get_puan_str()

        return puan_str
