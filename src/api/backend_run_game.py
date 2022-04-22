#!/bin/python
# copyright 2022 joe bussard
################################################3
#    backend_run_game.py
#
# Includes  - process_new_guess function
#           - validate_guess_input function


import re
import random
import json
import backend_setup
import backend_create_new_game


def process_new_guess(guess, game_state, all_words):
  # Does everything needed to process a new guess.
    if len(game_state.data['progress_grid_history']) > 5:
        return "game over"
    check_for_bad_input = validate_guess_input(guess, all_words)
    if "error" in check_for_bad_input:
        return check_for_bad_input
    solution = game_state.data['solution']
    new_progress_row, is_a_winner = compare_guess_to_solution(guess, solution)
    update_keyboard(game_state.data['keyboard_map'], new_progress_row, guess)
    update_efficient_key_map(game_state)
    game_state.data['guess_history'].append(guess)
    game_state.data['progress_grid_history'].append(new_progress_row)
    update_guess_map(game_state)
    game_state.data['turn'] += 1
    if is_a_winner == 2:
        game_state.data['public_solution'] = game_state.data['solution']
        game_state.data['progress'] = "victory"
    elif is_a_winner == 1:
        if len(game_state.data['guess_history']) >= 6:
            game_state.data['public_solution'] = game_state.data['solution']
            game_state.data['progress'] = "loss"
    return {"success":"game state updated"}

def validate_guess_input(guess, all_words):
    if len(guess) != 5:
        return {"error": "Word must be 5 letters"}
    pattern = re.compile("[A-Za-z]+")
    if not pattern.fullmatch(guess):
        return {"error": "Word must be only letters"}
    if guess.lower() not in list(all_words.values()):
        return {"error": "Word not in dictionary"}
    return {"success":""}

def compare_guess_to_solution(guess, solution):
    """trying to get this to o(n) time, but still o(n^2) to check yellows."""
    if guess == solution:
        winner = 2
    else:
        winner = 1
    guess_hash, solution_hash, result_hash = {}, {}, {}
    for i in range(5):
        guess_hash[i] = guess[i]
        solution_hash[i] = solution[i]
        result_hash[i] = "absent"
        if guess_hash[i] == solution_hash[i]:
            result_hash[i] = "correct"
            guess_hash[i], solution_hash[i] = "", ""

    for guess_key in range(5):
        for solution_key in range(5):
            if guess_hash[guess_key] == solution_hash[solution_key] and result_hash[guess_key] == "absent":
                result_hash[guess_key] = "present"
                guess_hash[guess_key], solution_hash[solution_key] = "", ""
    return result_hash, winner

def update_keyboard(key_map, progress_row, guess):
    """Input is a keyboard-status dictionary {'q': present, 'w':'absent', ... }
    .... It updates that keyboard map and returns it."""
    for x in progress_row:
        if key_map[guess[x]] != 'correct': # letters dont go from green to yellow
            key_map[guess[x]] = progress_row[x]
    return None


def update_efficient_key_map(game_state):
    """this is the map that says {'plain':'qwerty..'}"""
    ekm = game_state.data['efficient_key_map']
    for color in ['plain', 'absent', 'present', 'correct']:
        ekm[color] = []
    for letter in game_state.data['keyboard_map'].keys():
        ekm[game_state.data['keyboard_map'][letter]].append(letter)

def update_guess_map(game_state):
    """using pointers to the game state, updates the map that shows the progress
    of the whole game. The guess map is basically:
    Turn 0 = {Letter:Color, Letter:color, Letter:color, Letter:color, Letter:color}
    Turn 1 = {Letter:Color, Letter:color, Letter:color, Letter:color, Letter:color}
    etc."""
    progress = game_state.data['progress_grid_history']
    guesses = game_state.data['guess_history']
    guess_map = game_state.data['guess_map']
    turn = game_state.data['turn']
    guess_map.append([])
    letter_color = [[guesses[turn][i], progress[turn][i]] for i in range(5)]
    guess_map[turn] = letter_color
    return 0


def prepare_json_response(game_state):
    game_state_data = game_state.data
    response = game_state.get_public_data() 
    for field in ['uuid', 'user_id', 'progress', 'turn', 'guess_history', 'guess_map', 'efficient_key_map']:
        if field not in response:
            return {"error":"something wrong"}
    return response
