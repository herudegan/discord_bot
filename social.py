
import discord

class TinelliLinksView(discord.ui.View):
    @discord.ui.button(label="YouTube", style=discord.ButtonStyle.primary)
    async def youtubeButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Aqui está o link do meu canal no YouTube: [YouTube](https://www.youtube.com/@TinelliPlay)", ephemeral=True)

    @discord.ui.button(label="Servidor Discord", style=discord.ButtonStyle.primary)
    async def discordButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Aqui está o link do servidor do Discord do canal: [Discord](https://discord.gg/5Fqj64HFDV)", ephemeral=True)
    
    @discord.ui.button(label="Instagram", style=discord.ButtonStyle.primary)
    async def instaButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Aqui está o link do meu Instagram: [Instagram](https://www.instagram.com/vitortinelli)", ephemeral=True)
    
    @discord.ui.button(label="Github", style=discord.ButtonStyle.secondary)
    async def vitorGitHubButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Aqui está o link do meu GitHub: [GitHub](https://github.com/vitortinelli)", ephemeral=True)

class DevsLinksView(discord.ui.View):
    @discord.ui.button(label="Lucas Frasson", style=discord.ButtonStyle.primary)
    async def lucasGitHubButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Aqui está o link do meu GitHub: [GitHub](https://github.com/herudegan)", ephemeral=True)
    @discord.ui.button(label="Vinicius D.S.N", style=discord.ButtonStyle.primary)
    async def viniGitHubButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Aqui está o link do meu GitHub: [GitHub](https://github.com/ViniciusDSN)", ephemeral=True)
    @discord.ui.button(label="Vitor Tinelli", style=discord.ButtonStyle.primary)
    async def vitorGitHubButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Conheça mais sobre mim! Escolha uma das opções abaixo:", view=TinelliLinksView())


    