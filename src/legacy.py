#!/bin/python
# copyright 2022 joe bussard

import re
import random
import json

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
text_hash = {'yellow':text_colors.YELLOW,'green':text_colors.GREEN,'red':text_colors.RED,'white':'', 'end':text_colors.END}

performance_hash = {1:'Unbelievable!', 2:'Spectacular!', 3:'Amazing!',4:'Well done.',5:'Pretty good.', 6:'That was close!'}


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


def load_dicts():
    """Opens the 2 dictionaries in use, a smaller dictionary
    of more common words, and a larger dictionary with
    words that the user could guess.
    TODO: Make this an API call to improve space constraints"""
    common_words = []
    all_words = []
    with open('common-fives') as f:
        data_common = f.read()
        for x in data_common.split():
            common_words += [x]
    with open('all-fives') as f:
        data_all = f.read()
        for word in data_all.split():
            all_words += [word]
    return common_words, all_words

def check_guess_optimized(guess, word):
    """trying to get this to o(n) time, but still o(n^2) to check yellows."""
    guess_hash, word_hash, result_hash = {}, {}, {}
    for i in range(5):
        guess_hash[i] = guess[i]
        word_hash[i] = word[i]
        result_hash[i] = "red"
        if guess_hash[i] == word_hash[i]:
            result_hash[i] = "green"
            guess_hash[i], word_hash[i] = "", ""

    for guess_key in range(5):
        for word_key in range(5):
            if guess_hash[guess_key] == word_hash[word_key] and result_hash[guess_key] == "red":
                result_hash[guess_key] = "yellow"
                guess_hash[guess_key], word_hash[word_key] = "", ""
    return result_hash

def update_keyboard(key_map, color_map, guess):
    """Input is a keyboard map. It updates that keyboard map and returns it.
    The keyboard map connects the keys 'qwerty....bnm' to collors 'red', 'yellow', or 'green'"""
    # updates the keyboard
    guess_list = list(guess)
    for x in color_map:
        if key_map[guess_list[x]] != 'green':
            key_map[guess_list[x]] = color_map[x]
    #print (key_map)
    return key_map

def create_keyboard_map():
    """Creates the keyboard map. Initializes everything to "grey" because
    the user does not know if the letter is in use or not."""
    keys_only = ['q','w','e','r','t','y','u','i','o','p','a','s','d','f','g',
            'h','j','k','l','z','x','c','v','b','n','m']
    key_map = {}
    for i in keys_only:
        i = i.lower()
        key_map[i] = 'gray'
    return key_map

def pretty_print_keyboard(key_map):
    """prints the keyboard, color-coded to show which letters are in the word."""
    print("")
    for y in key_map:
        if y == 'a':
            print(f'\n\n  ', end='')
        elif y == 'z':
            print(f'\n\n    ', end='')
        x = y.upper()
        if key_map[y] == 'gray':
            print(                    x,                  "  ", sep='', end='')
        elif key_map[y] == 'yellow':
            print(text_colors.YELLOW, x, text_colors.END, "  ", sep='', end='')
        elif key_map[y] == 'green':
            print(text_colors.GREEN,  x, text_colors.END, "  ", sep='', end='')
        elif key_map[y] == 'red':
            print(text_colors.RED,    x, text_colors.END, "  ", sep='', end='')
    print("")
    print("")

def update_all(guess, word, key_map, index_map_history):
    """Run this command after each turn.  It updates the keyboard map,
    and it updates the index map history. Index map history is what I
    call the mapping of letters in each guess to their colors."""
    # check_guess returns a map from [0...4] to [green, yellow, etc]
    index_color_map = check_guess_optimized(guess, word)
    index_map_history.append(index_color_map)
    key_map = update_keyboard(key_map, index_color_map, guess)
    # i dont know what this should return
    return index_color_map, key_map

def create_emoji_hash():
    """returns a dict object hashmap that maps color words to emojis"""
    emoji_hash = {}
    emoji_hash['white']  = '⬜'
    emoji_hash['yellow'] = '🟨'
    emoji_hash['green']  = '🟩'
    emoji_hash['black']  = '⬛'
    emoji_hash['red']    = '🟥'
    return emoji_hash

def pretty_print_share_box(index_color_map_history, emoji_hash):
    """prints the box you get at the end that visualizes guess history"""
    for row in index_color_map_history:
        for column in row:
            print(emoji_hash[row[column]], sep='', end='')
        print("")

def generate_share_box(index_color_map_history, emoji_hash):
    """creates the box you get at the end that visualizes guess history,
    but it does not print it, returns a string."""
    my_string = ''
    for row in index_color_map_history:
        for column in row:
            my_string += emoji_hash[row[column]]
        my_string += f'\n'
    return my_string

def pretty_print_blank_lines(emoji_hash, color):
    """directly prints blank lines with the emoji block of a given color.
    used to visualize the remaining guesses."""
    for x in range(0, 5):
        print("", emoji_hash[color], " ", sep='', end='')
    print(f"\n")

