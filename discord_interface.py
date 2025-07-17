# discord_interface.py

# this does...
# 

import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord_bot.log', encoding='utf-8', mode = 'w')

# bot permissions are included in these intents
# read Gateway Intents in the discord api docs for more info
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# this gets the bots attention
bot = commands.Bot(command_prefix='!', intents=intents)

# handling events
@bot.event
async def on_ready():
    print(f"We are ready to go in, {bot.user.name}!")
    
bot.run(token, log_handler=handler, log_level=logging.DEBUG)



