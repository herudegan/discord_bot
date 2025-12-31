import music
import rpg
import aichat
import discord
import social
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os
import asyncio
import json
import sqlite3
from aiohttp import web

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

    @client.tree.command(name="criar_historia", description="Crie sua própria história de RPG")
    @app_commands.describe(
        titulo="O título da sua história",
        conteudo="O conteúdo/texto da sua história"
    )
    async def criar_historia(interaction: discord.Interaction, titulo: str, conteudo: str):
        await rpg.criar_historia(interaction, titulo, conteudo)
    
    @client.tree.command(name="ler_historia", description="Leia a história de um membro do servidor")
    @app_commands.describe(
        usuario="O usuário cuja história você quer ler (deixe vazio para ler a sua)"
    )
    async def ler_historia(interaction: discord.Interaction, usuario: discord.Member = None):
        await rpg.ler_historia(interaction, usuario)
    
    @client.tree.command(name="editar_historia", description="Edite sua história de RPG")
    @app_commands.describe(
        novo_titulo="O novo título da sua história (opcional)",
        novo_conteudo="O novo conteúdo da sua história (opcional)"
    )
    async def editar_historia(interaction: discord.Interaction, novo_titulo: str = None, novo_conteudo: str = None):
        await rpg.editar_historia(interaction, novo_titulo, novo_conteudo)
    
    @client.tree.command(name="excluir_historia", description="Exclua sua história de RPG")
    async def excluir_historia(interaction: discord.Interaction):
        await rpg.excluir_historia(interaction)

    async def health_check(request):
        """Endpoint de health check para manter o bot ativo no Render"""
        return web.Response(text="Bot is alive!", status=200)

    async def export_db_json(request):
        """Exporta todos os dados do rpg.db em formato JSON"""
        auth = request.headers.get('Authorization', '')
        secret = os.getenv('EXPORT_SECRET', 'meu_secret_temporario')
        if auth != f'Bearer {secret}':
            return web.Response(text="Unauthorized", status=401)
        
        try:
            conn = sqlite3.connect('rpg.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM stories")
            rows = cursor.fetchall()
            
            data = {
                "stories": [dict(row) for row in rows],
                "exported_at": str(asyncio.get_event_loop().time())
            }
            conn.close()
            
            return web.Response(
                text=json.dumps(data, indent=2, ensure_ascii=False, default=str),
                content_type='application/json'
            )
        except Exception as e:
            return web.Response(text=f"Error: {str(e)}", status=500)

    async def download_db(request):
        """Permite download direto do arquivo rpg.db"""
        auth = request.headers.get('Authorization', '')
        secret = os.getenv('EXPORT_SECRET', 'meu_secret_temporario')
        if auth != f'Bearer {secret}':
            return web.Response(text="Unauthorized", status=401)
        
        try:
            if os.path.exists('rpg.db'):
                with open('rpg.db', 'rb') as f:
                    content = f.read()
                return web.Response(
                    body=content,
                    content_type='application/octet-stream',
                    headers={'Content-Disposition': 'attachment; filename="rpg.db"'}
                )
            else:
                return web.Response(text="Database not found", status=404)
        except Exception as e:
            return web.Response(text=f"Error: {str(e)}", status=500)

    async def start_web_server():
        """Inicia servidor HTTP na porta definida pelo Render"""
        app = web.Application()
        app.router.add_get('/', health_check)
        app.router.add_get('/health', health_check)
        app.router.add_get('/export-json', export_db_json)
        app.router.add_get('/download-db', download_db)
        
        port = int(os.getenv('PORT', 8080))
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', port)
        await site.start()
        print(f'Health check server running on port {port}')
    
    async def main():
        await start_web_server()
        
        max_retries = 5
        for attempt in range(max_retries):
            try:
                await client.start(TOKEN)
                break
            except discord.errors.HTTPException as e:
                if e.status == 429:
                    wait_time = (attempt + 1) * 30  # 30s, 60s, 90s, etc.
                    print(f"Rate limited! Aguardando {wait_time}s antes de tentar novamente... (tentativa {attempt + 1}/{max_retries})")
                    await asyncio.sleep(wait_time)
                else:
                    raise
            except Exception as e:
                print(f"Erro ao conectar: {e}")
                raise
    
    asyncio.run(main())