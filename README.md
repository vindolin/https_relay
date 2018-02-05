# https_relay.py

Simple python program that relays HTTP connections to HTTPS targets.

I wrote this because Microcontrollers have a hard time communicating with https hosts.

Start the relay:

```bash
python https_relay.py -p 8077
```

Example showing how to post a message with curl to api.telegram.org:

```bash
curl -X POST "http://localhost:8077/botXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/sendMessage" \
-d "chat_id=XXXXXXXXX&text=Alarm!" --header "X-Relay-Target: api.telegram.org"
```

Just replace the original host:port with the address of the relay and provide the target host in the X-Relay-Target header.

Or if you can't add the X-Relay-Target header, you can start the relay with a default target host this way:

```bash
python https_relay.py -p 8077 -t api.telegram.org
```

__No chunked transfers supportet yet!__
