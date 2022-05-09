#!/bin/python
# copyright 2022 joe bussard
########################################################
#      backend_create_new_game.py                
#                                              
# Includes - GameState class.                      
#          - text_colors class. (unused)        
#          - create_keyboard_map function           
#          - update_efficient_key_map function       
# 
# The GameState class contains all the data and
# methods for a single game. After the game is over, 
# it continues to hold the historical data for that 
# game and a new GameState must be created to play
# a new game.
# 
# The text_colors class is for coloring terminal output 
# on unix machines.

# The create_keyboard_map function maps alphabetical  
# numbers to their initial state (plain) in QWERTY... 
# order, using Python's sorted dictionary ability.

# update_efficient_key_map updates the key map that 
# uses letter color as keys and letters as values.
##########################################################

import re
import random
import json
import backend_setup
from uuid import uuid4
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

  def __init__(self, given_uuid=None, user_id="Anon", fromCache=False, randomWord=True):
    backend_setup.print_err(f"initializing a new game state for {user_id}")
    if not fromCache:
      self.data = {}
      self.data['user_id'] = user_id
      new_uuid = uuid4()
      self.data['uuid'] = str(new_uuid)
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
      self.data['solution'] = "reset" ### TODO - hardcoded for testing
      self.data['guess_history'] = []
      self.data['current_guess'] = ''
      self.data['guess_map'] = []
      self.data['progress'] = "in progress"
      self.data['public_solution'] = ""
    else:
      if given_uuid:
        self.create_new_from_cache(given_uuid)
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

  def set_random_solution(self, common_words):
    rand_max = len(common_words)
    todays_word_index = ""
    while todays_word_index not in common_words:
        todays_word_index = str(random.choice(range(rand_max)))
    todays_word = common_words[todays_word_index]
    self.data['solution'] = todays_word
    if CHEATING: self.data['solution'] = 'cheat'
    return None

  def get_public_data(self):
    # For returning parts of data that should be given to the client, ie, not the solution.
    public_data = {}
    backend_setup.print_err(f'Creating new dictionary object for public data for {self.data["uuid"]}.')
    if self.data['public_solution'] != "":
      public_data['public_solution'] = self.data['public_solution']
    for field in ['uuid', 'user_id', 'progress', 'turn', 'guess_history', 'guess_map', 'efficient_key_map']:
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

