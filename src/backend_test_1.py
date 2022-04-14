import backend_setup
import backend_create_new_game

# Simulating starting up the game server

#myCache = backend_setup.GameStateCache(0)
myCache, common_words, all_words = backend_setup.start_up_game_backend('A')

for user in range(10):
  # users made connections and started new games
  print("Making a new game state for user", user)
  newGameState = backend_create_new_game.GameState(user)
  print("Calling function to save it to the cache")
  myCache.save_game_state_to_cache(newGameState)
  # maybe i should pass the 
  # game state object into the cache 
  # instead of its data 

for cache in myCache.game_states:
  print("yeah i should save the object instead,", cache)



