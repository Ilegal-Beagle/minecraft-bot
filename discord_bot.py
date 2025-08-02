# discord_bot.py

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

    # MISC ----------------------------

    # meant for use in the mc_action fucntion only
    # returns a list like so: [action, sender mc username]
    def _parse_command(self, cmd_str):
        # cmd string format: !mc_action action username(optional)
        cmd = []

        cmd_str = cmd_str.replace(f"{self.db.command_prefix}mc_action ", "")

        sr_actions = self.mc_bot.sender_req_actions
        sr_action = next((_ for _ in sr_actions if _ in cmd_str), None)

        if sr_action:
            cmd.append(sr_action)
            cmd_str.replace(sr_action, "")
            
            cmd.append(cmd_str.strip()) # should be only the username at this point

        else:
            cmd.append(cmd)

        return cmd


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
            command = self._parse_command(ctx.message.content)

            if not command:
                await ctx.send(f"usage: {self.db.command_prefix}mc_action "
                    f"'action' 'username'\nor: {self.db.command_prefix}"
                    "mc_action 'action'")
                return
            
            if command[0] not in self.mc_bot.actions:
                await ctx.send(f"action '{command[0]}' does not exist")
                return

            # if command requires sender
            if len(command) == 2:
                if command[1]:
                    try:
                        self.mc_bot.actions[command[0]](command[1])
                    except Exception as e:
                        print(f"error: {e}")

                else:
                    await ctx.send(f"usage: {self.db.command_prefix}mc_action "
                                   f"{command[0]} 'username'")
                    return
            
            else:
                try:
                    self.mc_bot.actions[command[0]]()
                except Exception as e:
                    print(f"error: {e}")


        # =====================================================================
        # VOICE CHAT EVENTS
        # =====================================================================

        # this may not be used until after i can get text to speech completed



if __name__ == "__main__":
    minecraft_bot = mcbot.Bot('localhost', 3000, 'python', '1.21')
    discord_bot = DiscordBot(token, minecraft_bot)
