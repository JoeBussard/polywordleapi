## Version 1

**API**

You can create a new game. You can make guesses on that game. You get the status of your game upon request. You can create as many new games as you want.

### Endpoints

`/` - `<any method>` - Pings the server and responds which version to use

`/v1` - `<any method>` - Pings the server and responds how to start a new game

`/v1/newgame` - `POST` - Creates a new game and returns the `game_uuid` in JSON format.

`/v1/game/<uuid>` - `GET` - Returns the state of a game in JSON format

`/v1/game/<uuid>` - `POST` - Posts a new guess to a game.  Requires that the user include a guess in the request body. Can be JSON or encoded in form.

Game status JSON includes `is_custom_solution` (true when the game was created with a chosen solution) and `solution_is_real_word` (false when that chosen solution is not in the dictionary; guesses must still be dictionary words, or exactly the solution).
