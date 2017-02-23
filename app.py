#!/usr/bin/env python3
import os
from binascii import hexlify
from string import ascii_lowercase
from flask import Flask, json, g, render_template, abort, session
from Hangman import HangmanClient, InvalidGuess

# Utils
def gen_user_key():
    return hexlify(os.urandom(24))

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
app.secret_key = '8a1f9630c72259b25bf311bacdcabd3b1bdfa0f057f324cd'
#app.secret_key = os.environ['SECRET_KEY']
vocab = list(parse_vocab('./2of12.txt'))
game = HangmanClient(vocab)
clients = {}

def register_user():
    if 'user' not in session:
        session['user'] = gen_user_key()
    return session['user']

def _get_game(user):
    try:
        print(user)
        return g.clients[user]
    except KeyError:
        abort(404)

@app.before_request
def set_clients():
    g.clients = clients

@app.route('/')
def index():
    register_user()
    return render_template('index.html')

@app.route('/game', methods=['GET'])
def get_game():
    user = register_user()
    game = _get_game(user)
    return json.dumps(game.get_state())

@app.route('/game/new', methods=['POST'])
def new_game():
    user = register_user()
    if user in g.clients:
        game = g.clients.get(user)
        game.new_game()
    else:
        g.clients[user] = HangmanClient(vocab)
        game = g.clients.get(user)
    return json.dumps(game.get_state())

@app.route('/guess/<string:letter>', methods=['POST'])
def guess(letter):
    user = register_user()
    game = _get_game(user)
    return json.dumps(game.guess(letter))

@app.errorhandler(InvalidGuess)
def handle_invalid_guess(error):
    response = json.jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

if __name__ == '__main__':
    app.run()
