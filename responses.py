import sqlite3
import random
import asyncio
import discord
    
def s_char(ctx):
  data = search_chars(ctx=ctx)
  text = []
  for i in data:
    text.append("```\n Nome: {}\n Idade: {}\n Raça: {}\n HP: {}```".format(str(i[1]), str(i[2]), str(i[3]), str(i[4])))
  return ctx.send(''.join(text))
  
def c_char(ctx):
  char = ""
  string: str = ctx.message.content
  if ";" in string[8:]: 
    char = string[8:].replace(" ", "").split(';')
  else:
     return ctx.send("Por favor, digite o seu personagem da seguinte maneira: ?c_char Nome; Idade; Raça;")
  if len(char) == 3:
    if char[0] and char[1] and char[2]:
      name = char[0]
      age = char[1]
      race = char[2]
      conn = sqlite3.connect('rpg.db')
      cursor = conn.cursor()

      # Searching in the database to see if the user already exists
      cursor.execute(f"""
        select * from users where username = '{ctx.author.name}';
      """)
      user = cursor.fetchone()
      if not user:
        cursor.execute(f"""
          insert into users(username) values('{ctx.author.name}');
        """)
        conn.commit()
        conn.close()

      # Searching in the database to see if this user already has such a character
      if search_chars(name=name, ctx=ctx):
        conn.close()
        return ctx.send("Você já possui um personagem com esse nome!")
      
      # Searching in the database to see if this user already has 3 characters
      chars = search_chars(ctx=ctx)
      if len(chars) >= 3:
        conn.close()
        return ctx.send("Você já possui 3 personagens!")
      
      try:
        cursor.execute("""
          insert into chars(name, age, race, health_points, attack_power, id_user)
          values (?, ?, ?, 20, 5, ?)
        """, (name, age, race, user[0]))
        conn.commit()
        conn.close()
        return ctx.send("Personagem criado com sucesso!")
      except Exception as e:
        print(f"Error: {e}")
  else:
    return ctx.send("Por favor, digite o seu personagem da seguinte maneira: ?c_char Nome; Idade; Raça;")
  
# Delete character
def d_char(ctx):
  string = str(ctx.message.content)
  name = string[8:]
  if name:
    if search_chars(name=name, ctx=ctx):
      try:
        conn = sqlite3.connect('rpg.db')
        cursor = conn.cursor()
        cursor.execute(f"""
          delete from chars where name = '{name}' and id_user = (select id from users where username = '{ctx.author.name}');
        """)
        conn.commit()
        conn.close()
        return ctx.send("Personagem deletado com sucesso!")
      except Exception as e:
        print(f"Error: {e}")
    else:
      return ctx.send("Você não possui um personagem com esse nome!")
  else:
    return ctx.send("Por favor, digite o nome do personagem que deseja deletar! Ex.: ?d_char Nome do personagem")
  

name_monster = ""
hp_monster = 0
hp_player = 0
async def s_battle(ctx):
  name = str (ctx.message.content[10:])
  conn = sqlite3.connect('rpg.db')
  cursor = conn.cursor()

  if len(name) > 0:
    char = search_chars(ctx=ctx, name=name)
    global hp_player
    if char: hp_player = int(char[4])
    if not char:
      await ctx.send("Por favor, digite o nome do personagem com o qual deseja jogar! Ex.: ?s_battle Nome do personagem.")
      return 
  else:
      await ctx.send("Por favor, digite o nome do personagem com o qual deseja jogar! Ex.: ?s_battle Nome do personagem.")
      return 
  
  monsters = {"Goblin": 25, "Orc": 35, "Troll": 50}
  num_monster = random.randint(0,2)
  global name_monster
  name_monster = list(monsters.keys())[num_monster]
  global hp_monster 
  hp_monster = monsters[list(monsters.keys())[num_monster]]

  # Encontrando um monstro aleatório
  await ctx.send("# Monstro encontrado!\n")
  while hp_monster > 0:
    text = ( "```\n"
            "| {}                 \n"
            "| HP: {}             |\n"
            "|--------------------|\n\n"
            "| {} \n"
            "| HP: {}             |\n"
            "|--------------------|\n"
            "| Escolha uma ação:  |\n"
            "| 1 - Atacar         |\n"
            "| 2 - Defender       |\n"
            "| 3 - Fugir          |\n"
            "|--------------------|```"
            .format(name_monster, hp_monster, name, hp_player))
    await ctx.send(''.join(text))
    
    def check(m):
      return m.author == ctx.author

    try:
      msg = await ctx.bot.wait_for('message', check=check, timeout=60.0)
    except asyncio.TimeoutError:
      return await ctx.send('Tempo esgotado!')
    else:
      if msg.content == '1':
        await attack(ctx)
      elif msg.content == '2':
        await ctx.send('Você escolheu defender!')
      elif msg.content == '3':
        await ctx.send('Você escolheu fugir!')
        break
      else:
        await ctx.send('Ação inválida!')
  if hp_player > 0 and hp_monster <= 0:
    cursor.execute(f"""
      update chars set health_points = {hp_player} where name = '{name}' and id_user = (select id from users where username = '{ctx.author.name}');
    """)
    conn.commit()
    conn.close()
    await ctx.send(f"Você venceu a batalha! Seu HP foi atualizado para {hp_player}!")
  elif hp_player > 0 and hp_monster > 0:
    await ctx.send(f"Você fugiu da batalha! Seu HP foi atualizado para {hp_player}!")
  else:
    cursor.execute(f"""
      delete from chars where name = '{name}' and id_user = (select id from users where username = '{ctx.author.name}');
    """)
    conn.commit()
    conn.close()
    await ctx.send("Você foi derrotado! Seu personagem foi deletado!")
  return

