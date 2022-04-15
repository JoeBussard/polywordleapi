import backend_setup
import json
import backend_create_new_game
import backend_run_game

# Simulating starting up the game server

#myCache = backend_setup.GameStateCache(0)
myCache, common_words, all_words = backend_setup.start_up_game_backend('A')

for user in range(10):
  # users made connections and started new games
  print("Making a new game state for user", user)
  newGameState = backend_create_new_game.GameState(user)
  print("Calling function to save it to the cache")
  if user == 0:
    newGameState.set_solution('cringe')
  myCache.save_game_state_to_cache(newGameState)
  if user == 1:
    newGameState.set_solution('after saving to cache')
  # maybe i should pass the 
  # game state object into the cache 
  # instead of its data 

for cache in myCache.game_states:
  print("yeah i should save the object instead,", cache)

print(json.dumps(myCache.game_states[0].get_public_data(), indent=2))
print(json.dumps(myCache.game_states[1].get_public_data(), indent=2))

backend_run_game.process_new_guess('fight', myCache.game_states[0], all_words)
backend_run_game.process_new_guess('fight', myCache.game_states[0], all_words)
backend_run_game.process_new_guess('fight', myCache.game_states[0], all_words)
backend_run_game.process_new_guess('fight', myCache.game_states[0], all_words)
backend_run_game.process_new_guess('fight', myCache.game_states[0], all_words)
backend_run_game.process_new_guess('fight', myCache.game_states[0], all_words)
backend_run_game.process_new_guess('fight', myCache.game_states[0], all_words)
backend_run_game.process_new_guess('fight', myCache.game_states[0], all_words)
print(json.dumps(myCache.game_states[0].get_public_data(), indent=2))


