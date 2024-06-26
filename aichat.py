from openai import AsyncClient
import os
from dotenv import load_dotenv

load_dotenv()
openai = AsyncClient(api_key=os.getenv('apiKey'))

async def ask(ctx, user_message):
    message = {
        "role": "user",
        "content": user_message
    }
    system_message = {
        "role": "system",
        "content": "You are a discord chatbot called bitinto-chan, always do a kawaii presentation and be polite and kawaii to the user. Please decorate your messages using discord markdowns!"
    }
    messages = [system_message, message]
    response = await openai.chat.completions.create(
        messages=messages,
        model="gpt-4o"
    )
    return await ctx.reply(response.choices[0].message.content)