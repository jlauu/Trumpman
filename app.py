#!/usr/bin/env python3
from string import ascii_lowercase
from flask import Flask, json, g, render_template
from Hangman import HangmanClient, InvalidGuess

# Utils
def parse_vocab(filepath, alphabet=ascii_lowercase):
    """Returns a list of words given a file with one word per line"""
    alphabet = set(alphabet)
    with open(filepath, 'r') as f:
        for word in f:
            word = word.lower().strip()
            if set(word).issubset(alphabet):
                yield word
# App

app = Flask(__name__)
vocab = list(parse_vocab('./2of12.txt'))

# Uncertain what thread/concurrency-related properties are 
# with a global object
# Alternatives: 
#   - game state in sessions + serializing/deserializing
#   - database with users, games, game history, etc.
#   - global hash of user-key to game session + storing key in session
global game
game = HangmanClient(vocab)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/game', methods=['GET'])
def get_game():
    global game
    return json.dumps(game.get_state())

@app.route('/game/new', methods=['POST'])
def new_game():
    global game
    game.new_game()
    return json.dumps(game.get_state())

@app.route('/guess/<string:letter>', methods=['POST'])
def guess(letter):
    global game
    return json.dumps(game.guess(letter))

@app.errorhandler(InvalidGuess)
def handle_invalid_guess(error):
    response = json.jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

if __name__ == '__main__':
    app.run()
