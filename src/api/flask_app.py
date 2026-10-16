from flask import Flask, request

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

import re

import backend_setup
import backend_create_new_game
import backend_run_game
import custom_word
from backend_setup import print_err

app = Flask(__name__)
# Behind a reverse proxy (Apache): trust one hop of X-Forwarded-For / -Proto so the
# rate limiter sees the real client address instead of 127.0.0.1.
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)
app.json.sort_keys = False
# Game requests are a few hundred bytes at most; refuse anything larger (413).
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024
CORS(app)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["90 per minute"],
    storage_uri="memory://",
    )

# A game id must look like a UUID (issue #70); anything else is a 404 without touching the cache.
UUID_RE = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')

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
@app.route('/v1/newgame', methods=['POST'])
@limiter.limit("100 per minute")
def api_new_game():
  if request.get_json(silent=True) == None and request.form.get('solution') == None:
    # Assume a random game is requested
    newGameState = backend_create_new_game.GameState()
    newGameState.set_random_solution(common_words)
    result = myCache.save_game_state_to_cache(newGameState)
    if "error" in result:
      return result, 404
    game_uuid = newGameState.uuid()
    return {"game_uuid":game_uuid}, 200

  custom_solution = None
  if request.get_json(silent=True) != None and 'solution' in request.get_json():
    print_err(request.get_json())
    custom_solution = str(request.get_json()['solution'])[:6]
  elif request.form.get('solution') != None:
    custom_solution = str(request.form.get('solution'))[:6]

  if custom_solution is not None:
    print_err("Recieved new custom solution:", custom_solution)
    # Validate first; a game state is only created once the solution is known to be acceptable.
    # A rejected word is a game-rules violation, so it is a 200 with an error field, not a 404.
    problem = custom_word.validate_custom_solution(custom_solution, all_words)
    if problem is not None:
      return problem, 200
    newGameState = backend_create_new_game.GameState()
    custom_word.set_custom_solution(newGameState, custom_solution, all_words)
    result = myCache.save_game_state_to_cache(newGameState)
    if "error" in result:
      return result, 404
    game_uuid = newGameState.uuid()
    return {"game_uuid":game_uuid}, 200
  return "", 500

# Getting status of game in cache
@app.route('/v1/game/<game_uuid>', methods=['GET'])
def api_show_game(game_uuid):
  good_game_uuid = str(game_uuid).lower()
  if not UUID_RE.match(good_game_uuid) or good_game_uuid not in myCache.game_states:
    return {"error":"game not found"}, 404
  response = backend_run_game.prepare_json_response(myCache.game_states[good_game_uuid])
  if "error" in response:
      return "", 404
  else:
    return response


# Guessing new word or making new solution
@app.route('/v1/game/<game_uuid>', methods=['POST'])
def api_game_new_guess(game_uuid):
  game_uuid = str(game_uuid).lower()
  if not UUID_RE.match(game_uuid) or game_uuid not in myCache.game_states:
    return {"error": "no game found for that UUID"}, 404

  if myCache.game_states[game_uuid].data['progress'] in ['victory', 'loss']:
    return {"error":"game already over"}, 200

  current_guess = None
  if request.get_json(silent=True) != None and 'guess' in request.get_json():
    current_guess = str(request.get_json()['guess'])[:8].lower()
  elif request.form.get('guess') != None:
    current_guess = str(request.form.get('guess'))[:8].lower()

  if not current_guess:
    return {"error":"POST methods require a guess."}, 400
  else:
    print_err("Recieved new guess:",current_guess)
    if current_guess in myCache.game_states[game_uuid].data['guess_history']:
      return {"error": "duplicate guess"}, 200
    guess_result = backend_run_game.process_new_guess(current_guess, myCache.game_states[game_uuid], all_words)
    if "error" in guess_result:
      return guess_result, 200
    myCache.save_game_state_to_cache(myCache.game_states[game_uuid])   # write the new turn through to disk
    return {"success":"guess posted"}, 200


if __name__ == '__main__':
    app.run(threaded=False)
