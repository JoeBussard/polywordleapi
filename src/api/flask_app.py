from flask import Flask, jsonify, request, redirect, url_for
from werkzeug.exceptions import TooManyRequests

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

#from flask_cors import CORS

import re
import json

import backend_setup
import backend_create_new_game
import backend_run_game
import custom_word
from backend_setup import print_err

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
#CORS(app)

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
def list_endpoints():
    return {"/v1/game, POST" : "Start a new game. Include /solution/ in request to set solution.",
            "/v1/game/<game_uuid>, POST" : "Post a new guess - include /guess/ in request.",
            "/v1/game/<game_uuid>, GET" : "Get the status of a given game."
            }, 200

# Creating a new game
@app.route('/v1/game', methods=['POST'])
@limiter.limit("30 per minute") 
def api_new_game():
  newGameState = backend_create_new_game.GameState()
  newGameState.set_random_solution(common_words)
  result = myCache.save_game_state_to_cache(newGameState)
  if "error" in result:
    return result, 404
  game_uuid = newGameState.uuid()

  custom_solution = None
  if request.get_json() != None and 'solution' in request.get_json():
    custom_solution = str(request.get_json()['solution'])[:6]
  elif request.form.get('solution') != None:
    custom_solution = str(request.form.get('solution'))[:6]
  if custom_solution is not None:
    print_err("Recieved new custom solution:", custom_solution)
    solution_result = custom_word.set_custom_solution(myCache.game_states[game_uuid], custom_solution, all_words)
    if "error" in solution_result:
      return solution_result, 200
  
  return {"game_uuid":newGameState.uuid()}, 200

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


# Guessing new word or making new solution
@app.route('/v1/game/<game_uuid>', methods=['POST'])
def api_game_new_guess(game_uuid):
  game_uuid = str(game_uuid)[:40]
  if game_uuid not in myCache.game_states:
    return {"error": "no game found for that UUID"}, 404 

  if myCache.game_states[game_uuid].data['progress'] in ['victory', 'loss']:
    return {"error":"game already over"}, 200

  current_guess = None
  if request.get_json() != None and 'guess' in request.get_json():
    current_guess = str(request.get_json()['guess'])[:8]
  elif request.form.get('guess') != None:
    current_guess = str(request.form.get('guess'))[:8]
 
  if not current_guess:
    return {"error":"POST methods require a guess."}, 400
  else:
    print_err("Recieved new guess:",current_guess)
    if current_guess in myCache.game_states[game_uuid].data['guess_history']:
      return {"error": "duplicate guess"}, 200  
    guess_result = backend_run_game.process_new_guess(current_guess, myCache.game_states[game_uuid], all_words) 
    if "error" in guess_result:
      return guess_result, 200
    return {"success":"guess posted"}, 200

