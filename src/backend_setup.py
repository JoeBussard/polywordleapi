#!/bin/python
# copyright 2022 joe bussard
# This is for setting up the server's backend. This is run once, and it is run when the game is brought online.

import re
import random
import json
from sys import stderr

def print_err(*args, **kwargs):
    print(*args, file=stderr, **kwargs)

def load_dicts_from_json():
    """ loads 2 lists of words: all words, used to check
    that the user made a legitimate guess; and common words,
    used to generate the word for the user to find.
    using a dictionary/JSON means i can remove unwanted words
    from common_words without changing index for other words
    as was brought up in issue #3."""
    common_words = {}
    all_words = {}
    with open('common_words.json') as f:
        common_words = json.load(f)
    with open('all_words.json') as f:
        all_words = json.load(f)
    return common_words, all_words

class GameStateCache:
    # Class wide variables............

    # to be used to make sure i don't save malicious or wrong data
    acceptable_state_fields = [
        'user_id',
        'user_auth',
        'keyboard_map',
        'progress_grid_history',
        'front_end',
        'turn',
        'secret_word',
        'solution',
        'guess_history',
        'current_guess'
        ]

    def __init__(self, cache_id):
      ## I will use some sort of hashing function to use different caches
      ## If i ever scale to that point
        self.cache_id = cache_id
        self.game_states = {}
        self.game_states_data = {}
        print_err(f'Created a new game state cache.')


    def save_game_state_to_cache(self, game_state_object):
      if game_state_object.data['user_id'] in self.game_states.keys():
        print_err(f'Updating game state for game {game_state_object.data["user_id"]} in cache {self.cache_id}')
      else:
        print_err(f'Saving new game state for game {game_state_object.data["user_id"]} in cache{self.cache_id}')
      self.game_states[game_state_object.data['user_id']] = game_state_object

    def save_game_data_to_cache(self, user_id, game_data):
      # user_id because only one game at a time per user
      # game_data should be a json file.
      if user_id in self.game_states_data.keys():
        print_err(f'Updating game state for game {user_id} in cache {self.cache_id}')
      else:
        print_err(f'Saving new game state for game {user_id} in cache{self.cache_id}')
        self.game_states_data[user_id] = {}
      if type(game_data) != dict:
        print_err(f'Data for {user_id} was not a dict')
        return False

      for key in game_data.keys():
        # if type(key) != 'str':
        #   print_err(f'Tried saving something weird to {self.cache_id}')
        #   return False
        str_key = str(key).lower()
        if str_key in self.acceptable_state_fields:
          self.game_states_data[user_id][str_key] = game_data[str_key]
          print_err(f'Saved {str_key} for {user_id} in cache.')
        else:
          print_err(f'Err: {str_key} is not an acceptable field to be cached.')

    def load_game_data_from_cache(self, user_id):
      ### Just loads a game from the cache
      if user_id in self.game_states_data.keys():
        print_err(f'Loading game data for {user_id} from cache.')
        return self.game_states_data[user_id]
      else:
        print_err(f'No game data found for {user_id} in cache {self.cache_id}')
        return False

    def delete_game_data_from_cache(self, user_id):
      ## Make sure you auth'ed before calling this
      if user_id in self.game_states_data.keys():
        print_err(f'Deleting game data for {user_id} from cache.')
        del self.game_states_data[key]
        return True
      else:
        print_err(f'Cannot delete game data for {user_id} from cache: User not found')
        return False

    def save_cache_to_disk(self, file_name):
      print_err("Reserved for saving this cache to disk")

    def load_cache_from_disk(self, file_name):
      print_err("Reserverd for loading game data from disk to a cache.")

    def dump_cache_to_stderr(self):
      print_err(f'Printing data stored in cache {self.cache_id}...')
      print_err(json.dumps(self.game_data, indent=2, sort_keys=True))


def start_up_game_backend(cache_id):
    """ Boot strapping the game server"""
    print_err("Booting up Polywordle v.0.0.1")

    my_cache = GameStateCache(cache_id)

    common_words, all_words = load_dicts_from_json()

    return my_cache, common_words, all_words


#     def test2():
#       """main game logic. initializes several variables, then jumps into the main loop:
#       1. compare a guess
#       2. print the new board
#       3. repeat."""
#       guess_history = []
#       index_map_history = []
#       common_words, all_words = load_dicts_from_json()
#       game_day = 0
#       shared_id, shared_word = ask_user_new_word_or_word_from_id(common_words)
#       if shared_word and shared_id:
#           todays_word_game_id = shared_id
#           todays_word = shared_word
#       else:
#           todays_word_game_id, todays_word = get_todays_word(common_words)
#       if CHEATING: print("[cheating] todays word is", todays_word)
#       key_map = create_keyboard_map()
#       emoji_hash = create_emoji_hash()
#       guesses = 0
#   
#       print("Welcome to Polywordle [version 0.2]")
#   
#       # Print the "blank" board with just empty squares.
#       for x in range(guesses, 6):
#           pretty_print_blank_lines(emoji_hash, 'white')
#       pretty_print_keyboard(key_map)
#   
#       print("this is key_map")
#       json_status_dict = {}
#       json_status_dict['keyboard'] = key_map
#       json_status_dict['game_id'] = 0
#       json_status_dict['turn'] = guesses
#       print(key_map)
#       print("this is the json response")
#       print(json_status_dict)
#       print(json.dumps(json_status_dict, indent=4))
#   
#       while guesses < 6:
#           invalid_guess = True
#           while invalid_guess:
#               current_guess = input(("Guess #"+ str(guesses+1)+ ": "))
#               if len(current_guess) == 5:
#                   pattern = re.compile("[A-Za-z]+")
#                   if pattern.fullmatch(current_guess):
#                       if current_guess.lower() in list(all_words.values()): break
#                       else: print("Not in dictionary.")
#                   else: print("Must only be letters.")
#               else: print("Must be 5 letters.")
#   
#           current_guess = current_guess.lower()
#   
#           guesses += 1
#           # note sure if this is right
#           index_color_map, key_map = update_all(current_guess, todays_word, key_map, index_map_history)
#           guess_history.append(current_guess)
#   
#           print("now printing the json response")
#           json_status_dict['keyboard'] = key_map
#           json_status_dict['index_color_map_history'] = index_map_history
#           json_status_dict['turn'] = guesses
#           print(json.dumps(json_status_dict, indent=4))
#   
#   
#           # clear screen
#           for x in range(50):print("")
#           for x in range(guesses):
#               pretty_print_index_color(index_map_history[x], guess_history[x], emoji_hash)
#   
#           for x in range(guesses, 6):
#               pretty_print_blank_lines(emoji_hash, 'white')
#   
#           pretty_print_keyboard(key_map)
#           if current_guess == todays_word:
#               break
#       if current_guess == todays_word:
#           print(text_hash['green'], end='')
#           print(performance_hash[guesses])
#           print(text_hash['end'], end='')
#       else:
#           print(text_hash['red'], "Bummer! The word was ", todays_word.upper(), text_hash['end'], sep='')
#       print(f"\nIf you feel this word is unfair, please open an issue at ", text_hash['yellow'], "https://GitHub.com/JoeBussard/PolyWordle", text_hash['end'], sep='')
#   
#       print(f"\nShare your score:\n")
#       print(generate_share_text(guesses, index_map_history, emoji_hash, todays_word_game_id))
#   
#       exit(0)
#   
#   #test2()