def generate_share_text(guesses, index_color_map_history, emoji_hash, todays_word_game_id):
    """generates the full share-text that you copy and paste for friends."""
    string = ''
    string += "Polywordle " + str(todays_word_game_id)
    guess_num = guesses if guesses < 6 else 'X'
    string += " " + str(guesses) + "/6"
    string += f'\n'
    string += generate_share_box(index_color_map_history, emoji_hash)
    return string

def pretty_print_index_color(index_color_map, guess, emoji_hash):
    """prints the letters for a guess in the colors that correspond to its game status."""
    guess_list = list(guess)
    for x in index_color_map:
    #    print('line 122',x)
        print(text_hash[index_color_map[x]], guess[x].upper(), text_colors.END,"  ", sep='', end='')
    print(f"\n")

def get_todays_word(common_words):
    """picks a random word and obfuscates it."""
    rand_max = len(common_words)
    todays_word_index = ""
    while todays_word_index not in common_words:
        todays_word_index = str(random.choice(range(rand_max)))

    fake_id_letters = 'abcdefABCDEF1234567890'
    todays_word_game_id = random.choice(fake_id_letters) + str(random.choice(range(10))) + str(todays_word_index) + random.choice(fake_id_letters)
    todays_word = common_words[todays_word_index]
    return todays_word_game_id, todays_word

def get_predetermined_word(common_words, word_game_id):
    """could be called from a client. decoding is done server-side."""
    real_word_index = str(decode_word_game_id(word_game_id))
    predetermined_word = common_words[real_word_index]
    return predetermined_word

def decode_word_game_id(word_game_id):
    word_id_without_obfuscation = word_game_id[2:-1]
    return word_id_without_obfuscation

def ask_user_new_word_or_word_from_id(common_words):
    print("Enter the Share ID for the word you want to play or press ENTER for a random word: ")
    user_input = str(input())
    decoded_word = ""
    if len(user_input) < 8 and len(user_input) > 3:
        try:
            decoded_word = get_predetermined_word(common_words, user_input)
        except:
            decoded_word = ""
            user_input = ""
    return user_input, decoded_word

class GameStateCache:
    def __init__():
        pass
    pass


def test2():
    """main game logic. initializes several variables, then jumps into the main loop:
    1. compare a guess
    2. print the new board
    3. repeat."""
    guess_history = []
    index_map_history = []
    common_words, all_words = load_dicts_from_json()
    game_day = 0
    shared_id, shared_word = ask_user_new_word_or_word_from_id(common_words)
    if shared_word and shared_id:
        todays_word_game_id = shared_id
        todays_word = shared_word
    else:
        todays_word_game_id, todays_word = get_todays_word(common_words)
    if CHEATING: print("[cheating] todays word is", todays_word)
    key_map = create_keyboard_map()
    emoji_hash = create_emoji_hash()
    guesses = 0

    print("Welcome to Polywordle [version 0.2]")

    # Print the "blank" board with just empty squares.
    for x in range(guesses, 6):
        pretty_print_blank_lines(emoji_hash, 'white')
    pretty_print_keyboard(key_map)

    print("this is key_map")
    json_status_dict = {}
    json_status_dict['keyboard'] = key_map
    json_status_dict['game_id'] = 0
    json_status_dict['turn'] = guesses
    print(key_map)
    print("this is the json response")
    print(json_status_dict)
    print(json.dumps(json_status_dict, indent=4))

    while guesses < 6:
        invalid_guess = True
        while invalid_guess:
            current_guess = input(("Guess #"+ str(guesses+1)+ ": "))
            if len(current_guess) == 5:
                pattern = re.compile("[A-Za-z]+")
                if pattern.fullmatch(current_guess):
                    if current_guess.lower() in list(all_words.values()): break
                    else: print("Not in dictionary.")
                else: print("Must only be letters.")
            else: print("Must be 5 letters.")

        current_guess = current_guess.lower()

        guesses += 1
        # note sure if this is right
        index_color_map, key_map = update_all(current_guess, todays_word, key_map, index_map_history)
        guess_history.append(current_guess)

        print("now printing the json response")
        json_status_dict['keyboard'] = key_map
        json_status_dict['index_color_map_history'] = index_map_history
        json_status_dict['turn'] = guesses
        json_status_dict['guess_history'] = guess_history
        print(json.dumps(json_status_dict, indent=4))


        # clear screen
        for x in range(50):print("")
        for x in range(guesses):
            pretty_print_index_color(index_map_history[x], guess_history[x], emoji_hash)

        for x in range(guesses, 6):
            pretty_print_blank_lines(emoji_hash, 'white')

        pretty_print_keyboard(key_map)
        if current_guess == todays_word:
            break
    if current_guess == todays_word:
        print(text_hash['green'], end='')
        print(performance_hash[guesses])
        print(text_hash['end'], end='')
    else:
        print(text_hash['red'], "Bummer! The word was ", todays_word.upper(), text_hash['end'], sep='')
    print(f"\nIf you feel this word is unfair, please open an issue at ", text_hash['yellow'], "https://GitHub.com/JoeBussard/PolyWordle", text_hash['end'], sep='')

    print(f"\nShare your score:\n")
    print(generate_share_text(guesses, index_map_history, emoji_hash, todays_word_game_id))

    exit(0)

test2()
