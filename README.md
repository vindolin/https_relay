# https_relay.py

Simple python program that relays http connections to https targets.
Microcontrollers have a hard time communicating with https hosts.

Start the relay:

```bash
python https_relay.py -p 8077
```

Example usage to post a message with curl to api.telegram.org:

```bash
curl -X POST "http://localhost:8077/botXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/sendMessage" \
-d "chat_id=XXXXXXXXX&text=Alarm!" --header "X-Relay-Target: api.telegram.org"
```

Or if you can't add the X-Relay-Target header, you can start the relay with a default target host this way:

```bash
python https_relay.py -p 8077 -t api.telegram.org
```
