import nextcord
import os
import logging
import sys

from nextcord.ext import commands
from nextcord.ext import help_commands

from src import config

# --- Activity Setup ---

activity = nextcord.Activity(
    name="asu.p2w",
    type=nextcord.ActivityType.watching
)

# --- Setup ---
token = os.getenv("DISCORD_BOT_TOKEN")
logging.basicConfig(level=logging.ERROR)
intents = nextcord.Intents.default()
intents.message_content = True


bot = commands.Bot(
    command_prefix=config.PREFIX,
    intents=intents,
    help_command=help_commands.PaginatedHelpCommand(),
    strip_after_prefix=True,
    activity=activity
)

# --- Events ---
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


# --- Load Cogs ---
if __name__ == '__main__':
    for filename in os.listdir('src/cogs'):
        if filename.endswith('.py'):
            bot.load_extension(f'src.cogs.{filename[:-3]}')


bot.run(token)
