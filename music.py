import discord
import asyncio
import yt_dlp

queues = {}
voice_clients = {}
current_song = {}
soundcloud_base_url = 'https://soundcloud.com/'

yt_dl_options = {
    "format": "bestaudio/best",
    "noplaylist": False,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "logtostderr": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "auto",
    "source_address": "0.0.0.0",
    "http_headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    },
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -filter:a "volume=1.0"'
}


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.3):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
        self.webpage_url = data.get('webpage_url')

    @classmethod
    async def from_url(cls, url, *, loop=None):
        loop = loop or asyncio.get_event_loop()
        ytdl = yt_dlp.YoutubeDL(yt_dl_options)
        
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
        
        if data is None:
            raise Exception("Could not find any audio for this search")
        
        if 'entries' in data:
            data = data['entries'][0]
        
        audio_url = None
        
        if 'url' in data:
            audio_url = data['url']
        
        # Prioriza HTTP sobre HLS (mais compatível com SoundCloud)
        if 'formats' in data and data['formats']:
            for f in data['formats']:
                if f.get('protocol') in ('http', 'https'):
                    audio_url = f['url']
                    break
            
            if not audio_url:
                audio_url = data['formats'][0]['url']
        
        if not audio_url:
            raise Exception("No audio URL found")
        
        return cls(
            discord.FFmpegPCMAudio(audio_url, **ffmpeg_options),
            data=data
        )


async def play_next(ctx):
    guild_id = ctx.guild.id
    if guild_id in queues and queues[guild_id]:
        next_song = queues[guild_id].pop(0)
        await play(ctx, url=next_song['search'], skip=True)


async def play(ctx, *, url, skip=False):
    if ctx.author.voice is None:
        return await ctx.send(f"{ctx.author.mention} you need to be in a voice channel to play music!")

    guild_id = ctx.guild.id
    
    if guild_id not in queues:
        queues[guild_id] = []

    if guild_id in voice_clients and voice_clients[guild_id].is_playing() and not skip:
        search_url = url if soundcloud_base_url in url else f"scsearch:{url}"
        try:
            loop = asyncio.get_event_loop()
            ytdl = yt_dlp.YoutubeDL(yt_dl_options)
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(search_url, download=False))
            
            if 'entries' in data:
                data = data['entries'][0]
            
            queues[guild_id].append({
                'title': data.get('title', url),
                'search': search_url
            })
            return await ctx.reply(f"🎵 **{data.get('title', url)}** added to queue!")
        except Exception as e:
            print(f"Error adding to queue: {e}")
            return await ctx.reply("Error adding song to queue!")

    try:
        if guild_id not in voice_clients or voice_clients[guild_id] is None:
            voice_client = await ctx.author.voice.channel.connect()
            voice_clients[guild_id] = voice_client
        elif not voice_clients[guild_id].is_connected():
            voice_client = await ctx.author.voice.channel.connect()
            voice_clients[guild_id] = voice_client
        else:
            voice_client = voice_clients[guild_id]
    except discord.ClientException:
        voice_client = voice_clients[guild_id]
    except Exception as e:
        print(f"Error connecting to voice: {e}")
        return await ctx.reply("Error connecting to voice channel!")

    try:
        search_url = url if soundcloud_base_url in url else f"scsearch:{url}"
        
        loop = asyncio.get_event_loop()
        player = await YTDLSource.from_url(search_url, loop=loop)
        
        current_song[guild_id] = player.title

        def after_playing(error):
            if error:
                print(f"Player error: {error}")
            fut = asyncio.run_coroutine_threadsafe(play_next(ctx), loop)
            try:
                fut.result()
            except Exception as e:
                print(f"Error playing next: {e}")

        voice_client.play(player, after=after_playing)
        
        return await ctx.reply(f'🎶 Now playing: **{player.title}**')
        
    except Exception as e:
        print(f"Error playing: {e}")
        return await ctx.reply(f"Error playing song: {str(e)}")


async def queue(ctx):
    guild_id = ctx.guild.id
    try:
        if guild_id in queues and queues[guild_id]:
            queue_message = "**🎵 Music Queue:**\n```"
            for i, song in enumerate(queues[guild_id]):
                queue_message += f"{i+1}. {song['title']}\n"
            queue_message += "```"
            
            if guild_id in current_song:
                queue_message = f"**Now playing:** {current_song[guild_id]}\n\n" + queue_message
            
            return await ctx.reply(queue_message)
        else:
            msg = ""
            if guild_id in current_song and current_song[guild_id]:
                msg = f"**Now playing:** {current_song[guild_id]}\n\n"
            return await ctx.reply(msg + "The queue is empty!")
    except Exception as e:
        print(f"Error showing queue: {e}")
        return await ctx.reply("Error showing queue!")


async def clear_queue(ctx):
    guild_id = ctx.guild.id
    if guild_id in queues:
        queues[guild_id].clear()
        await ctx.reply("🗑️ Queue cleared!")
    else:
        await ctx.reply("The queue is already empty!")


async def pause(ctx):
    guild_id = ctx.guild.id
    try:
        if guild_id in voice_clients and voice_clients[guild_id].is_playing():
            voice_clients[guild_id].pause()
            return await ctx.reply("⏸️ Paused! Use /resume to continue playing.")
        else:
            return await ctx.reply("Nothing is playing!")
    except Exception as e:
        print(f"Error pausing: {e}")
        return await ctx.reply("Error pausing!")


async def resume(ctx):
    guild_id = ctx.guild.id
    try:
        if guild_id in voice_clients and voice_clients[guild_id].is_paused():
            voice_clients[guild_id].resume()
            return await ctx.reply("▶️ Resumed!")
        else:
            return await ctx.reply("Nothing is paused!")
    except Exception as e:
        print(f"Error resuming: {e}")
        return await ctx.reply("Error resuming!")


async def stop(ctx):
    guild_id = ctx.guild.id
    try:
        if guild_id in voice_clients:
            voice_clients[guild_id].stop()
            if guild_id in current_song:
                current_song[guild_id] = None
            return await ctx.reply("⏹️ Stopped!")
        else:
            return await ctx.reply("Nothing is playing!")
    except Exception as e:
        print(f"Error stopping: {e}")
        return await ctx.reply("Error stopping!")


async def skip(ctx):
    guild_id = ctx.guild.id
    try:
        if guild_id in voice_clients and voice_clients[guild_id].is_playing():
            voice_clients[guild_id].stop()  # stop() dispara after_playing() que toca a próxima
            return await ctx.reply("⏭️ Skipped!")
        else:
            return await ctx.reply("Nothing is playing!")
    except Exception as e:
        print(f"Error skipping: {e}")
        return await ctx.reply("Error skipping!")


async def leave(ctx):
    guild_id = ctx.guild.id
    try:
        if guild_id in voice_clients:
            await voice_clients[guild_id].disconnect()
            del voice_clients[guild_id]
            if guild_id in current_song:
                del current_song[guild_id]
            if guild_id in queues:
                queues[guild_id].clear()
            return await ctx.reply("👋 Left the voice channel!")
        else:
            return await ctx.reply("I'm not in a voice channel!")
    except Exception as e:
        print(f"Error leaving: {e}")
        return await ctx.reply("Error leaving voice channel!")