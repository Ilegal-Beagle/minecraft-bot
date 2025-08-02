# discord_interface.py

# this does...
# 

import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
import logging
from dotenv import load_dotenv
import os

import asyncio

import minecraft_interface as mcbot


load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord_bot.log', encoding='utf-8', mode = 'w')
logging.basicConfig(level=logging.DEBUG, handlers=[handler])


class DiscordBot:

    def __init__(self, token, mc_bot=None):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.voice_states = True
        self.db = commands.Bot(command_prefix="!", intents=intents)

        self.mc_bot = mc_bot
        self.setup_events(self.db)
        self.db.run(token, log_handler=handler, log_level=logging.DEBUG)


    def add_mc_bot(self, mc_bot):
        try:
            assert isinstance(mc_bot, mcbot.Bot)
            self.mc_bot = mc_bot
        except AssertionError:
            print("invalid type for bot")
            return
        
    def vc_play_sound(self, voice_client, audio_filename):
        try: 
            source = FFmpegPCMAudio(audio_filename)
            voice_client.play(source)

        except Exception as e:
            print(f"error in play_sound: {e}")


    def setup_events(self, bot):
        # =====================================================================
        # CHAT EVENTS
        # =====================================================================

        # VOICE CHAT ----------------------------------------------------------
        @bot.command(pass_context = True)
        async def join_voice(ctx):

            if not ctx.author.voice:
                await ctx.send("not without you broslice")
                return
    
            voice_channel = ctx.author.voice.channel
            try:
                voice = await voice_channel.connect()
                await ctx.send(f"joined {voice_channel.name}")

                # funny test audio
                self.vc_play_sound(voice, "sounds/metal.wav")

            except Exception as e:
                print(f"Error joining {voice_channel.name}: {e}")

        @bot.command(pass_context = True)
        async def leave_voice(ctx):

            if not ctx.voice_client:
                await ctx.send("i'm not even in there homeslice")
                return
                
            await ctx.guild.voice_client.disconnect()
            await ctx.send("dippin' homie")

        

        # MINECRAFT SERVER ----------------------------------------------------

        # @bot.command(pass_context = True)
        # async def join_server(ctx):
        #     if not mc_bot:
        #         print("No minecraft bot to call")
        #         return
            
        #     try:
        #         mc_bot = mcbot.Bot('localhost', 3000, 'python', '1.21')
        #         await ctx.send(f'joined server successfully!')

        #     except Exception as e:
        #         await ctx.send(f"ERROR in function 'join_server': {e}, {type(e)}")

        # mc_action executes the mc_bot action by using its dictionary of 
        # keys and function values
        @bot.command()
        async def mc_action(ctx):
            msg = ctx.message.content
            msg = ctx.message.content.split(' ', 1)[1:]

            if not msg:
                await ctx.send(f"usage: {self.db.command_prefix}mc_action 'action' "
                               f"'username'\nor: {self.db.command_prefix}mc_action "
                                "'action'")
            else:
                msg = str(msg)

            # parse command for sender required action
            sr_action = None 
            sr_action = next((_ for _ in self.mc_bot.sender_req_actions if _ in msg), None)
            
            if sr_action:
                msg = msg.replace(sr_action, "").strip("[]' ")
                
                # if user did not specify sender for sender required action
                if not msg:
                    await ctx.send(f"usage: {self.db.command_prefix}mc_action {sr_action} "
                                    "'username'")
                    return
                
                # do the sender required action
                else:
                    try:
                        # msg should be the username
                        self.mc_bot.actions[sr_action](msg)
                    except Exception as e:
                        print(f"error: {e}")
            
            else:
                msg = msg.strip("[]' ")

                if msg not in self.mc_bot.actions:
                    await ctx.send(f"action '{msg}' does not exist")
                    return
                
                else:
                    try:
                        self.mc_bot.actions[msg]()
                    except Exception as e:
                        print(f"error: {e}")
            

        # =====================================================================
        # VOICE CHAT EVENTS
        # =====================================================================

        # this may not be used until after i can get text to speech completed



if __name__ == "__main__":
    minecraft_bot = mcbot.Bot('localhost', 3000, 'python', '1.21')
    discord_bot = DiscordBot(token, minecraft_bot)
