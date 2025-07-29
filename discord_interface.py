# discord_interface.py

# this does...
# 

import discord
from discord import FFmpegPCMAudio
import logging
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord_bot.log', encoding='utf-8', mode = 'w')
logging.basicConfig(level=logging.DEBUG, handlers=[handler])

# bot permissions are included in these intents
# read Gateway Intents in the discord api docs for more info
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

client = discord.Client(intents=intents)

# handling events
@client.event
async def on_ready():
    print(f"We are ready to go in, {client.user.name}!")

@client.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content == "!join":
        print("Invite recieved!")

        if message.author.voice.channel:
            channel = message.author.voice.channel
            try:
                voice_client = await channel.connect()
                print(f"Voice client state: {voice_client.is_connected()}")
                audio_source = discord.FFmpegPCMAudio("1-minute-of-silence.mp3")
                voice_client.play(audio_source, after=lambda e: print(f"player error: {e}") if e else None)
            except Exception as e:
             print(e)
        else:
            print("no exception and not connected")

client.run(token, log_handler=handler, log_level=logging.DEBUG)




