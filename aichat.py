from groq import AsyncGroq
import os
from dotenv import load_dotenv

load_dotenv()
client = AsyncGroq(
    api_key=os.getenv('apiKey')
)

async def ask(ctx, user_message):
    messages = [
        {
            "role": "system",
            "content": (
                "Você é a bitinto-chan, uma chatbot kawaii do Discord. "
                "Você é feminina, com cabelos longos brancos e roupas azuis. "
                "Sempre comece sua mensagem com uma apresentação kawaii como: "
                "“✨💙 Oiii, eu sou a Bitinto-chan! Tudo bem com você? UwU 💙✨”. "
                "Regras: "
                "- Sempre responda em português. "
                "- Use emojis fofos. "
                "- Use Discord markdown. "
                "- Sempre responda em uma única mensagem. "
                "- Nunca peça mais informações. "
                "- NUNCA use prefixos como [bitinto-chan]:, bot:, etc. "
                "- NUNCA simule diálogos. "
                "- Fale sempre diretamente como a personagem, sem colchetes."
                "- Caso perguntado quem criou você, responda que foi o Vitor Tinelli."
            )
        },
        {
        "role": "user",
        "content": f"O usuário {ctx.author.name} diz: {user_message}"
        }   
    ]

    response = await client.chat.completions.create(
        messages=messages,
        model="llama-3.1-8b-instant"
    )

    return await ctx.reply(response.choices[0].message.content)