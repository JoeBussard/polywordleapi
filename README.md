# Polywordle API 💻

**Welcome 😀 to the Polywordle API**

Polywordle is a server for playing wordle-type games.
It uses a basic REST API for interacting with each client.
Once the server is up and running, send requests to `127.0.0.1:5000` with game instructions. This can be done with a front-end client or even Postman or 
`curl` if you are so inclined 😮. You can play any time you want. You 
get an infinite number of words per day. Currently there are official front-end clients for Discord bots and PHP/HTML/CSS static web pages in development.

### Installation 🛠️

**Linux 🐧** & **macOS** 🍎

`git clone https://github.com/JoeBussard/polywordleapi`

`cd polywordleapi`

`pip install requirements.txt`

### Running 👟

`cd src/api`

`export FLASK_APP=flask_app.py`

`flask run`

The server will now be running and API endpoints are at `127.0.0.1:5000`

### Interaction 🎮

Have your client send an empty `POST` request to `/v1/game` to get
a UUID for your game.

Send a `GET` request to `/v1/game/<your_uuid>` to see your game's status

Send a `POST` request with `guess=<your_guess>` as a JSON object or 
as a form field to `/v1/game/<your_uuid>` to make a new guess.

That is all you need to play the game. Have fun.

*This is a portfolio project by a new university grad. Let me know 
if you like it and your company is hiring* 🎓
