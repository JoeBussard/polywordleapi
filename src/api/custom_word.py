import re
import backend_setup

FIVE_LETTERS = re.compile("[A-Za-z]{5}")

def validate_custom_solution(new_solution, all_words):
  """Check a requested custom solution. Returns an {"error": ...} dict, or None when it is acceptable.
  Called BEFORE a game state is created, so a bad request never occupies memory (issue #71)."""
  if type(new_solution) != str:
    return {"error": "new solution must be string"}
  if len(new_solution) != 5:
    return {"error": "Word must be 5 letters"}
  if not FIVE_LETTERS.fullmatch(new_solution):
    return {"error": "Word must be only a-z letters."}
  # Made-up words are allowed as custom solutions (issue #54, ruleset 1): the game records
  # whether the solution is a real word; when it is not, guesses need not be real words either.
  return None

def set_custom_solution(game_state, new_solution, all_words):
  """Apply an already-validated custom solution to a fresh game state."""
  game_state.data['solution'] = new_solution.lower()
  game_state.data['is_custom_solution'] = True
  game_state.data['solution_is_real_word'] = new_solution.lower() in all_words
  return {"success": f"game solution set to {new_solution.lower()}"}
