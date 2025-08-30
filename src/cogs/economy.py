import nextcord
import random
import sqlite3
from nextcord.ext import commands
from src import config

# --- Economy Cog ---

class EconomyCog(commands.Cog, name="Economy"):
    """Handles the basic economy system."""
    def __init__(self, bot):
        self.bot = bot
        self.db_path = 'economy.db'
        self.setup_database()

    def get_connection(self):
        """Gets a new database connection."""
        return sqlite3.connect(self.db_path)

    def setup_database(self):
        """Sets up the initial database and table."""
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                balance INTEGER NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    async def get_balance(self, user_id: int) -> int | None:
        """Gets the balance of a user. Returns None if user not found."""
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        result = c.fetchone()
        conn.close()
        return result[0] if result else None

    async def update_balance(self, user_id: int, change: int):
        """Updates a user's balance by a certain amount (can be negative)."""
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (change, user_id))
        conn.commit()
        conn.close()

    @nextcord.slash_command(name="register", description="Create an account in the economy system.")
    async def register(self, interaction: nextcord.Interaction):
        user_id = interaction.user.id
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        if c.fetchone():
            await interaction.response.send_message("You already have an account.", ephemeral=True)
        else:
            c.execute("INSERT INTO users (user_id, balance) VALUES (?, ?)", (user_id, 100))
            conn.commit()
            await interaction.response.send_message("Your account has been created with a starting balance of 100.", ephemeral=True)
        conn.close()

    @nextcord.slash_command(name="balance", description="Check your account balance.")
    async def balance(self, interaction: nextcord.Interaction, user: nextcord.Member = None):
        target_user = user or interaction.user
        balance = await self.get_balance(target_user.id)
        if balance is not None:
            await interaction.response.send_message(f"{target_user.display_name} has a balance of {balance}.")
        else:
            await interaction.response.send_message(f"{target_user.display_name} does not have an account. Use /register to create one.", ephemeral=True)

    @nextcord.slash_command(name="baladd", description="Add money to a user's account.", guild_ids=[config.GUILD_ID])
    async def baladd(self, interaction: nextcord.Interaction, user: nextcord.Member, amount: int):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        else:
            target_user = user or interaction.user
            await self.update_balance(target_user.id, amount)
            await interaction.response.send_message(f"Added {amount} to {target_user.display_name}'s balance.")

# --- Gambling Cog ---

class Gambling(commands.Cog, name="Gambling"):
    """Commands for gambling."""
    def __init__(self, bot):
        self.bot = bot

    def coinflip(self):
        return random.randint(0, 1) == 1 # Return True for win, False for loss

    @nextcord.slash_command(name="gamble", description="Gamble your money on a coinflip (2x payout).")
    async def gamble_slash(self, interaction: nextcord.Interaction, amount: int):
        if amount <= 0:
            await interaction.response.send_message("You must gamble a positive amount.", ephemeral=True)
            return

        economy = self.bot.get_cog('Economy')
        if not economy:
            await interaction.response.send_message("The economy system is currently disabled.", ephemeral=True)
            return

        user_id = interaction.user.id
        balance = await economy.get_balance(user_id)

        if balance is None:
            await interaction.response.send_message("You don't have an account. Use /register first.", ephemeral=True)
            return

        if balance < amount:
            await interaction.response.send_message("You don't have enough money to gamble that amount.", ephemeral=True)
            return

        # Perform the gamble
        if self.coinflip():
            # Win
            winnings = int(amount * 1)
            await economy.update_balance(user_id, winnings)
            new_balance = balance + winnings
            await interaction.response.send_message(f"You won! You gained {winnings}. Your new balance is {new_balance}.")
        else:
            # Loss
            await economy.update_balance(user_id, -amount)
            new_balance = balance - amount
            await interaction.response.send_message(f"You lost! You lost {amount}. Your new balance is {new_balance}.")

# --- Setup Function ---

def setup(bot):
    """Adds the cogs to the bot."""
    bot.add_cog(EconomyCog(bot))
    bot.add_cog(Gambling(bot))