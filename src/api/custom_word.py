import re, random, json, requests
import backend_setup, backend_create_new_game

def set_custom_solution(game_state, new_solution, all_words):
  # Error checking
  # Game must exist
  if game_state is None or game_state.data is None:
    return {"error":"Game does not exist"}
  # Game must not be in progress
  if game_state.data['turn'] > 0:
    return {"error":"Game already started"}
  # New solution must be a valid word
  if type(new_solution) != str:
    return {"error":"new solution must be string"}
  if len(new_solution) != 5:
    return {"error":"Word must be 5 letters"}
  pattern = re.compile("[A-Za-z]+")
  if not pattern.fullmatch(new_solution):
    return {"error":"Word must be only a-z letters."}
  # Check if that is already the solution
  if game_state.data['solution'] == new_solution:
    return {"error":"Solution already set to that word."}
  new_solution = str(new_solution)[:5].lower()
  if new_solution not in list(all_words.values()):
    print(new_solution, "was not in dictionary")
    return {"error":"Solution is not in dictionary"}
  game_state.data['solution'] = new_solution
  return {"success":f"game solution set to {new_solution}"}

