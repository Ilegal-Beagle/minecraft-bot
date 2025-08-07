# discord_bot.py

# this file contains the discord bot for our final project

import discord
from discord.ext import commands

from discord import FFmpegPCMAudio
import pyttsx3

import logging
from dotenv import load_dotenv
import os
import subprocess

import minecraft_interface as mcbot


class DiscordBot:

    def __init__(self, token):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.voice_states = True
        self.db = commands.Bot(command_prefix="!", intents=intents)
        self.mc_bot = None
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)

        self.setup_events(self.db)
        handler = logging.FileHandler(filename='discord_bot.log', encoding='utf-8', mode = 'w')
        logging.basicConfig(level=logging.DEBUG, handlers=[handler])
        self.db.run(token, log_handler=handler, log_level=logging.DEBUG)

    # AUDIO HANDLING ----------------------------
        
    def vc_play_sound(self, voice_client, audio_filename):
        try: 
            source = FFmpegPCMAudio(audio_filename)
            voice_client.play(source)

        except Exception as e:
            print(f"error in play_sound: {e}")
        
    # INTERNAL ----------------------------------

    # meant for use in the mc_action function only
    # returns a list like so: [action, sender mc username]
    def _parse_command(self, cmd_str):
        # cmd string format: !mc_action action username(optional)
        cmd = []

        cmd_str = cmd_str.replace(f"{self.db.command_prefix}mc_action", "")

        sr_actions = self.mc_bot.sender_req_actions
        sr_action = next((_ for _ in sr_actions if _ in cmd_str), None)

        if sr_action:
            cmd.append(sr_action)
            cmd_str = cmd_str.replace(sr_action, "")
            
            cmd.append(cmd_str.strip()) # should be only the username at this point

        else:
            cmd.append(cmd_str)

        return cmd

    def setup_events(self, bot):

        @bot.event
        async def on_ready():
            print(f"{bot.user} is ready")

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
            voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)

            if voice_client and voice_client.is_connected():
                await ctx.send("already vibin whichya brodog")
                return

            try:
                await voice_channel.connect()
                await ctx.send(f"joined {voice_channel.name}")

            except Exception as e:
                print(f"Error joining {voice_channel.name}: {e}")
                return


        @bot.command(pass_context = True)
        async def leave_voice(ctx):
            voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)

            if not ctx.voice_client or not voice_client.is_connected():
                await ctx.send("i'm not even in there homeslice")
                return
                
            await ctx.guild.voice_client.disconnect()
            await ctx.send("dippin' homie")


        @bot.command
        async def _voice_echo(channel, message):

            if not channel.members:
                return
            
            voice_client = discord.utils.get(bot.voice_clients, guild=channel.guild)
            if not voice_client:
                return
            
            try:
                self.tts_engine.save_to_file(message, "sounds/curr_tts.wav")
                self.tts_engine.runAndWait()
                self.vc_play_sound(voice_client, "sounds/curr_tts.wav")
            except Exception as e:
                print(f"Error in say_this: {e}")
                return


        @bot.command()
        async def say_this(ctx):

            print(ctx.message.content)
            msg = ctx.message.content
            msg = msg.replace(f"{self.db.command_prefix}say_this", "")

            if not msg:
                await ctx.send(f"usage: {self.db.command_prefix}say 'message'")
                return
            
            voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
            
            if not voice_client.is_connected():
                await ctx.send("homedog im not in a voice chat bro")
                return
            
            try:
                self.tts_engine.save_to_file(msg, "sounds/curr_tts.wav")
                self.tts_engine.runAndWait()
                self.vc_play_sound(voice_client, "sounds/curr_tts.wav")
            except Exception as e:
                print(f"Error in say_this: {e}")
                return
            

        @bot.command()
        async def tell_this(ctx):
            if not self.mc_bot:
                await ctx.send("the minecraft bot isn't active")
                return
            
            msg = ctx.message.content.replace(f"{self.db.command_prefix}"
                                              "tell_this", "").strip()
            
            print(f"tell_this msg: {msg}")
            if msg:
                self.mc_bot.send(msg)

            else:
                print(f"Usage: !tell_this 'text'")

        # MINECRAFT BOT -------------------------------------------------------

        @bot.command()
        async def join_server(ctx, ip, port, username, version):
            if self.mc_bot:
                await ctx.send("minecraft bot is already active")
                return

            try:
                self.mc_bot = mcbot.Bot(ip, port, username, version, self)
                await ctx.send(f'joined server successfully! ')

            except Exception as e:
                await ctx.send(f"ERROR in function 'join_server': {e}, {type(e)}")


        @bot.command()
        async def leave_server(ctx):
            if not self.mc_bot:
                await ctx.send("the minecraft bot isn't active")
                return
            
            self.mc_bot.quit()
            self.mc_bot = None
            await ctx.send("deuces!")


        # mc_action executes the mc_bot action by using its dictionary of 
        # keys and function values
        @bot.command()
        async def mc_action(ctx):
            if not self.mc_bot:
                await ctx.send("the minecraft bot isn't active")
                return

            command = self._parse_command(ctx.message.content)
            print(command)
            if not command[0]:
                await ctx.send(f"usage: {self.db.command_prefix}mc_action "
                    f"'action' 'username'\nor: {self.db.command_prefix}"
                    "mc_action 'action'")
                return
            
            if command[0].strip() not in self.mc_bot.actions:
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
                    self.mc_bot.wandering = not self.mc_bot.wandering if command[0].strip() == 'wander' else self.mc_bot.wandering
                    self.mc_bot.actions[command[0].strip()]()
                except Exception as e:
                    print(f"error: {e}")

        # =====================================================================
        # VOICE CHAT EVENTS
        # =====================================================================

        # this may not be used until after i can get text to speech completed


if __name__ == "__main__":
    load_dotenv()
    token = os.getenv('DISCORD_TOKEN')

    handler = logging.FileHandler(filename='discord_bot.log', encoding='utf-8', mode = 'w')
    logging.basicConfig(level=logging.DEBUG, handlers=[handler])

    discord_bot = DiscordBot(token)

