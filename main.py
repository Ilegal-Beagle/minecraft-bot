import os, logging
from dotenv import load_dotenv
from discord_bot import DiscordBot

if __name__ == '__main__':
    load_dotenv()
    token = os.getenv('DISCORD_TOKEN')

    handler = logging.FileHandler(filename='discord_bot.log', encoding='utf-8', mode = 'w')
    logging.basicConfig(level=logging.DEBUG, handlers=[handler])

    discord_bot = DiscordBot(token)
