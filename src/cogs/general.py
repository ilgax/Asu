import nextcord
import random
from nextcord.ext import commands

from src import config


class GeneralCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send("🏓 Pong! (prefix command)")

    @nextcord.slash_command(name="ping", description="Responds with Pong!")
    async def ping_slash(self, interaction: nextcord.Interaction):
        await interaction.response.send_message("🏓 Pong! (slash command)")

    @nextcord.slash_command(name="test", description="Test command")
    async def test_slash(self, interaction: nextcord.Interaction):
        await interaction.response.send_message("Test command")

    @nextcord.slash_command(name="roll", description="Test command")
    async def roll(self, interaction: nextcord.Interaction, limit: int, times: int):
        if limit < 1:
            await interaction.response.send_message("Limit has to be greater than 0!")
        elif times < 1:
            await interaction.response.send_message("Times has to be greater than 0!")

        try:
            result = ", ".join(str(random.randint(1, limit)) for _ in range(times))
        except Exception:
            await interaction.response.send_message("An error occurred")
            return

        await interaction.response.send_message(result)

    @commands.command(name="avatar", description="Displays the avatar of a user.")
    async def avatar(self, ctx, member: nextcord.Member = None):
        if member is None:
            member = ctx.author
        await ctx.send(member.avatar.url)

def setup(bot):
    bot.add_cog(GeneralCog(bot))