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
    class Status(Enum):
        ongoing = 0
        won = 1
        lost = 2

    def __init__(self, vocab, alphabet=ascii_lowercase):
        """Given a vocabulary to draw a random word, 
        returns a new game session"""
        self.vocab = [w for w in vocab if len(w) <= HangmanClient.MAX_GUESSES]
        self.won = 0
        self.lost = 0
        self.answers = set()
        self.alphabet = set(alphabet)
        self.new_game()

    def new_game(self, answer=None):
        if answer is None:
          self.answer = self._draw_word()
        else:
          self.answer = answer.lower().strip()
        self.guesses = 0
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
            self.guesses += 1
        letter = set(letter)
        self.letters_guessed |= letter
        self.letters_left -= letter
        return self.get_state()

    def get_state(self):
        """Returns an object representing the current game state"""
        if len(self.letters_left) == 0 and \
            self.answer not in self.answers:
            self.status = HangmanClient.Status.won
            self.won += 1
        elif self.guesses >= HangmanClient.MAX_GUESSES and \
             self.answer not in self.answers:
            self.status = HangmanClient.Status.lost
            self.lost += 1
        payload = {
          'max_guesses': HangmanClient.MAX_GUESSES,
          'status': self.status.name,
          'guesses_left': HangmanClient.MAX_GUESSES - self.guesses,
          'letters_guessed': list(self.letters_guessed),
          'word_with_blanks': self.get_word_with_blanks(),
          'won': self.won,
          'lost': self.lost
        }
        if self.status != HangmanClient.Status.ongoing:
            payload['letters_left'] = list(self.letters_left)
            payload['answer'] = self.answer
        return payload

    def get_word_with_blanks(self):
        return ''.join('_' if c in self.letters_left else c \
                       for c in self.answer)

    def _draw_word(self):
        return choice(self.vocab)

    def __repr__(self):
        return '<Hangman {0!s}>'.format(self.get_state())

