#!/usr/bin/env python3
import unittest
from random import choice
from Hangman import HangmanClient, InvalidGuess
from string import ascii_lowercase

vocab = "quick brown fox jumped over the lazy dog".split()
alph = ascii_lowercase

class HangmanTestCase(unittest.TestCase):
    def setUp(self):
        self.game = HangmanClient()
        # ensure at least 1 non-game-ending guess 
        self.answer = choice([w for w in vocab
          if 1 < len(set(w)) < HangmanClient.MAX_GUESSES])
        self.game.new_game(self.answer, alph)
        self.bad_letters = set(alph) - set(self.answer)
        self.bad_guess = choice(list(self.bad_letters))
        self.good_guess = choice(self.answer)
        self.invalid_guess = '@'
        self.initial_state = {
          'max_guesses': HangmanClient.MAX_GUESSES,
          'status': HangmanClient.Status.ongoing.name,
          'guesses_left': HangmanClient.MAX_GUESSES,
          'letters_guessed': [],
          'word_with_blanks':  HangmanClient.BLANK_CHAR * len(self.answer),
          'won': 0,
          'lost': 0
        }
        # post good guess state
        [pggs_blanks, pbgs_blanks] = \
          [''.join(HangmanClient.BLANK_CHAR if \
                  c != other else \
                  self.good_guess \
                  for c in self.answer) \
           for other in [self.good_guess, self.bad_guess]]
        self.pggs = self.initial_state.copy()
        self.pggs.update({
            'letters_guessed': [self.good_guess],
            'word_with_blanks': pggs_blanks
        })
        # post bad guess state
        self.pbgs = self.initial_state.copy()
        self.pbgs.update({
            'letters_guessed': [self.bad_guess],
            'word_with_blanks': pbgs_blanks,
            'guesses_left': HangmanClient.MAX_GUESSES - 1
        })

    def tearDown(self):
        del self.game


    def test_get_status(self):
        game = self.game
        for l in range(len(self.answer)+1):
            for g in range(HangmanClient.MAX_GUESSES+1):
                with self.subTest(left=l, guesses=g): 
                    status = game._compute_status(l,g)
                    if l <= 0:
                        expected = HangmanClient.Status.won
                    elif g >= HangmanClient.MAX_GUESSES:
                        expected = HangmanClient.Status.lost
                    else:
                        expected = HangmanClient.Status.ongoing
                    self.assertEqual(status, expected)

    def test_init(self):
        game = self.game
        self.assertEqual(game.won, 0)
        self.assertEqual(game.lost, 0)
        self.assertEqual(len(game.answers), 0)

    def test_new_game(self):
        game = self.game
        game.new_game(self.answer, alph)
        self.assertEqual(game.incorrect_guesses, 0)
        self.assertEqual(game.status, HangmanClient.Status.ongoing)
        self.assertEqual(len(game.letters_left), len(self.answer))
        self.assertEqual(len(game.letters_guessed), 0)

    def test_get_state_initial(self):
        game = self.game
        state = game.get_state()
        self.assertEqual(state, self.initial_state)

    def test_good_guess(self):
        game = self.game
        state = game.guess(self.good_guess)
        self.assertEqual(game.incorrect_guesses, 0)
        self.assertEqual(game.status, HangmanClient.Status.ongoing)
        self.assertIn(self.good_guess, game.letters_guessed)
        self.assertEqual(len(game.letters_left), len(self.answer)-1)
        self.assertEqual(state, self.pggs)

    def test_bad_guess(self):
        game = self.game
        state = game.guess(self.bad_guess)
        self.assertEqual(game.incorrect_guesses, 1)
        self.assertEqual(game.status, HangmanClient.Status.ongoing)
        self.assertIn(self.bad_guess, game.letters_guessed)
        self.assertEqual(len(game.letters_left), len(self.answer))
        self.assertEqual(state, self.pbgs)

    def test_invalid_guess(self):
        game = self.game
        with self.assertRaises(InvalidGuess):
            game.guess(self.invalid_guess)
        state = game.get_state()
        self.assertEqual(state, self.initial_state)

    def test_same_good_guess(self):
        game = self.game
        game.guess(self.good_guess)
        with self.assertRaises(InvalidGuess):
            game.guess(self.good_guess)
        state = game.get_state()
        self.assertEqual(state, self.pggs)

    def test_same_bad_guess(self):
        game = self.game
        game.guess(self.bad_guess)
        with self.assertRaises(InvalidGuess):
            game.guess(self.bad_guess)
        self.assertEqual(game.get_state(), self.pbgs)

    def test_guess_after_lost(self):
        game = self.game
        with self.assertRaises(InvalidGuess):
            for c in self.bad_letters:
                game.guess(c)

    def test_guess_after_won(self):
        game = self.game
        for c in self.answer:
            game.guess(c)
        with self.assertRaises(InvalidGuess):
            game.guess(self.bad_guess)


    def test_won_state(self):
        game = self.game
        for c in self.answer:
            state = game.guess(c)
        lg = state['letters_guessed']
        lg.sort()
        state['letters_guessed'] = lg
        expected = self.initial_state.copy()
        lg = list(set(self.answer))
        lg.sort()
        expected['letters_guessed'] = lg
        expected.update({
            'status': HangmanClient.Status.won.name,
            'word_with_blanks': self.answer,
            'won': 1,
            'letters_left': [],
            'answer': self.answer
        })
        self.assertEqual(state, expected)

    def test_lost_state(self):
        game = self.game
        expected = self.initial_state.copy()
        expected['letters_guessed'] = set()
        for c in list(self.bad_letters)[:HangmanClient.MAX_GUESSES]:
            state = game.guess(c)
            expected['letters_guessed'].add(c)
        expected.update({
            'status': HangmanClient.Status.lost.name,
            'guesses_left': 0,
            'won': 0,
            'lost': 1,
            'answer': self.answer,
            'letters_left': list(set(self.answer))
        })
        for entry in ['letters_guessed','letters_left']:
            val = state[entry]
            val.sort()
            state[entry] = val
            e_val = list(expected[entry])
            e_val.sort()
            expected.update({
                entry: e_val
            })
        self.assertEqual(state, expected)
        
if __name__ == '__main__':
    unittest.main()
