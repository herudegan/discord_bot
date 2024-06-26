import music
import responses
import aichat
import discord
from discord.ext import commands
from dotenv import load_dotenv
import music
import os


if __name__ == "__main__":
    load_dotenv()
    TOKEN = os.getenv('discord_token')

    intents = discord.Intents.default()
    intents.message_content = True
    client = commands.Bot(command_prefix="?", intents=intents)

    @client.event
    async def on_ready():
        print(f'I am online now!')

    @client.command(name="play")
    async def play(ctx, url):
        await music.play(ctx, url)

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
    
    @client.command(name="queue")
    async def queue(ctx, url):
        await music.queue(ctx, url)

    @client.command(name="skip")
    async def skip(ctx):
        await music.skip(ctx)

    @client.command(name="leave")
    async def leave(ctx):
        await music.leave(ctx)

    @client.command(name="s_char")
    async def s_char(ctx):
        await responses.s_char(ctx)

    @client.command(name="c_char")
    async def c_char(ctx):
        await responses.c_char(ctx)

    @client.command(name="d_char")
    async def d_char(ctx):
        await responses.d_char(ctx)

    @client.command(name="s_battle")
    async def s_battle(ctx):
        await responses.s_battle(ctx)

    @client.command(name="ask")
    async def ask_command(ctx, *, question):  
        await aichat.ask(ctx, question)

client.run(TOKEN)
    