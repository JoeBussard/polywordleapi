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
