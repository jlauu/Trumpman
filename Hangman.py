#!/usr/bin/env python3
from string import ascii_lowercase
from enum import Enum

class InvalidGuess(Exception):
    """Exception for badly formed guesses"""
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

class Hangman:
    """Representation of a game session"""
    MAX_GUESSES = 10
    class Status(Enum):
        ongoing = 0
        won = 1
        lost = 2

    def __init__(self, answer, alphabet=ascii_lowercase):
        self.answer = answer.lower().strip()
        self.alphabet = set(alphabet)
        self.guesses = 0
        self.status = Hangman.Status.ongoing
        self.letters_left = set(answer)
        self.letters_guessed = set()

    def guess(self, letter):
        """Advances the game state given the next guess"""
        letter = letter.lower()
        if self.status != Hangman.Status.ongoing:
            raise InvalidGuess('Game is already over', payload=self.get_state())
        if letter not in self.alphabet or len(letter) != 1:
            raise InvalidGuess('Invalid guess given', payload=self.get_state())
        if letter in self.letters_guessed:
            raise InvalidGuess('Guess already made', payload=self.get_state())
        letter = set(letter)
        self.letters_guessed |= letter
        self.letters_left -= letter
        self.guesses += 1
        return self.get_state()

    def get_state(self):
        """Returns an object representing the current game state"""
        if len(self.letters_left) == 0:
            self.status = Hangman.Status.won
        elif self.guesses >= Hangman.MAX_GUESSES:
            self.status = Hangman.Status.lost
        return {
          'status': self.status.name,
          'guesses_left': Hangman.MAX_GUESSES - self.guesses,
          'letters_guessed': list(self.letters_guessed),
          'word_with_blanks': self.get_word_with_blanks()
        }

    def get_word_with_blanks(self):
        return ''.join(' ' if c in self.letters_left else c \
                       for c in self.answer)

    def __repr__(self):
        return '<Hangman {0!s}>'.format(self.get_state())