async def monster_turn(ctx, name):
  dice = random.randint(1, 20)
  await ctx.send(f"# Turno do {name}!\n")

  if dice == 1:
    fail_message = [
        "Critical fail! O monstro errou feio o ataque e bateu a cabeça no chão!",
        "Critical fail! Foi um desastre total, o monstro tropeçou e caiu!",
        "Critical fail! A tentativa do monstro foi um fiasco, ele se atrapalhou e machucou a própria mão!",
        "Critical fail! O monstro não poderia ter errado mais, a espada saiu voando e o punho dela acertou a cabeça dele!",
        "Critical fail! Foi uma catástrofe, o monstro escorregou e caiu de bunda!"
    ]
    await ctx.send(f'>>> {fail_message[random.randint(0,4)]}')
  elif dice <= 5:
    fail_message = [
        "O monstro quase acertou, mas errou o",
        "Por pouco o monstro não conseguiu acertar o",
        "Foi por um triz, mas o monstro errou o",
        "Ele se desviou do ataque por pouco, o monstro errou o",
        "Ele se provou muito agilidoso e errou o"
    ]
    await ctx.send(f'>>> {fail_message[random.randint(0,4)]} jogador!')
  elif dice <= 13:
    damage = random.randint(1, 3)
    hit_message = [
        "O monstro acertou o",
        "O monstro tenta esquivas, mas acerta de raspão o",
        "O monstro provou ser mais rápido por pouco e acerta o",
        "Por pouco o monstro não errou e acertou o",
        "Ele acertou o"
    ]
    await ctx.send(f'>>> {hit_message[random.randint(0,4)]} jogador! \n'
                  f'* Dano causado: {damage}')
  elif dice <= 19:
    damage = random.randint(3, 5)
    hit_message = [
        "O monstro acertou em cheio o",
        "O monstro tenta esquivar, mas prevê e acerta com tudo o",
        "O monstro provou ser mais rápido e acerta sem dificuldades o",
        "O monstro acertou em cheio o",
        "O monstro atingiu diretamente o"
    ]
    await ctx.send(f'>>> {hit_message[random.randint(0,4)]} jogador! \n'
                  f'* Dano causado: {damage}')
  elif dice <= 20:
    damage = random.randint(5, 7)
    hit_message = [
        "O monstro mirou no torso e por sorte acertou o coração do",
        "O monstro realizou um ataque perfeito e atingiu o ponto vital do",
        "O monstro com uma precisão incrível, acertou em cheio o ponto fraco do",
        "O monstro executou um golpe devastador e causou um dano massivo ao",
        "O monstro realizou um ataque impecável que desferiu um golpe crítico no"
    ]
    await ctx.send(f'>>> {hit_message[random.randint(0,4)]} jogador! \n'
                  f'* Dano causado: {damage}')
  return

