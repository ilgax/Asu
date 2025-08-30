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

    @nextcord.slash_command(name="avatar", description="Displays the avatar of a user.")
    async def avatar_slash(self, interaction: nextcord.Interaction, member: nextcord.Member = None):
        if member is None:
            member = interaction.user
        await interaction.response.send_message(member.avatar.url)

    @nextcord.slash_command(name="coinflip", description="Flip a coin.")
    async def coinflip_slash(self, interaction: nextcord.Interaction):
        result = random.choice(["Heads", "Tails"])
        await interaction.response.send_message(result)

    @nextcord.slash_command(name="counter", guild_ids=[config.GUILD_ID])
    async def counter(self, interaction: nextcord.Interaction):
        """Starts a counter for pressing."""
        await interaction.send("Press!", view=EphemeralCounter())


class Counter(nextcord.ui.View):
    # Define the actual button
    # When pressed, this increments the number displayed until it hits 5.
    # When it hits 5, the counter button is disabled and it turns green.
    # note: The name of the function does not matter to the library
    @nextcord.ui.button(label="0", style=nextcord.ButtonStyle.red)
    async def count(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        number = int(button.label) if button.label else 0
        if number >= 4:
            button.style = nextcord.ButtonStyle.green
            button.disabled = True
        button.label = str(number + 1)

        # Make sure to update the message with our updated selves
        await interaction.response.edit_message(view=self)


# Define a View that will give us our own personal counter button
class EphemeralCounter(nextcord.ui.View):
    # When this button is pressed, it will respond with a Counter view that will
    # give the button presser their own personal button they can press 5 times.
    @nextcord.ui.button(label="Click", style=nextcord.ButtonStyle.blurple)
    async def receive(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        # ephemeral=True makes the message hidden from everyone except the button presser
        await interaction.response.send_message("Enjoy!", view=Counter(), ephemeral=True)


def setup(bot):
    bot.add_cog(GeneralCog(bot))