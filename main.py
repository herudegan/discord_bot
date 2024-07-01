import music
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

if __name__ == "__main__":
    load_dotenv()
    TOKEN = os.getenv('discord_token')

    intents = discord.Intents.default()
    intents.message_content = True
    client = commands.Bot(command_prefix="?", intents=intents)

    @client.command(name="play")
    async def play(ctx, *, url):
        await music.play(ctx, url=url)

    @client.command(name="queue")
    async def queue(ctx):
        await music.queue(ctx)    

    @client.command(name="c_queue")
    async def clear_queue(ctx):
        await music.clear_queue(ctx)

    @client.command(name="pause")
    async def pause(ctx):
        await music.pause(ctx)

    @client.command(name="resume")
    async def resume(ctx):
        await music.resume(ctx)

    @client.command(name="stop")
    async def stop(ctx):
        await music.stop(ctx)

    @client.command(name="skip")
    async def skip(ctx):
        await music.skip(ctx)

    @client.command(name="leave")
    async def leave(ctx):
        await music.leave(ctx)

client.run(TOKEN)
    