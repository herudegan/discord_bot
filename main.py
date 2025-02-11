import music
import responses
import aichat
import discord
import social
import asyncio
from aiohttp import web
from discord.ext import commands
from dotenv import load_dotenv
import os

if __name__ == "__main__":
    load_dotenv()
    TOKEN = os.getenv('discord_token')

    intents = discord.Intents.default()
    intents.message_content = True
    client = commands.Bot(command_prefix="/", intents=intents)

    @client.event
    async def on_ready():
        await client.tree.sync()
        print(f'I am online now!')

    @client.command(name="play")
    async def play(ctx, *, url):
        await music.play(ctx, url=url)

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
    async def queue(ctx):
        await music.queue(ctx)

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

    @client.command(name="tinelli")
    async def sobre(ctx):
        view = social.TinelliLinksView()
        await ctx.send("Conheça mais sobre mim! Escolha uma das opções abaixo:", view=view)
    
    @client.command(name="desenvolvedores")
    async def devs(ctx):
        view = social.DevsLinksView()
        await ctx.send("Conheça mais sobre os desenvolvedores! Escolha uma das opções abaixo:", view=view)
    
    async def health_check(request):
        return web.Response(text="Bot is healthy and running on port 8080")

    app = web.Application()
    app.router.add_get('/health', health_check)

    async def main():
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host='0.0.0.0', port=8080)
        await site.start()
        print("Web server running on http://0.0.0.0:8080")

        await client.start(TOKEN)

    asyncio.run(main())