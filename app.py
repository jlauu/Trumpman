#!/usr/bin/env python3
import os
from string import ascii_lowercase
from random import choice
from flask import Flask, json, g
from Hangman import Hangman, InvalidGuess

# Utils

def generate_game_key():
    return os.urandom(24)

def parse_vocab(filepath, alphabet=ascii_lowercase):
    """Returns a list of words given a file with one word per line"""
    alphabet = set(alphabet)
    with open(filepath, 'r') as f:
        for word in f:
            word = word.lower().strip()
            if set(word).issubset(alphabet):
                yield word

def new_game(vocab, alphabet=ascii_lowercase):
    """Given a vocabulary to draw a random word, returns a new game session"""
    answer = choice([w for w in vocab if len(w) <= Hangman.MAX_GUESSES])
    return Hangman(answer, alphabet=ascii_lowercase)

# App

app = Flask(__name__)
vocab = list(parse_vocab('./2of12.txt'))
game = new_game(vocab)

@app.before_request
def get_game():
    g.game = game

@app.route('/')
def index():
    return json.dumps(g.game.get_state())

@app.route('/reset', methods=['POST'])
def reset():
    g.game = new_game(vocab)
    return json.dumps(g.game.get_state())

@app.route('/guess/<string:letter>', methods=['POST'])
def guess(letter):
    return json.dumps(g.game.guess(letter))

@app.errorhandler(InvalidGuess)
def handle_invalid_guess(error):
    response = json.jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

if __name__ == '__main__':
    app.run()
