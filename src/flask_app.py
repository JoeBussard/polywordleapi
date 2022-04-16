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
print_err("Booting up...")

myCache, common_words, all_words = backend_setup.start_up_game_backend('A')

@app.route('/')
def hello_word():
  return "Polywordle API is alive", 200

@app.route('/v1/game', methods=['GET'])
def api_new_game():
  newGameState = backend_create_new_game.GameState()
  myCache.save_game_state_to_cache(newGameState)
  return {"game_uuid": newGameState.uuid()}, 200

@app.route('/v1/game', methods=['POST', 'PUT', 'DELETE'])
def api_new_game_bad_method():
  return "", 400


@app.route('/v1/game/<game_uuid>', methods=['GET'])
def api_show_game(game_uuid):
  good_game_uuid = str(game_uuid)
  if good_game_uuid not in myCache.game_states:
    return {"error":"game not found"}, 404
  return backend_run_game.prepare_json_response(myCache.game_states[good_game_uuid])
  
### GUESS NEW WORD ###

@app.route('/v1/game/<game_uuid>', methods=['POST'])
def api_game_new_guess(game_uuid):
  good_game_uuid = str(game_uuid)
#   try: 
#     guess_data = request.get_json()
#     if guess_data is not None:
#       if 'guess' in guess_data:
#         current_guess = str(guess_data['guess'])[:8]
#         backend_run_game.validate_guess_input(current_guess, all_words)
#         backend_run_game.compare_guess_to_solution(current_guess, myCache.game_states[good_game_uuid].data['solution'])
#         return backend_run_game.prepare_json_response(myCache.game_states[good_game_uuid])
#   except request.on_json_loading_failed():

  if request.form.get('guess') != None:
    current_guess = str(request.form.get('guess'))[:8]
    print_err("Recieved guess:",current_guess)
    valid_input = backend_run_game.validate_guess_input(current_guess, all_words)
    guess_result = backend_run_game.process_new_guess(current_guess, myCache.game_states[game_uuid], all_words)
    if "error" in guess_result:
      print_err(valid_input['error'])
      return valid_input, 200 
    return backend_run_game.prepare_json_response(myCache.game_states[good_game_uuid])

  else: # lets see if it's part of a curl
    return "", 500
  #if request
  #else:
  #  return {"error":"no guess in post request"}


  if good_game_uuid not in myCache.game_states:
    return {"error": "game not found"}, 404






@app.route('/game/<user_id>/<guess>', methods=["GET"])
def api_process_guess(user_id, guess):
  global all_words
  clipped_id = str(user_id)[:10]
  clipped_guess = str(guess)[:10]
#  backend_run_game.process_new_guess(clipped_guess, myCache.game_states[clipped_id], all_words)
#  return myCache.game_states[clipped_id].get_public_data()
  backend_run_game.process_new_guess(clipped_guess, myCache.game_states[clipped_id], all_words)
  return backend_run_game.prepare_json_response(myCache.game_states[clipped_id])

    

