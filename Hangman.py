#!/usr/bin/env python3
from random import choice
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

class HangmanClient:
    """A client game session"""
    MAX_GUESSES = 10
    BLANK_CHAR = '_'
    class Status(Enum):
        ongoing = 0
        won = 1
        lost = 2

    def __init__(self):
        """Given a vocabulary to draw a random word, 
        returns a new game session"""
        self.won = 0
        self.lost = 0
        self.answers = set()

    def new_game(self, answer, alphabet):
        self.answer = answer.lower().strip()
        self.alphabet = set(a.lower().strip() for a in alphabet)
        self.incorrect_guesses = 0
        self.status = HangmanClient.Status.ongoing
        self.letters_left = set(self.answer)
        self.letters_guessed = set()

    def guess(self, letter):
        """Advances the game state given the next guess"""
        letter = letter.lower()
        if self.status != HangmanClient.Status.ongoing:
            raise InvalidGuess('Game is already over', payload=self.get_state())
        if letter not in self.alphabet or len(letter) != 1:
            raise InvalidGuess(
                "Invalid guess '{}' was made".format(letter), 
                payload=self.get_state())
        if letter in self.letters_guessed:
            raise InvalidGuess(
              "You already guessed '{}'".format(letter), 
               payload=self.get_state())
        if letter not in self.letters_left:
            self.incorrect_guesses += 1
        letter = set(letter)
        self.letters_guessed |= letter
        self.letters_left -= letter
        status = self._compute_status(len(self.letters_left), \
                                      self.incorrect_guesses)
        if status == HangmanClient.Status.won:
            self.won += 1
        elif status == HangmanClient.Status.lost:
            self.lost += 1
        self.status = status
        return self.get_state()

    def get_state(self):
        """Returns an object representing the current game state"""
        payload = {
          'incorrect_guesses': self.incorrect_guesses,
          'max_guesses': HangmanClient.MAX_GUESSES,
          'status': self.status.name,
          'guesses_left': HangmanClient.MAX_GUESSES - self.incorrect_guesses,
          'letters_guessed': list(self.letters_guessed),
          'word_with_blanks': self._to_blanks(self.answer),
          'won': self.won,
          'lost': self.lost
        }
        if self.status != HangmanClient.Status.ongoing:
            payload.update({
                'letters_left': list(self.letters_left),
                'answer': self.answer
            })
        return payload

    def _compute_status(self, letters_left, guesses):
        if letters_left <= 0:
            return HangmanClient.Status.won
        elif guesses >= HangmanClient.MAX_GUESSES:
            return HangmanClient.Status.lost
        else:
            return HangmanClient.Status.ongoing

    def _to_blanks(self, word):
        return ''.join( \
          HangmanClient.BLANK_CHAR if c in self.letters_left else c \
          for c in word)

    def __repr__(self):
        return '<Hangman {0!s}>'.format(self.get_state())

