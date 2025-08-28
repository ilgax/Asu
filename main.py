import nextcord
from nextcord.ext import commands
import os

# --- Setup ---
intents = nextcord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# --- Events ---
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# --- Prefix Command Example ---
@bot.command()
async def ping(ctx):
    """Responds with Pong! (prefix command)"""
    await ctx.send("🏓 Pong! (prefix command)")

# --- Slash Command Example ---
@bot.slash_command(name="ping", description="Responds with Pong!", guild_ids=[1347581861622452314])
async def ping_slash(interaction: nextcord.Interaction):
    await interaction.response.send_message("🏓 Pong! (slash command)")

# --- Run Bot ---
token = os.getenv("DISCORD_BOT_TOKEN")
bot.run(token)
