import discord
from discord.ext import commands
from datetime import date, time, datetime
import os
from dotenv import load_dotenv

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn'}

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all() # Enable all intents (members list, presence info etc.)
bot = commands.Bot(command_prefix='5gym', intents=intents.all()) # Initialize bot with all intents (permissions)

class ESR(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_client = None

    @commands.Cog.listener()
    async def on_ready(self):  # This is called when a connection to Discord is achieved
        today = date.today()  # Get what day it currently is. Needed because bot is meant to run for multiple days in 1 run.
        logmsg = f'{bot.user} has connected to Discord! ' + 'at ' + datetime.now().strftime(
            "%d-%m-%Y-%X") + '\n'  # Use a string that we log and print to the terminal
        logfile = open("logs-" + (today.strftime("%d-%m-%Y")) + ".txt",
                       "a+")  # Open today's logfile in append mode, create if it doesn't exist
        print(logmsg)  # Print our log message
        logfile.write(logmsg)  # Write the log message to the logfile
        logmsg = f'{bot.user} is connected to the following servers (guilds):\n'
        print(logmsg)
        logfile.write(logmsg)
        for guild in bot.guilds:  # For every server (guild) the bot is connected to, print and log the members in it
            logmsg = f'{guild.name} (ID: {guild.id})\n'
            print(logmsg)
            logfile.write(logmsg)
            members = '\n - '.join([member.name for member in guild.members])  # loop over all of a server's members
            logmsg = f'Members of the server:\n - {members}\n'
            print(logmsg)
            logfile.write(logmsg)
        logfile.close()

    @commands.command(name='esr', help="Connect to the ESR and stream audio")
    async def esr(self, ctx):
        guild = ctx.guild

        channel = discord.utils.get(guild.voice_channels, name='ESR')

        self.voice_client = discord.utils.get(self.bot.voice_clients, guild=guild)

        if self.voice_client is None:
            self.voice_client = await channel.connect()
        else:
            await self.voice_client.move_to(channel)

        url = 'http://europeanschoolradio.eu:1351/esradio.mp3'

        try:
            source = discord.FFmpegPCMAudio(url,
                                            **FFMPEG_OPTIONS)  # converts the youtube audio source into a source discord can use
            self.voice_client.play(source)  # play the source
            print("Now listening to European School Radio")
            await ctx.send("Now listening to European School Radio")

        except discord.ClientException as e:
            await ctx.send(f"A client exception occured:\n`{e}`")
            print(f"A client exception occured:\n`{e}`")
        except TypeError as e:
            await ctx.send(f"TypeError exception:\n`{e}`")
        except discord.opus.OpusNotLoaded as e:
            await ctx.send(f"OpusNotLoaded exception: \n`{e}`")

    @commands.command(name='dc', help="Disconnect from ESR")
    async def dc(self, ctx):
        await self.bot.voice_clients[0].disconnect()
        self.bot.voice_clients[0] = None

bot.add_cog(ESR(bot))
bot.run(token)