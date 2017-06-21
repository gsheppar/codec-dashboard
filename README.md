# codec-sparkbot
Special thanks to K.Corbin and G.Sheppard for help and examples

Building a Cisco Sparkbot to interface with a Cisco SX Codec and Touch10

This sparkbot can receive alarms from a Codec (using http feedback), and can send commands and messages to a codec using python scripts.  This particular example is configured to do the following, but you can be easily customized:
* Sparkbot remotely checks Codec status
* Sparkbot remotely check Codec diagnostics
* Codec Report an Issue to Sparkbot (using http feedback POST)
* Codec Request In-room Help to Sparkbot (using httpfeedback POST)
* Sparkbot send a message to a Codec
* Sparkbot remotely dial numbers from the Codec


<h1>Files:</h1>

* boy.py = main file that receives POST from codec, and responds to requests from Sparkbot
* envfile = contains all variables (username, password,bot room, id, token etc)
* roomcontrolconfig.xml =  for customizing Touch10 panels
* dockerfile = image parameters
* actions.py = contains functions for interacting with the codec
* templates.py = this contains the xml formatted data structure for various commands that will be sent to the codec


<h1>Tasks:</h1>

1. Install repo and Run Docker
2. Create sparkbot
3. Create sparkbot webhook
4. Add sparkbot to room
5. Configure codec and add webhook
6. Update ENV file with local variables
7. Build and run docker file

<h1> Steps:</h1>
<h2> 1. Install Repo and Docker</h2>
Docker can be downloaded here: https://docs.docker.com/

note: I was running 17.03.1-ce on macOS

Ensure reachability from docker python server and to codec and cisco spark.  I used Ngrok in a terminal window and noted http/https url and insert in the env file and in the sparkbot url.
```
e.g.
    ngrok  http 5000
```
when running, it will look like this:
```
ngrok by @inconshreveable                                                                                                              (Ctrl+C to quit)

Session Status                online
Version                       2.2.4
Region                        United States (us)
Web Interface                 http://127.0.0.1:4040
Forwarding                    http://this.is.the.http.url.you.want -> localhost:5000
Forwarding                    https://this.is.the.https.url.you.want -> localhost:5000

Connections                   ttl     opn     rt1     rt5     p50     p90
                              266     0       0.00    0.00    0.90    2.19

HTTP Requests
-------------

POST /                         200 OK
```

<h2>2. Create sparkbot</h2>
https://developer.ciscospark.com/
create a BOT (My Apps) and generate a token

Create a Space Space and add the Bot
    Make a note of your Bot access token, as you will need it

Confirm the room id, as you'll need it later.
    API Reference > Rooms > List
```
note: the room ID
```

<h2>3. Create webhook</h2>
Create a Webhook for your Sparkbot
   API Reference > Webhook > Create a Webhook
    Add Authorization Bearer token (should be auto populated)
   name=“”
   targetUrl=“" (point to bot.py file)
   resource=messages
   event=created
   (you can list existing ones if needed)


<h2>4. Add sparkbot to room</h2>
Create a room/space in Spark and add your Sparkbot.

Test by sending a message to the bot in your Space.  A message should appear in the docker console logs.
note: the sparkbot will work in both direct (a.k.a 1-on-1)  and group spaces, but this script has been developed for a group room where the codec bot is mentioned in the room and parsed out.

<h2>5. Configure codec and add webhook</h2>
To enable the API on the codec, make sure you have SSH and HTTP/HTTPS enabled.
Create user account for api (optional, but recommended)

ssh into codec and enable httpfeedback (aka webhook)
```
xcommand HttpFeedback Register FeedbackSlot: 1 ServerUrl: http://<ip addr of docker>:5000/codec Format: JSON Expression: /Event
xcommand HttpFeedback Register FeedbackSlot: 1 ServerUrl:  http://<ip addr of docker>:5000/codec Format: JSON Expression: /Configuration
```

To check feedback POSTs are being sent from codec, use CLI commands:
```
    xFeedback register /Status
    xFeedback register /Configuration
    xFeedback register /Events
```

http://www.cisco.com/c/dam/en/us/td/docs/telepresence/endpoint/ce83/codec-sx10-api-reference-guide-ce83.pdf
<h2>6. Update ENV file with local variables</h2>
Set the OS ENV file with Spark bot details, token, roomId, codec user names etc.

<h2>7. Build and run docker file</h2>
Build the file
note: Make sure you are in the correct directory
```
    docker build -t test-server .
```
Run the docker file
    docker run -ti -p 5000:5000 --env-file envfile test-serv

Note: if you are running docker on your pc, you may need to disable any local firewalls if enabled (especially on mac)

test server by opening a browser to http://localhost:5000

end
