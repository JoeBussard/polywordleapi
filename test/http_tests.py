import requests
import json

def test_new_game():
  confirm = input("Test a new game y/[N]?")
  if confirm != "Y": return
  r = requests.get("http://127.0.0.1:5000/v1/game")
  print(r)
  uuid_str = str(json.loads(r.content.decode('utf-8')))
  print(uuid_str)



def test_game_data():
  print("testing GET game data")
  given_uuid = input("Paste the uuid")
  if given_uuid == None or given_uuid == "N":
    return
  r = requests.get(f"http://127.0.0.1:5000/v1/game/{given_uuid}")
  

def test_new_guess():
  print("testing POST new guess")
  given_uuid = input("Paste the uuid")
  if given_uuid == None or given_uuid == "N":
    return
  guess_request_json = {}
  user_guess = input("Input your guess")
  guess_request_json['guess'] = user_guess
  #r = requests.get(f"http://127.0.0.1:5000/v1/game/{given_uuid}")
  #print(r)
  #print(r.content)
  print("now trying the guess")
  s = requests.post(f"http://127.0.0.1:5000/v1/game/{given_uuid}", data = {'guess':user_guess}) # guess_request_json)
  
  

