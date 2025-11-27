import music
import responses
import aichat
import discord
import social
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os

if __name__ == "__main__":
    load_dotenv()
    TOKEN = os.getenv('discord_token')

    intents = discord.Intents.default()
    intents.message_content = True
    client = commands.Bot(command_prefix="?", intents=intents)

    @client.event
    async def on_ready():
        try:
            synced = await client.tree.sync()
            print(f'I am online now! Synced {len(synced)} commands.')
        except Exception as e:
            print(f'Failed to sync commands: {e}')

    @client.tree.command(name="play", description="Toca uma faixa (suporta pesquisa ou links)")
    @app_commands.describe(song="O nome da música ou URL do SoundCloud para tocar")
    async def play(interaction: discord.Interaction, song: str):
        ctx = await commands.Context.from_interaction(interaction)
        await interaction.response.defer()
        await music.play(ctx, url=song)

    @client.tree.command(name="queue", description="Mostra a fila de músicas atual")
    async def queue(interaction: discord.Interaction):
        ctx = await commands.Context.from_interaction(interaction)
        await music.queue(ctx)

    @client.tree.command(name="skip", description="Pula a música atual")
    async def skip(interaction: discord.Interaction):
        ctx = await commands.Context.from_interaction(interaction)
        await music.skip(ctx)

    @client.tree.command(name="pause", description="Pausa a música atual")
    async def pause(interaction: discord.Interaction):
        ctx = await commands.Context.from_interaction(interaction)
        await music.pause(ctx)

    @client.tree.command(name="resume", description="Retoma a música pausada")
    async def resume(interaction: discord.Interaction):
        ctx = await commands.Context.from_interaction(interaction)
        await music.resume(ctx)

    @client.tree.command(name="stop", description="Para a reprodução de música")
    async def stop(interaction: discord.Interaction):
        ctx = await commands.Context.from_interaction(interaction)
        await music.stop(ctx)

    @client.tree.command(name="leave", description="Desconecte o bot do canal de voz")
    async def leave(interaction: discord.Interaction):
        ctx = await commands.Context.from_interaction(interaction)
        await music.leave(ctx)

    @client.tree.command(name="clear_queue", description="Limpa a fila de músicas")
    async def clear_queue(interaction: discord.Interaction):
        ctx = await commands.Context.from_interaction(interaction)
        await music.clear_queue(ctx)

    @client.tree.command(name="ask", description="Pergunte algo para a Bitinto-chan AI")
    @app_commands.describe(question="Sua pergunta para a AI")
    async def ask_command(interaction: discord.Interaction, question: str):
        ctx = await commands.Context.from_interaction(interaction)
        await interaction.response.defer()
        await aichat.ask(ctx, question)

    @client.tree.command(name="tinelli", description="Descubra mais sobre mim")
    async def sobre(interaction: discord.Interaction):
        view = social.TinelliLinksView()
        await interaction.response.send_message("Conheça mais sobre mim! Escolha uma das opções abaixo:", view=view)
    
    @client.tree.command(name="devs", description="Descubra mais sobre os desenvolvedores")
    async def devs(interaction: discord.Interaction):
        view = social.DevsLinksView()
        await interaction.response.send_message("Conheça mais sobre os desenvolvedores! Escolha uma das opções abaixo:", view=view)

    # ===== PREFIX COMMANDS (Others) =====
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
    
    client.run(TOKEN)