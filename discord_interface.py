# discord_interface.py

# this does...
# 

import discord
from discord import FFmpegPCMAudio
import logging
from dotenv import load_dotenv
import os
import minecraft_interface as mcbot
from discord.ext import commands

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord_bot.log', encoding='utf-8', mode = 'w')
logging.basicConfig(level=logging.DEBUG, handlers=[handler])

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
client = discord.Client(intents=intents)
mc_bot = None

@bot.command()
async def hello(ctx):
    await ctx.send("Hello there!")

@bot.command()
async def join_server(ctx):
    try:
        mc_bot = mcbot.Bot('localhost', 3000, 'python', '1.21')
        await ctx.send(f'joined server successfully!')

    except Exception as e:
        await ctx.send(f'ERROR: {e}, {type(e)}')

@bot.command()
async def come(ctx):
    try:
        mc_bot.come()

    except AttributeError as e:
        await ctx.send(f'ERROR: Attribute error. Have you started the bot?')
    
    except Exception as e:
        await ctx.send(f'ERROR: {e}, {type(e)}')

@bot.command()
async def join_voice(ctx):
    pass

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

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
client.run(token, log_handler=handler, log_level=logging.DEBUG)

