# Progress journal.

### 4/15/2022

*Three Body Problem*

The project is stuck.  I started with a system design that included an 
API for the Polywordle server, the JSON responses, and the endpoints 
send to the API.  This worked.  I then made a PHP script that consumes 
the API. It sends HTTP requests to the API, interprets the JSON 
response, and translates it into a frontend in HTML/CSS. I created
the PHP script mainly to do sanity tests for the API.

Unfortunately none of the components really work together. 

The JSON response body needs more fields, and at the same time, it is 
bloated, sending the same data in 2 different structures. 

The API cannot handle certain requests without throwing exceptions. 
It also behaves in weird ways that I don't understand. Sometimes it 
tries to redirect the user in ways I don't understand either.

The PHP backend is somewhere between a client and a backend. It 
generates requests to the API, but it also makes the frontend. 
I have very little ability with PHP and every function needs 
15 minutes of debugging and syntax research.  It is hardcoded 
and monolithic.

The HTTP requests are not thought out ahead of time. I don't know
when to use GET and when to use POST.  The browser sends POST
requests to the PHP script. The PHP script sends GET requests
to the API.

If I try and build any one of these 4 pieces I change how it works
for everything else. It is time to sketch out a more detailed
system design.


### 4/16/2022

*Testless Driven Development*

Development today has been very difficult because I have little
experience with testing APIs. The front end I tried to whip-up 
to test the API with ended up being another project that has 
taken up as much time as the API since development started.

Today may be spent researching cURL or downloading POSTMAN or
otherwise coming up with testing scripts.  It may be spent continuing
to develop the PHP 'test' client that consumes the API.

As far as the API specifications are concerned, I was inspired by
a lecture by Les Hazlewood at Oktane17 called "Beautiful REST+JSON
APIs" [1]  <https://yewtu.be/watch?v=MiOSzpfP1Ww> Hazlewood's 
model for a REST API is different from contemporary models. The model 
he presents has an API response that contains all of the necessary 
data in each response and does not rely on the Header field of an 
HTTP request, ie GET, POST. This was interesting because I like 
when software is resilient and simple. In theory my API could deliver 
all of the data for a user, provided the right authorization, and let 
the client parse the data. The client would have data for every game, 
including guess history, solutions to finished games, etc in each
response. I like researching different paradigms but modifying the 
project scope or requirements at this point would be a bad idea.

While I may be developing myself into a corner by forcing the data in
every response and request take the form of JSON, and by using
GET/POST/PUT/DELETE headers to force the consumer to use HTTP, 
the reality is that, as Hazlewood says, the vast majority of modern 
API's don't use this paradigm. Since this is a portfolio project 
and not a passion project I might as well go with the accepted 
practices instead of following neat "road less taken," "better" 
ways of doing things.
 
I will say that using JSON definitely made cURL commands more 
expensive because I couldn't just say `curl <url> -F 
"game_uuid=<uuid>"`; I have to do... like, `curl -X POST <url> 
-H "Content-Type: application/json" -d "<JSON data>"`. This is easy 
in Flask, and presumably easy in JavaScript, but not when I am
trying to send out a single request to unit test my program.


*Itempotency*

Idempotency is actually a lot more important than I thought. It did 
not seem like a huge deal at first, since it's a silly sounding 
word describing a somewhat abstract concept. After thinking about the 
currently available endpoints and their HTTP methods, I've learned 
that API v1 currently violates the concept of idempotency and as 
such should be modified in-place before being worthy of the title v1.

GET, PUT, and DELETE are three idempotent HTTP methods. There are 
other HTTP methods but they are out of the scope of v1 and this 
project entirely. I like to think that GET is idepoptent because 
when you reload a web page you get the same result again and the 
server doesn't really care.

Currently sending a GET request to /v1/game is not idempotent. 
It creates a new server resource; namely, a new game, and it returns 
the UUID of the new game.  This was cool when I was testing because 
I could generate a new UUID to test with just by directing my web 
browser to the endpoint, but it is not cool with RESTful API 
standards.

I will have to change /v1/game to only create new games on a POST 
request.  People seem to disagree on whether POST requests **have** 
to have data payloads. I am good with using POSTs with no payload.


