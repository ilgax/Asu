import asyncio

import aiohttp
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

    @nextcord.slash_command(name="counter")
    async def counter(self, interaction: nextcord.Interaction):
        """Starts a counter for pressing."""
        await interaction.send("Press!", view=EphemeralCounter())

    @nextcord.slash_command(name="webhook", guild_ids=[config.GUILD_ID])
    async def webhook(self, interaction: nextcord.Interaction, url: str, content: str):
        """Sends a message to a webhook."""
        if not url.startswith("https://discord.com/api/webhooks/"):
            await interaction.send("Invalid webhook URL.", ephemeral=True)
            return
        if len(content) > 2000:
            await interaction.send("Message is too long.", ephemeral=True)
            return
        await interaction.send(f"Sending message {content!r} to webhook", ephemeral=True)
        await send_to_webhook(url, content)

    @nextcord.slash_command(guild_ids=[config.GUILD_ID])
    async def ask(self, interaction):
        """Asks the user a question to confirm something."""
        # We create the view and assign it to a variable so we can wait for it later.
        view = Confirm()
        await interaction.send("Do you want to continue?", view=view)
        # Wait for the View to stop listening for input...
        await view.wait()
        if view.value is None:
            print("Timed out...")
        elif view.value:
            print("Confirmed...")
        else:
            print("Cancelled...")


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

class Confirm(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @nextcord.ui.button(label="Confirm", style=nextcord.ButtonStyle.green)
    async def confirm(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_message("Confirming", ephemeral=True)
        self.value = True
        self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @nextcord.ui.button(label="Cancel", style=nextcord.ButtonStyle.grey)
    async def cancel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_message("Cancelling", ephemeral=True)
        self.value = False
        self.stop()

async def send_to_webhook(url, content):
    # Create a new HTTP session and use it to create webhook object
    async with aiohttp.ClientSession() as session:
        webhook = nextcord.Webhook.from_url(url, session=session)
        await webhook.send(content)


def setup(bot):
    bot.add_cog(GeneralCog(bot))