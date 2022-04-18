# Polywordle API 💻

**Welcome 😀 to the Polywordle API**

You can download and run this API on your own server to host a game of 
Polywordle. Just make your own client, (which could even be Postman or 
`curl` if you are so inclined 😮) and you can play any time you want. You 
get an infinite number of words per day.

### Installation 🛠️

**Linux 🐧**

`git clone https://github.com/JoeBussard/polywordleapi`

`pip install requirements.txt`

### Running 👟

`cd polywordleapi/src/api`

`export FLASK_APP=flask_app.py`

`flask run`

The API server will now be running at `127.0.0.1:5000`

### Interaction 🎮

Have your client send an empty `POST` request to `/v1/game` to get
a UUID for your game.

Send a `GET` request to `/v1/game/<your_uuid>` to see your game's status

Send a `POST` request with `guess=<your_guess>` as a JSON object or 
as a form field to `/v1/game/<your_uuid>` to make a new guess.

That is all you need to play the game. Have fun.

*This is a portfolio project by a new university grad. Let me know 
if you like it and your company is hiring* 🎓


