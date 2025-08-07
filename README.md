# Minecraft Bot

## Installing

**NOTE**: You will need to set up a discord bot to use the bot AND you will need the discord API token.

### Docker

Make sure you have Docker Desktop installed and in the repo directory. Then run:
```
docker built -t minecraft-bot .
docker run minecraft-bot:latest
```

### Non-Docker
1. `sudo apt install nodejs npm espeak-ng`

2. `npm install mineflayer`

4. `pip install -r requirements.txt`

5. The mineflayer module is currently breaking with Python.
There is a file in `pathces/chat.js` that has a fix that works with it for now.
Replace the file in `node_modules/minecraft-protocol/client/chat.js` with the file in `patches`.