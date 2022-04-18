from flask import Flask, jsonify, request, redirect, url_for
from werkzeug.exceptions import TooManyRequests

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


import re
import json

import backend_setup
import backend_create_new_game
import backend_run_game
from backend_setup import print_err

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["90 per minute"]
    )

# Initialize server
myCache, common_words, all_words = backend_setup.start_up_game_backend('A')

# Ping
@app.route('/')
def hello_world():
  return "Polywordle is live at version /v1/", 200

@app.route('/v1')
def hello_world_v1():
  return "Polywordle /v1/ is live. Send a POST to /v1/game to start a new game", 200

# Creating a new game
@app.route('/v1/game', methods=['POST'])
@limiter.limit("30 per minute") 
def api_new_game():
  try:
    newGameState = backend_create_new_game.GameState()
    newGameState.set_random_solution(common_words)
    result = myCache.save_game_state_to_cache(newGameState)
    if "error" in result:
      return result, 404
    return {"game_uuid": newGameState.uuid()}, 200
  except TooManyRequests as e:
    del(newGameState)
    return "", 429


@app.route('/v1/game', methods=['GET'])
def api_new_game_wrong_method():
  return {"error":"Missing game ID in URL"}, 400


# Getting status of game in cache
@app.route('/v1/game/<game_uuid>', methods=['GET'])
def api_show_game(game_uuid):
  good_game_uuid = str(game_uuid)[:40]
  if good_game_uuid not in myCache.game_states:
    return {"error":"game not found"}, 404
  response = backend_run_game.prepare_json_response(myCache.game_states[good_game_uuid])
  if "error" in response:
      return "", 404
  else:
    return response


# Guessing new word
@app.route('/v1/game/<game_uuid>', methods=['POST'])
def api_game_new_guess(game_uuid):
  good_game_uuid = str(game_uuid)[:40]
  game_uuid = good_game_uuid
  if good_game_uuid not in myCache.game_states:
    return {"error": "no game found for that UUID"}, 404 

  if myCache.game_states[good_game_uuid].data['progress'] in ['victory', 'loss']:
    return {"error":"game already over"}, 200

  guess_data = request.get_json()
  if guess_data != None:
    if 'guess' in guess_data:
      current_guess = str(guess_data['guess'])[:8]
      if current_guess in myCache.game_states[game_uuid].data['guess_history']:
          return {"error": "duplicate guess"}, 200
      guess_result = backend_run_game.process_new_guess(current_guess, myCache.game_states[game_uuid], all_words)
      if "error" in guess_result:
        if "not in dictionary" in guess_result["error"]:
          return {"error":"word not in dictionary"}, 200
        if "only letters" in guess_result["error"]:
          return {"error":"word must be only letters"}, 200
      return {"success":"guess posted"}, 200

  elif request.form.get('guess') != None:
    current_guess = str(request.form.get('guess'))[:8]
    print_err("Recieved guess:",current_guess)
    if current_guess in myCache.game_states[game_uuid].data['guess_history']:
      return {"error": "duplicate guess"}, 200
    guess_result = backend_run_game.process_new_guess(current_guess, myCache.game_states[game_uuid], all_words)
    if "error" in guess_result:
      return "something wrong", 500
    return {"success":"guess posted"}, 200
    #backend_run_game.prepare_json_response(myCache.game_states[good_game_uuid])
  
  else:
    return {"error":"POST methods require a guess"}, 400
