import asyncio
import nextcord
from nextcord.ext import commands
from nextcord import Interaction
import yt_dlp as youtube_dl
from src import config

# --- Custom Exceptions for Music Cog ---
class UserNotInVoiceChannel(commands.CheckFailure):
    """Exception raised when a user is not in a voice channel."""
    pass

class BotNotInVoiceChannel(commands.CheckFailure):
    """Exception raised when the bot is not in a voice channel."""
    pass

# --- Music Cog --- 

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ""

ytdl_format_options = {
    "format": "bestaudio/best",
    "restrictfilenames": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "logtostderr": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "ytsearch",
    "source_address": "0.0.0.0",  # bind to ipv4
}

ffmpeg_options = {
    "options": "-vn",
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- Join VC ---
    @nextcord.slash_command(name="join", description="Join a voice channel", guild_ids=[config.GUILD_ID])
    async def join(self, interaction: Interaction):
        if not interaction.user.voice:
            raise UserNotInVoiceChannel("You must be in a voice channel to use this command.")

        channel = interaction.user.voice.channel
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.move_to(channel)
        else:
            await channel.connect()
        await interaction.response.send_message(f"✅ Joined {channel}")

    # --- Play from YouTube (Stream) ---
    @nextcord.slash_command(description="Play a song from YouTube by URL or title", guild_ids=[config.GUILD_ID])
    async def play(self, interaction: Interaction, query: str):
        if not interaction.user.voice:
            raise UserNotInVoiceChannel("You must be in a voice channel to use this command.")

        channel = interaction.user.voice.channel
        voice_client = interaction.guild.voice_client

        if voice_client is None:
            voice_client = await channel.connect()
        elif voice_client.channel != channel:
            await voice_client.move_to(channel)

        await interaction.response.defer()

        try:
            loop = self.bot.loop or asyncio.get_event_loop()
            data = await loop.run_in_executor(
                None, lambda: ytdl.extract_info(query, download=False)
            )

            if "entries" not in data or not data["entries"]:
                return await interaction.followup.send("❌ Could not find any results.")

            song_data = data["entries"][0]
            filename = song_data["url"]
            title = song_data.get("title", "Unknown title")

            # Create the audio source with volume control
            audio_source = nextcord.PCMVolumeTransformer(
                nextcord.FFmpegPCMAudio(filename, **ffmpeg_options)
            )

            def after_playing(error):
                if error:
                    print(f'Player error: {error}')

            voice_client.play(audio_source, after=after_playing)

            await interaction.followup.send(f"🎶 Now playing: **{title}**")

        except Exception as e:
            await interaction.followup.send(f"❌ Could not play song. Error: {e}", ephemeral=True)

    # --- Volume ---
    @nextcord.slash_command(description="Change the volume (0-100)")
    async def volume(self, interaction: Interaction, vol: int):
        if not interaction.guild.voice_client:
            raise BotNotInVoiceChannel("I'm not connected to a voice channel.")

        vc = interaction.guild.voice_client
        if not vc.source:
            return await interaction.response.send_message("I am not playing anything right now.", ephemeral=True)

        # Clamp volume between 0 and 100
        vol = max(0, min(100, vol))
        vc.source.volume = vol / 100
        await interaction.response.send_message(f"🔊 Volume set to {vol}%")

    # --- Stop ---
    @nextcord.slash_command(description="Stop and disconnect the bot")
    async def stop(self, interaction: Interaction):
        if not interaction.guild.voice_client:
            raise BotNotInVoiceChannel("I'm not connected to a voice channel.")

        vc = interaction.guild.voice_client
        if vc.is_playing():
            vc.stop()
        await vc.disconnect()
        await interaction.response.send_message("🛑 Stopped and disconnected.")


def setup(bot):
    bot.add_cog(Music(bot))