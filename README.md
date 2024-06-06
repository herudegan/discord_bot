# Discord Bot em Python

## Desenvolvedores:
- Lucas De Bitencourt Frasson
- Vitor Muneretto Tinelli
- Vinícius dos Santos Nascimento

## Descrição do Projeto:
Este projeto visa a criação de um bot para o Discord, desenvolvido em Python, com duas funcionalidades principais: tocar músicas do YouTube e proporcionar uma experiência de RPG simples para os usuários.

## Funcionalidades:
### 1. Reprodução de Músicas
O bot será capaz de reproduzir músicas diretamente do YouTube através de comandos específicos no chat do Discord.

### 2. Criação de Personagem
Os usuários poderão criar e personalizar seus personagens de RPG, incluindo atributos básicos como força, agilidade e inteligência.

### 3. Sistema de Combate
Implementação de um sistema de combate simples onde os personagens podem enfrentar monstros.

## Requisitos
- Python 3.8+
- Biblioteca `discord.py`
- Biblioteca `youtube_dl`
- Biblioteca `pytube`
- Outras dependências listadas em `requirements.txt`

## Como Executar
1. Clone o repositório:
    ```sh
    git clone https://github.com/seu-usuario/discord-bot.git
    ```
2. Navegue até o diretório do projeto:
    ```sh
    cd discord-bot
    ```
3. Instale as dependências:
    ```sh
    pip install -r requirements.txt
    ```
4. Configure o arquivo `.env` com o token do seu bot:
    ```sh
    BOT_TOKEN=seu_token_aqui
    ```
5. Execute o bot:
    ```sh
    python bot.py
    ```

## Comandos Disponíveis
### Comandos de Música
- `!play <url>`: Reproduz a música do YouTube a partir da URL fornecida.
- `!pause`: Pausa a reprodução da música.
- `!resume`: Retoma a reprodução da música.
- `!stop`: Para a reprodução da música e limpa a fila.

### Comandos de RPG
- `!createcharacter <nome>`: Cria um novo personagem com o nome fornecido.
- `!status`: Mostra os atributos do personagem.
- `!fight <monstro>`: Inicia uma batalha contra um monstro.

## Contribuições
1. Faça um fork do projeto.
2. Crie uma branch para sua feature:
    ```sh
    git checkout -b minha-nova-feature
    ```
3. Commit suas mudanças:
    ```sh
    git commit -m 'Adiciona minha nova feature'
    ```
4. Faça o push para a branch:
    ```sh
    git push origin minha-nova-feature
    ```
5. Abra um Pull Request.

## Licença
Este projeto está licenciado sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## Agradecimentos
Agradecemos a todos que contribuíram direta ou diretamente para este projeto.

