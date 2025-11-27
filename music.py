import discord
import asyncio
import yt_dlp

queues = {}
voice_clients = {}
soundcloud_base_url = 'https://soundcloud.com/'

yt_dl_options = {
    "format": "bestaudio/best",
    "http_headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    },
}

ytdl = yt_dlp.YoutubeDL(yt_dl_options)

ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn -filter:a "volume=0.3"'}

async def play_next(ctx):
    if queues[ctx.guild.id]:
        link = queues[ctx.guild.id][0] 
        await play(ctx, link=link, skip=True)  

async def play(ctx, *, url, skip=False):
    if ctx.author.voice is None:
        return await ctx.send(f"{ctx.author.mention} you need to be in a voice channel to play music!")

    if ctx.guild.id not in queues:
        queues[ctx.guild.id] = []

    if ctx.guild.id in voice_clients and voice_clients[ctx.guild.id].is_playing():
        final_url = url if soundcloud_base_url in url else f"scsearch:{url}"
        loop = asyncio.get_event_loop()
        video_info = await loop.run_in_executor(None, lambda: ytdl.extract_info(final_url, download=False))
        if 'entries' in video_info:
            video_info = video_info['entries'][0]
        video_title = video_info['title']
        queues[ctx.guild.id].append(video_title)
        return await ctx.reply(f"{video_title} added to queue!")
    else:
        try:
            voice_client = await ctx.author.voice.channel.connect()
            voice_clients[ctx.guild.id] = voice_client
        except:
            voice_client = voice_clients[ctx.guild.id]
        try:
            if soundcloud_base_url not in url:
                url = f"scsearch:{url}"

            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
            
            if 'entries' in data:
                data = data['entries'][0]
            
            song = data['url']
            player = discord.FFmpegOpusAudio(song, **ffmpeg_options)

            def after_playing(e):
                if queues[ctx.guild.id]:
                    next_url = queues[ctx.guild.id].pop(0)
                    asyncio.run_coroutine_threadsafe(play(ctx, url=next_url), loop)

            voice_client.play(player, after=after_playing)
            if skip:
                queues[ctx.guild.id].pop(0)
                return await ctx.reply(f'Playing: {data["title"]}!')
            return await ctx.reply(f'Playing: {data["title"]}!')
        except Exception as e:
            print(e)

async def queue(ctx):
    try:
        if ctx.guild.id in queues:
            if queues[ctx.guild.id] != []:
                queue_message = "```"
                for i, name in enumerate(queues[ctx.guild.id]):
                    queue_message += f"{i+1}. {name}\n"
                queue_message += "```"
                return await ctx.reply(queue_message)
            else:
                return await ctx.reply(f"There is no music in the queue!")
        else:
            return await ctx.reply(f"There is no music in the queue!")
    except Exception as e:
        print(e)

async def clear_queue(ctx):
    if ctx.guild.id in queues:
        queues[ctx.guild.id].clear()
        await ctx.reply(f"Queue cleared!")
    else:
        await ctx.reply(f"There is no music in the queue!")

async def pause(ctx):
    try:
        voice_clients[ctx.guild.id].pause()
        return await ctx.reply(f"Paused! Use /resume to continue playing.")
    except Exception as e:
        print(e)

async def resume(ctx):
    try:
        voice_clients[ctx.guild.id].resume()
        return await ctx.reply(f"Resumed!")
    except Exception as e:
        print(e)

async def stop(ctx):
    try:
        voice_clients[ctx.guild.id].stop()
        return await ctx.reply(f"Stopped!")
    except Exception as e:
        print(e)

async def skip(ctx):
    try:
        voice_clients[ctx.guild.id].stop()
        if queues[ctx.guild.id]:
            await play_next(ctx)
        else:
            await ctx.reply("No more songs in the queue!")
    except Exception as e:
        print(e)


async def leave(ctx):
    try:
        await voice_clients[ctx.guild.id].disconnect()
        del voice_clients[ctx.guild.id]
        return await ctx.reply(f"Left the voice channel!")
    except Exception as e:
        print(e)