import sqlite3
import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime


def init_database():
    """Inicializa o banco de dados e cria a tabela de histórias se não existir."""
    conn = sqlite3.connect('rpg.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            username TEXT NOT NULL,
            titulo TEXT NOT NULL,
            conteudo TEXT NOT NULL,
            data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
            data_modificacao DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


# Inicializa o banco ao importar o módulo
init_database()


class ConfirmarExclusao(discord.ui.View):
    """View com botões de confirmação para excluir história."""
    
    def __init__(self, user_id: int):
        super().__init__(timeout=30)
        self.user_id = user_id
        self.confirmed = None
    
    @discord.ui.button(label="Confirmar", style=discord.ButtonStyle.danger, emoji="🗑️")
    async def confirmar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Apenas o autor pode confirmar!", ephemeral=True)
            return
        self.confirmed = True
        self.stop()
        await interaction.response.defer()
    
    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.secondary, emoji="❌")
    async def cancelar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Apenas o autor pode cancelar!", ephemeral=True)
            return
        self.confirmed = False
        self.stop()
        await interaction.response.defer()


async def criar_historia(interaction: discord.Interaction, titulo: str, conteudo: str):
    """Cria uma nova história para o usuário."""
    try:
        conn = sqlite3.connect('rpg.db')
        cursor = conn.cursor()
        
        # Verifica se o usuário já tem uma história
        cursor.execute("SELECT id FROM stories WHERE user_id = ?", (interaction.user.id,))
        existing = cursor.fetchone()
        
        if existing:
            conn.close()
            embed = discord.Embed(
                title="❌ Erro",
                description="Você já possui uma história! Use `/editar_historia` para modificá-la ou `/excluir_historia` para deletá-la.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Insere a nova história
        cursor.execute("""
            INSERT INTO stories (user_id, username, titulo, conteudo)
            VALUES (?, ?, ?, ?)
        """, (interaction.user.id, interaction.user.name, titulo, conteudo))
        conn.commit()
        conn.close()
        
        embed = discord.Embed(
            title="✅ História Criada!",
            description=f"**{titulo}**\n\nSua história foi salva com sucesso!",
            color=discord.Color.green()
        )
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text=f"Use /ler_historia para visualizá-la")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    except Exception as e:
        embed = discord.Embed(
            title="❌ Erro",
            description=f"Ocorreu um erro ao criar a história: {str(e)}",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def ler_historia(interaction: discord.Interaction, usuario: discord.Member = None):
    """Lê a história de um usuário."""
    target_user = usuario or interaction.user
    
    try:
        conn = sqlite3.connect('rpg.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT titulo, conteudo, username, data_criacao, data_modificacao
            FROM stories WHERE user_id = ?
        """, (target_user.id,))
        story = cursor.fetchone()
        conn.close()
        
        if not story:
            embed = discord.Embed(
                title="📖 História não encontrada",
                description=f"**{target_user.display_name}** ainda não criou uma história.",
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        titulo, conteudo, username, data_criacao, data_modificacao = story
        
        embed = discord.Embed(
            title=f"📜 {titulo}",
            description=conteudo,
            color=discord.Color.blue()
        )
        embed.set_author(name=f"Autor: {target_user.display_name}", icon_url=target_user.display_avatar.url)
        embed.add_field(name="📅 Criada em", value=data_criacao[:10] if data_criacao else "N/A", inline=True)
        embed.add_field(name="✏️ Modificada em", value=data_modificacao[:10] if data_modificacao else "N/A", inline=True)
        embed.set_footer(text=f"História de {username}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    except Exception as e:
        embed = discord.Embed(
            title="❌ Erro",
            description=f"Ocorreu um erro ao ler a história: {str(e)}",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def editar_historia(interaction: discord.Interaction, novo_titulo: str = None, novo_conteudo: str = None):
    """Edita a história do usuário."""
    if not novo_titulo and not novo_conteudo:
        embed = discord.Embed(
            title="❌ Erro",
            description="Você precisa fornecer pelo menos um novo título ou novo conteúdo!",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    try:
        conn = sqlite3.connect('rpg.db')
        cursor = conn.cursor()
        
        # Verifica se o usuário tem uma história
        cursor.execute("SELECT titulo, conteudo FROM stories WHERE user_id = ?", (interaction.user.id,))
        existing = cursor.fetchone()
        
        if not existing:
            conn.close()
            embed = discord.Embed(
                title="❌ Erro",
                description="Você ainda não possui uma história! Use `/criar_historia` primeiro.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Atualiza os campos fornecidos
        titulo_final = novo_titulo if novo_titulo else existing[0]
        conteudo_final = novo_conteudo if novo_conteudo else existing[1]
        
        cursor.execute("""
            UPDATE stories 
            SET titulo = ?, conteudo = ?, data_modificacao = ?
            WHERE user_id = ?
        """, (titulo_final, conteudo_final, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), interaction.user.id))
        conn.commit()
        conn.close()
        
        embed = discord.Embed(
            title="✅ História Editada!",
            description=f"**{titulo_final}**\n\nSua história foi atualizada com sucesso!",
            color=discord.Color.green()
        )
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        
        changes = []
        if novo_titulo:
            changes.append("📝 Título atualizado")
        if novo_conteudo:
            changes.append("📖 Conteúdo atualizado")
        embed.add_field(name="Alterações", value="\n".join(changes), inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    except Exception as e:
        embed = discord.Embed(
            title="❌ Erro",
            description=f"Ocorreu um erro ao editar a história: {str(e)}",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def excluir_historia(interaction: discord.Interaction):
    """Exclui a história do usuário após confirmação."""
    try:
        conn = sqlite3.connect('rpg.db')
        cursor = conn.cursor()
        
        # Verifica se o usuário tem uma história
        cursor.execute("SELECT titulo FROM stories WHERE user_id = ?", (interaction.user.id,))
        existing = cursor.fetchone()
        
        if not existing:
            conn.close()
            embed = discord.Embed(
                title="❌ Erro",
                description="Você não possui uma história para excluir!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        conn.close()
        
        # Pede confirmação
        embed = discord.Embed(
            title="⚠️ Confirmar Exclusão",
            description=f"Você tem certeza que deseja excluir sua história **\"{existing[0]}\"**?\n\n**Esta ação não pode ser desfeita!**",
            color=discord.Color.orange()
        )
        
        view = ConfirmarExclusao(interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        
        # Aguarda a resposta
        await view.wait()
        
        if view.confirmed is None:
            embed = discord.Embed(
                title="⏰ Tempo Esgotado",
                description="A operação foi cancelada por tempo limite.",
                color=discord.Color.grey()
            )
            await interaction.edit_original_response(embed=embed, view=None)
            return
        
        if view.confirmed:
            conn = sqlite3.connect('rpg.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM stories WHERE user_id = ?", (interaction.user.id,))
            conn.commit()
            conn.close()
            
            embed = discord.Embed(
                title="🗑️ História Excluída",
                description="Sua história foi excluída com sucesso!",
                color=discord.Color.green()
            )
            await interaction.edit_original_response(embed=embed, view=None)
        else:
            embed = discord.Embed(
                title="❌ Cancelado",
                description="A exclusão foi cancelada.",
                color=discord.Color.grey()
            )
            await interaction.edit_original_response(embed=embed, view=None)
        
    except Exception as e:
        embed = discord.Embed(
            title="❌ Erro",
            description=f"Ocorreu um erro ao excluir a história: {str(e)}",
            color=discord.Color.red()
        )
        if not interaction.response.is_done():
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.edit_original_response(embed=embed, view=None)