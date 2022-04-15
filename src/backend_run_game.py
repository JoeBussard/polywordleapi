#!/bin/python
# copyright 2022 joe bussard

import re
import random
import json
import backend_setup
import backend_create_new_game

def process_new_guess(guess, game_state, all_words):
  # Does everything needed to process a new guess.
    if len(game_state.data['progress_grid_history']) > 5:
        print("Something wrong")
        return None
    print("processing new guess")
    check_for_bad_input = validate_guess_input(guess, all_words)
    if check_for_bad_input is not None:
        return check_for_bad_input
    solution = game_state.data['solution']
    new_progress_row = compare_guess_to_solution(guess, solution)
    update_keyboard(game_state.data['keyboard_map'], new_progress_row, guess)
    game_state.data['guess_history'].append(guess)
    game_state.data['progress_grid_history'].append(new_progress_row)
    return None

def validate_guess_input(guess, all_words):
    if len(guess) != 5:
        return {"error": "Word must be 5 letters"}
    pattern = re.compile("[A-Za-z]+")
    if not pattern.fullmatch(guess):
        return {"error": "Word must be only letters"}
    if guess.lower() not in list(all_words.values()):
        return {"error": "Word not in dictionary"}
    return None

def compare_guess_to_solution(guess, solution):
    """trying to get this to o(n) time, but still o(n^2) to check yellows."""
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
    return result_hash

def update_keyboard(key_map, progress_row, guess):
    """Input is a keyboard-status dictionary {'q': present, 'w':'absent', ... }
    .... It updates that keyboard map and returns it."""
    for x in progress_row:
        if key_map[guess[x]] != 'present': # letters dont go from green to yellow
            key_map[guess[x]] = progress_row[x]
    return None

def prepare_json_response(game_state):
    game_state_data = game_state.data
    keyboard_map = game_state_data['keyboard_map']
    prepped = game_state_data
    efficient_key_map = {
        'plain':[],
        'absent':[],
        'present':[],
        'correct':[]
        }
    for letter in keyboard_map.keys():
        efficient_key_map[keyboard_map[letter]].append(letter)
    turn = len(game_state_data['progress_grid_history'])
    progress_ptr = game_state_data['progress_grid_history']
    guess_ptr = game_state_data['guess_history']
    guess_map = []
    for turn_no in range(turn):
        guess_map.append([])
        key_value = [[guess_ptr[turn_no][i], progress_ptr[turn_no][i]] for i in range(len(guess_ptr[turn_no]))]
        guess_map[turn_no] = key_value

    prepped['keyboard'] = efficient_key_map
    prepped['guesses'] = guess_map
    return prepped
  


# def test2():
#     """main game logic. initializes several variables, then jumps into the main loop:
#     1. compare a guess
#     2. print the new board
#     3. repeat."""
#     guess_history = []
#     index_map_history = []
#     common_words, all_words = load_dicts_from_json()
#     game_day = 0
#     shared_id, shared_word = ask_user_new_word_or_word_from_id(common_words)
#     if shared_word and shared_id:
#         todays_word_game_id = shared_id
#         todays_word = shared_word
#     else:
#         todays_word_game_id, todays_word = get_todays_word(common_words)
#     if CHEATING: print("[cheating] todays word is", todays_word)
#     key_map = create_keyboard_map()
#     emoji_hash = create_emoji_hash()
#     guesses = 0
# 
#     print("Welcome to Polywordle [version 0.2]")
# 
#     # Print the "blank" board with just empty squares.
#     for x in range(guesses, 6):
#         pretty_print_blank_lines(emoji_hash, 'white')
#     pretty_print_keyboard(key_map)
# 
#     print("this is key_map")
#     json_status_dict = {}
#     json_status_dict['keyboard'] = key_map
#     json_status_dict['game_id'] = 0
#     json_status_dict['turn'] = guesses
#     print(key_map)
#     print("this is the json response")
#     print(json_status_dict)
#     print(json.dumps(json_status_dict, indent=4))
# 
#     while guesses < 6:
#         invalid_guess = True
#         while invalid_guess:
#             current_guess = input(("Guess #"+ str(guesses+1)+ ": "))
#             if len(current_guess) == 5:
#                 pattern = re.compile("[A-Za-z]+")
#                 if pattern.fullmatch(current_guess):
#                     if current_guess.lower() in list(all_words.values()): break
#                     else: print("Not in dictionary.")
#                 else: print("Must only be letters.")
#             else: print("Must be 5 letters.")
# 
#         current_guess = current_guess.lower()
# 
#         guesses += 1
#         # note sure if this is right
#         index_color_map, key_map = update_all(current_guess, todays_word, key_map, index_map_history)
#         guess_history.append(current_guess)
# 
#         print("now printing the json response")
#         json_status_dict['keyboard'] = key_map
#         json_status_dict['index_color_map_history'] = index_map_history
#         json_status_dict['turn'] = guesses
#         json_status_dict['guess_history'] = guess_history
#         print(json.dumps(json_status_dict, indent=4))
# 
# 
#         # clear screen
#         for x in range(50):print("")
#         for x in range(guesses):
#             pretty_print_index_color(index_map_history[x], guess_history[x], emoji_hash)
# 
#         for x in range(guesses, 6):
#             pretty_print_blank_lines(emoji_hash, 'white')
# 
#         pretty_print_keyboard(key_map)
#         if current_guess == todays_word:
#             break
#     if current_guess == todays_word:
#         print(text_hash['green'], end='')
#         print(performance_hash[guesses])
#         print(text_hash['end'], end='')
#     else:
#         print(text_hash['red'], "Bummer! The word was ", todays_word.upper(), text_hash['end'], sep='')
#     print(f"\nIf you feel this word is unfair, please open an issue at ", text_hash['yellow'], "https://GitHub.com/JoeBussard/PolyWordle", text_hash['end'], sep='')
# 
#     print(f"\nShare your score:\n")
#     print(generate_share_text(guesses, index_map_history, emoji_hash, todays_word_game_id))
# 
#     exit(0)
# 
# #test2()
