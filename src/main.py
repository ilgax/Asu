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


@bot.event
async def on_application_command_error(interaction: nextcord.Interaction, error: Exception):
    """Global error handler for all application commands."""
    # Use the original error to get the correct type
    error = getattr(error, "original", error)
    error_type_name = type(error).__name__

    if isinstance(error, commands.CommandOnCooldown):
        await interaction.response.send_message(
            f"This command is on cooldown. Please try again in {error.retry_after:.2f} seconds.",
            ephemeral=True
        )
    elif isinstance(error, commands.MissingPermissions):
        await interaction.response.send_message(
            "You don't have the required permissions to run this command.",
            ephemeral=True
        )
    elif error_type_name in ("UserNotInVoiceChannel", "BotNotInVoiceChannel"):
        await interaction.response.send_message(str(error), ephemeral=True)

    elif isinstance(error, commands.CheckFailure):
        await interaction.response.send_message(
            "You do not meet the requirements to run this command.",
            ephemeral=True
        )
    else:
        print(f"Unhandled application command error: {error}")
        if not interaction.response.is_done():
            await interaction.response.send_message(
                "An unexpected error occurred while running this command.",
                ephemeral=True
            )
        else:
            await interaction.followup.send(
                "An unexpected error occurred while running this command.",
                ephemeral=True
            )


# --- Load Cogs ---
if __name__ == '__main__':
    for filename in os.listdir('src/cogs'):
        if filename.endswith('.py'):
            bot.load_extension(f'src.cogs.{filename[:-3]}')


bot.run(token)
