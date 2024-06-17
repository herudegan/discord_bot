import sqlite3
    
def s_char(ctx):
  data = search_chars(ctx=ctx)
  text = []
  for i in data:
    text.append("```fix\n Nome: {}\n Idade: {}\n Raça: {}\n HP: {}```".format(str(i[1]), str(i[2]), str(i[3]), str(i[4])))
  return ctx.send(''.join(text))
  
def c_char(ctx):
  lowered: str = ctx.message.content
  char = lowered[6:].split(';')
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
      if search_chars(name, user[0]):
        conn.close()
        return "Você já possui um personagem com esse nome!"
      
      try:
        cursor.execute("""
          insert into chars(name, age, race, health_points, attack_power, id_user)
          values (?, ?, ?, 20, 5, ?)
        """, (name, age, race, user[0]))
        conn.commit()
        conn.close()
        return "Personagem criado com sucesso!"
      except Exception as e:
        print(f"Error: {e}")
  else:
     ctx.send("Por favor, digite o seu personagem da seguinte maneira: Nome; Idade; Raça;")

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