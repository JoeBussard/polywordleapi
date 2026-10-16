#!/bin/python
# copyright 2022 joe bussard
####################################################
#         backend_setup.py
# 
#  Includes:   - print_err  function
#              - load_dicts_from_json function
#              - GameStateCache function
#              - start_up_game_backend function
#
# The print_err function can be used instead of print() to
# print directly to stderr.
#
# The load_dicts_from_json reads JSON files "all_words.json"
# and "common_words.json" from disk and saves them as 
# 2 dictionaries in memory.
#
# The GameStateCache has a dictionary of active games,
# As well as some functions for saving the cache to disk
# in case the server needs to scale and save games to disk
# instead of in memory.
#
# The start_up_game_backend function creates a new 
# GameStateCache and loads the dictionaries into memory to 
# bootsrap a new instance of the Polywordle server.
########################################################

import json
import os
import sqlite3
import time
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
    # all_words is only ever used for membership tests, so hand it out as a set: O(1) instead of
    # building a list of 16k values on every guess (issue #49). common_words stays a dict because
    # random solutions are picked by numeric key.
    return common_words, set(all_words.values())

class GameStateCache:
    # Class wide variables............
    MAX_GAMES = 20000   # ~ a few tens of MB; protects a small server from game-spam

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

    def __init__(self, cache_id, db_path=None):
      ## I will use some sort of hashing function to use different caches
      ## If i ever scale to that point
        self.cache_id = cache_id
        self.game_states = {}
        self.game_states_data = {}
        # issue #73: games are kept in memory for speed but written through to SQLite so a
        # restart does not forget them. db_path None = memory only (tests, local runs).
        self.db = None
        if db_path:
          self.db = sqlite3.connect(db_path, check_same_thread=False)
          self.db.execute('create table if not exists games (uuid text primary key, data text not null, updated real not null)')
          self.db.commit()
          self._load_from_db()
        print_err(f'Created a new game state cache ({"sqlite: " + db_path if db_path else "memory only"}).')

    def _load_from_db(self):
      import backend_create_new_game
      rows = self.db.execute('select uuid, data from games order by updated').fetchall()
      for uuid, data in rows:
        gs = backend_create_new_game.GameState(fromCache=True)
        gs.data = json.loads(data)
        self.game_states[uuid] = gs
      print_err(f'Loaded {len(rows)} games from disk.')

    def _persist(self, game_state_object):
      if self.db is None: return
      self.db.execute('insert or replace into games (uuid, data, updated) values (?, ?, ?)',
                      (game_state_object.data['uuid'], json.dumps(game_state_object.data), time.time()))
      self.db.commit()

    def _forget(self, uuid):
      if self.db is None: return
      self.db.execute('delete from games where uuid = ?', (uuid,))
      self.db.commit()


    def save_game_state_to_cache(self, game_state_object):
      if game_state_object.data['uuid'] in self.game_states.keys():
        print_err(f'Updating game state for game {game_state_object.data["uuid"]} in cache {self.cache_id}')
      else:
        print_err(f'Saving new game state for game {game_state_object.data["uuid"]} in cache{self.cache_id}')
        # Memory guard: keep at most MAX_GAMES games; evict the oldest when full.
        if len(self.game_states) >= self.MAX_GAMES:
          oldest_uuid = next(iter(self.game_states))
          print_err(f'Cache full ({self.MAX_GAMES} games): evicting oldest game {oldest_uuid}')
          del self.game_states[oldest_uuid]
          self._forget(oldest_uuid)
      self.game_states[game_state_object.data['uuid']] = game_state_object
      self._persist(game_state_object)
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
        del self.game_states_data[uuid]
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

    # POLYWORDLE_DB=/path/to/games.sqlite3 turns on persistence; unset = memory only.
    my_cache = GameStateCache(cache_id, os.environ.get('POLYWORDLE_DB') or None)

    common_words, all_words = load_dicts_from_json()

    return my_cache, common_words, all_words