# Testar se quando tem 2 jogadores as varíaveis globais não vão dar problema --------------------------------------------------------------------------------------------------------
async def attack(ctx):
  dice = random.randint(1, 20)
  global hp_player
  global hp_monster
  global name_monster
  if dice == 1:
    fail_message = [
        "Critical fail! Você errou feio o ataque e bateu a cabeça no chão!",
        "Critical fail! Foi um desastre total, você tropeçou e caiu!",
        "Critical fail! Sua tentativa foi um fiasco, você se atrapalhou e machucou a própria mão!",
        "Critical fail! Você não poderia ter errado mais, a espada saiu voando e o punho dela acertou a sua cabeça!",
        "Critical fail! Foi uma catástrofe, você escorregou e caiu de bunda!"
    ]
    hp_player = hp_player - random.randint(1, 3)
    await ctx.send("# Turno do player!\n"
                   f'>>> {fail_message[random.randint(0,4)]}\n'
                    f"* HP do jogador: {hp_player if hp_player > 0 else 0}")
    await monster_turn(ctx)
  elif dice <= 5:
    fail_message = [
        "Você quase acertou, mas errou o",
        "Por pouco você não conseguiu acertar o",
        "Foi por um triz, mas você errou o",
        "Ele se desviou do seu ataque por pouco, você errou o",
        "Ele se provou muito agilidoso e você errou o"
    ]
    damage = 0
    hp_monster = hp_monster - damage
    await ctx.send("# Turno do player!\n"
                  f'>>> {fail_message[random.randint(0,4)]} {name_monster}! \n'
                  f'* Dano causado: {damage}\n'
                  f'* HP do monstro: {hp_monster if hp_monster > 0 else 0}')
    await monster_turn(ctx, name_monster)
  elif dice <= 13:
    damage = random.randint(1, 3)
    hp_monster = hp_monster - damage
    hit_message = [
        "Você acertou o",
        "O monstro tenta esquivas, mas você acerta de raspão o",
        "Você provou ser mais rápido por pouco e acerta o",
        "Por pouco você não errou e acertou o",
        "Foi por um fio, mas você atingiu o"
    ]
    if hp_monster <= 0:
      await ctx.send("# Turno do player!\n"
                     f'## Parabéns! Você derrotou o {name_monster}!\n'
                     f'>>> {hit_message[random.randint(0,4)]} {name_monster}! \n'
                     f'* Dano causado: {damage}\n'
                     f'* HP do monstro: {hp_monster if hp_monster > 0 else 0}')
    else:
      await ctx.send("# Turno do player!\n"
                    f'>>> {hit_message[random.randint(0,4)]} {name_monster}! \n'
                    f'* Dano causado: {damage}\n'
                    f'* HP do monstro: {hp_monster if hp_monster > 0 else 0}')
      await monster_turn(ctx, name_monster)
  elif dice <= 19:
    damage = random.randint(3, 5)
    hp_monster = hp_monster - damage
    hit_message = [
        "Você acertou em cheio o",
        "O monstro tenta esquivar, mas você o prevê e acerta com tudo o",
        "Você provou ser mais rápido e acerta sem dificuldades o",
        "Seu golpe foi perfeito e acertou em cheio o",
        "Você executou o movimento com precisão e atingiu diretamente o"
    ]
    if hp_monster <= 0:
      await ctx.send("# Turno do player!\n"
                     f'## Parabéns! Você derrotou o {name_monster}!\n'
                     f'>>> {hit_message[random.randint(0,4)]} {name_monster}! \n'
                     f'* Dano causado: {damage}\n'
                     f'* HP do monstro: {hp_monster if hp_monster > 0 else 0}')
    else:
      await ctx.send("# Turno do player!\n"
                    f'>>> {hit_message[random.randint(0,4)]} {name_monster}! \n'
                    f'* Dano causado: {damage}\n'
                    f'* HP do monstro: {hp_monster if hp_monster > 0 else 0}')
      await monster_turn(ctx, name_monster)
  elif dice <= 20:
    damage = random.randint(5, 7)*2
    hp_monster = hp_monster - damage
    success_message = [
        "Critical Success! Você mirou no torso e por sorte acertou o coração do",
        "Critical Success! Seu ataque foi perfeito e atingiu o ponto vital do",
        "Critical Success! Com uma precisão incrível, você acertou em cheio o ponto fraco do",
        "Critical Success! Seu golpe foi devastador e causou um dano massivo ao",
        "Critical Success! Você realizou um ataque impecável que desferiu um golpe crítico no"
    ]
    if hp_monster <= 0:
      await ctx.send("# Turno do player!\n"
                     f'## Parabéns! Você derrotou o {name_monster}!\n'
                     f'>>> {success_message[random.randint(0,4)]} {name_monster}! \n'
                     f'* Dano causado: {damage}\n'
                     f'* HP do monstro: {hp_monster if hp_monster > 0 else 0}')
    else:
      await ctx.send("# Turno do player!\n"
                    f'>>> {success_message[random.randint(0,4)]} {name_monster}! \n'
                    f'* Dano causado: {damage}\n'
                    f'* HP do monstro: {hp_monster if hp_monster > 0 else 0}')
      await monster_turn(ctx, name_monster)

def search_chars(ctx, name=None):
  if name:
    cursor = sqlite3.connect('rpg.db').cursor()
    cursor.execute(f"""
        select * from chars where name = '{name}' and id_user = (select id from users where username = '{ctx.author.name}');
      """)
    return cursor.fetchone()
  else:
    cursor = sqlite3.connect('rpg.db').cursor()
    cursor.execute(f"""
        select * from chars where id_user = (select id from users where username = '{ctx.author.name}');
      """)
    return cursor.fetchall()