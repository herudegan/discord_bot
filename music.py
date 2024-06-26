import discord
from discord.ext import commands
import os
import asyncio
import yt_dlp
from dotenv import load_dotenv
import urllib.parse, urllib.request, re

queues = {}
voice_clients = {}
youtube_base_url = 'https://www.youtube.com/'
youtube_results_url = youtube_base_url + 'results?'
youtube_watch_url = youtube_base_url + 'watch?v='
yt_dl_options = {"format": "bestaudio/best"}
ytdl = yt_dlp.YoutubeDL(yt_dl_options)

ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn -filter:a "volume=0.3"'}

async def play_next(ctx):
    if queues[ctx.guild.id] != []:
        link = queues[ctx.guild.id].pop(0)
        await play(ctx, link=link)

async def play(ctx, link):
    try:
        if ctx.author.voice is None:
            return await ctx.send(f"{ctx.author.mention} you need to be in a voice channel to play music!")
        voice_client = await ctx.author.voice.channel.connect()
        voice_clients[voice_client.guild.id] = voice_client
    except Exception as e:
        print(e)

    try:
        if youtube_base_url not in link:
            query_string = urllib.parse.urlencode({
                'search_query': link
            })

            content = urllib.request.urlopen(
                youtube_results_url + query_string
            )

            search_results = re.findall(r'/watch\?v=(.{11})', content.read().decode())

            link = youtube_watch_url + search_results[0]

        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(link, download=False))

        song = data['url']
        player = discord.FFmpegOpusAudio(song, **ffmpeg_options)

        voice_clients[ctx.guild.id].play(player, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), client.loop))
        return await ctx.send(f'Playing: {data["title"]} asked by {ctx.author.mention}!')
    except Exception as e:
        print(e)

async def clear_queue(ctx):
    if ctx.guild.id in queues:
        queues[ctx.guild.id].clear()
        await ctx.send(f"Queue cleared by {ctx.author.mention}!")
    else:
        await ctx.send(f"There is no music in the queue, {ctx.author.mention}!")

async def pause(ctx):
    try:
        voice_clients[ctx.guild.id].pause()
        return await ctx.send(f"Paused by {ctx.author.mention}! Use ?resume to continue playing.")
    except Exception as e:
        print(e)

async def resume(ctx):
    try:
        voice_clients[ctx.guild.id].resume()
        return await ctx.send(f"Resumed by {ctx.author.mention}!")
    except Exception as e:
        print(e)

async def stop(ctx):
    try:
        voice_clients[ctx.guild.id].stop()
        return await ctx.send(f"Stopped by {ctx.author.mention}!")
    except Exception as e:
        print(e)

async def queue(ctx, *, url):
    if ctx.guild.id not in queues:
        queues[ctx.guild.id] = []
    queues[ctx.guild.id].append(url)
    await ctx.send(f"{ctx.author.mention} added to queue: {url}!")

async def skip(ctx):
    try:
        voice_clients[ctx.guild.id].stop()
        await play_next(ctx)
        return await ctx.send(f"Skipped by {ctx.author.mention}!")
    except Exception as e:
        print(e)

async def leave(ctx):
    try:
        await voice_clients[ctx.guild.id].disconnect()
        del voice_clients[ctx.guild.id]
        return await ctx.send(f"{ctx.author.mention} asked me to leave the voice channel!")
    except Exception as e:
        print(e)