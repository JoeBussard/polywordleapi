#!/bin/python
# copyright 2022 joe bussard

import re
import random
import json
import backend_setup
import requests
from werkzeug.exceptions import TooManyRequests

CHEATING = False

class text_colors:
    """Defines how to use colors for terminals
    TODO: Does this work on other machines?
    TODO: Does this work on Windows terminals?"""
    BOLD = '\033[1m'
    YELLOW = BOLD + '' + '\033[93m'
    GREEN = BOLD + '' + '\033[96m'
    RED = BOLD + '' + '\033[91m'
    END = '\033[0m'

# Easier lookup (text_hash[x]) than text_colors.x
text_hash = {'present':text_colors.YELLOW,'correct':text_colors.GREEN,'absent':text_colors.RED,'plain':'', 'end':text_colors.END}

class GameState:
  # One game state per user

  def __init__(self, uuid=None, user_id="Anon", fromCache=False, randomWord=True):
    backend_setup.print_err(f"initializing a new game state for {user_id}")
    if not fromCache:
      self.data = {}
      self.data['user_id'] = user_id
      new_uuid = requests.get("https://www.uuidtools.com/api/generate/v4")
      if new_uuid.status_code == 429:
        raise TooManyRequests()
      uuid_str = str(json.loads(new_uuid.content.decode('utf-8'))[0])
      self.data['uuid'] = uuid_str
      self.data['keyboard_map'] = create_keyboard_map()
      self.data['efficient_key_map'] = {
          'plain':[],
          'absent':[],
          'present':[],
          'correct':[]
          }
      self.data['progress_grid_history'] = []
      self.data['front_end'] = 'JSON'
      self.data['turn'] = 0
      self.data['solution'] = 'based' ### TODO - hardcoded for testing
      self.data['guess_history'] = []
      self.data['current_guess'] = ''
      self.data['guess_map'] = []
    else:
      if uuid:
        self.create_new_from_cache(uuid)
      else:
        print("No game with uuid {uuid} exists.")


  def uuid(self):
    if self.data['uuid']:
      return self.data['uuid']
    else:
      return None

  def set_solution(self, new_solution):
    backend_setup.print_err(f'Changing the solution for {self.data["uuid"]} from {self.data["solution"]} to {new_solution}')
    self.data['solution'] = new_solution

  def get_public_data(self):
    # For returning parts of data that should be given to the client, ie, not the solution.
    public_data = {}
    backend_setup.print_err(f'Creating new dictionary object for public data for {self.data["uuid"]}.')
    for field in ['uuid', 'user_id', 'turn', 'guess_history', 'guess_map', 'efficient_key_map']:
      public_data[field] = self.data[field]
    return public_data

# replace this with UUID
  def create_new_from_cache(self, uuid):
    data_ptr =  backend_setup.GameStateCache.load_game_data_from_cache(uuid)
    for key in data_ptr.keys():
      self.data[key] = data_ptr[key]

  def create_new_from_cache_data(self, uuid, user_id, keyboard_map, progress_grid_history, front_end, turn, solution, guess_history, current_guess):
    backend_setup.print_err(f"Creating new game state object for {uuid} from cache")
    self.data = {}
    self.data['uuid'] = uuid
    self.data['user_id'] = user_id
    self.data['keyboard_map'] = keyboard_map
    self.data['progress_grid_history'] = progress_grid_history
    self.data['front_end'] = front_end
    self.data['turn'] = turn
    self.data['solution'] = solution ### TODO - hardcoded for testing
    self.data['guess_history'] = guess_history
    self.data['current_guess'] = current_guess
    #self.data['guess_map'] = []

def create_keyboard_map():
    """Creates the keyboard map. Initializes everything to "grey" because
    the user does not know if the letter is in use or not."""
    keys_only = ['q','w','e','r','t','y','u','i','o','p','a','s','d','f','g',
            'h','j','k','l','z','x','c','v','b','n','m']
    key_map = {}
    for i in keys_only:
        i = i.lower()
        key_map[i] = 'plain'
    return key_map

def update_efficient_key_map(self):
    ekm = self.data['efficient_key_map']
    for letter in self.data['keyboard_map'].keys():
        ekm[self.data['keyboard_map'][letter]].append(letter)


# def create_emoji_hash():
#     """returns a dict object hashmap that maps color words to emojis"""
#     emoji_hash = {}
#     emoji_hash['white']  = '⬜'
#     emoji_hash['yellow'] = '🟨'
#     emoji_hash['green']  = '🟩'
#     emoji_hash['black']  = '⬛'
#     emoji_hash['red']    = '🟥'
#     return emoji_hash

# def get_todays_word(common_words):
#     """picks a random word and obfuscates it."""
#     rand_max = len(common_words)
#     todays_word_index = ""
#     while todays_word_index not in common_words:
#         todays_word_index = str(random.choice(range(rand_max)))
# 
#     fake_id_letters = 'abcdefABCDEF1234567890'
#     todays_word_game_id = random.choice(fake_id_letters) + str(random.choice(range(10))) + str(todays_word_index) + random.choice(fake_id_letters)
#     todays_word = common_words[todays_word_index]
#     return todays_word_game_id, todays_word
# 
# def get_predetermined_word(common_words, word_game_id):
#     """could be called from a client. decoding is done server-side."""
#     real_word_index = str(decode_word_game_id(word_game_id))
#     predetermined_word = common_words[real_word_index]
#     return predetermined_word
# 
# def decode_word_game_id(word_game_id):
#     word_id_without_obfuscation = word_game_id[2:-1]
#     return word_id_without_obfuscation

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
