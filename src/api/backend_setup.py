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
        'uuid',
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
      if game_state_object.data['uuid'] in self.game_states.keys():
        print_err(f'Updating game state for game {game_state_object.data["uuid"]} in cache {self.cache_id}')
      else:
        print_err(f'Saving new game state for game {game_state_object.data["uuid"]} in cache{self.cache_id}')
        if len(self.game_states.keys()) > 1000:
          print_err(f'Rate limit: Refusing to create more than 100 games at a time')
          raise 
          return {"error":"Game state cache full"}
      self.game_states[game_state_object.data['uuid']] = game_state_object
      return {"success":"game state updated/saved"}

    def save_game_data_to_cache(self, uuid, game_data):
      # user_id because only one game at a time per user
      # game_data should be a json file.
      if uuid in self.game_states_data.keys():
        print_err(f'Updating game state for game {uuid} in cache {self.cache_id}')
      else:
        print_err(f'Saving new game state for game {uuid} in cache{self.cache_id}')
        self.game_states_data[uuid] = {}
      if type(game_data) != dict:
        print_err(f'Data for {uuid} was not a dict')
        return False

      for key in game_data.keys():
        # if type(key) != 'str':
        #   print_err(f'Tried saving something weird to {self.cache_id}')
        #   return False
        str_key = str(key).lower()
        if str_key in self.acceptable_state_fields:
          self.game_states_data[uuid][str_key] = game_data[str_key]
          print_err(f'Saved {str_key} for {uuid} in cache.')
        else:
          print_err(f'Err: {str_key} is not an acceptable field to be cached.')

    def load_game_data_from_cache(self, uuid):
      ### Just loads a game from the cache
      if uuid in self.game_states_data.keys():
        print_err(f'Loading game data for {uuid} from cache.')
        return self.game_states_data[uuid]
      else:
        print_err(f'No game data found for {uuid} in cache {self.cache_id}')
        return False

    def delete_game_data_from_cache(self, uuid):
      ## Make sure you auth'ed before calling this
      if uuid in self.game_states_data.keys():
        print_err(f'Deleting game data for {uuid} from cache.')
        del self.game_states_data[key]
        return True
      else:
        print_err(f'Cannot delete game data for {uuid} from cache: User not found')
        return False

    def save_cache_to_disk(self, file_name):
      print_err("Reserved for saving this cache to disk")

    def load_cache_from_disk(self, file_name):
      print_err("Reserverd for loading game data from disk to a cache.")

    def dump_cache_to_stderr(self):
      print_err(f'Printing data stored in cache {self.cache_id}...')
      #print_err(json.dumps(self.game_data, indent=2, sort_keys=True))


def start_up_game_backend(cache_id):
    """ Boot strapping the game server"""
    print_err("Booting up Polywordle v.0.0.1")

    my_cache = GameStateCache(cache_id)

    common_words, all_words = load_dicts_from_json()

    return my_cache, common_words, all_words

