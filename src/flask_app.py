from flask import Flask, jsonify, request, redirect, url_for

import re
import json

import backend_setup
import backend_create_new_game
import backend_run_game
from backend_setup import print_err

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

## Initialize server

myCache, common_words, all_words = backend_setup.start_up_game_backend('A')

@app.route('/')
def hello_word():
  return "Polywordle API is alive", 200

@app.route('/newgame/<user_id>', methods=['GET'])
def api_new_game(user_id):
  clipped_id = str(user_id)[:10]
  newGameState = backend_create_new_game.GameState(clipped_id)
  myCache.save_game_state_to_cache(newGameState)
  return api_show_game( user_id)

@app.route('/game', methods=['GET'])
def api_new_game_no_id():
  new_id = 'random_id'
  return api_new_game(new_id)

@app.route('/game/<user_id>', methods=['GET'])
def api_show_game(user_id):
  clipped_id = str(user_id)[:10]
 # return myCache.game_states[clipped_id].get_public_data()
  return backend_run_game.prepare_json_response(myCache.game_states[clipped_id])
  
@app.route('/game/<user_id>/<guess>', methods=["GET"])
def api_process_guess(user_id, guess):
  global all_words
  clipped_id = str(user_id)[:10]
  clipped_guess = str(guess)[:10]
#  backend_run_game.process_new_guess(clipped_guess, myCache.game_states[clipped_id], all_words)
#  return myCache.game_states[clipped_id].get_public_data()
  backend_run_game.process_new_guess(clipped_guess, myCache.game_states[clipped_id], all_words)
  return backend_run_game.prepare_json_response(myCache.game_states[clipped_id])

    

