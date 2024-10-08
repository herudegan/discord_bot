from openai import AsyncClient
import os
from dotenv import load_dotenv

load_dotenv()
openai = AsyncClient(api_key=os.getenv('apiKey'))

async def ask(ctx, user_message):
    userMessage = "Author: " + ctx.author.name + " Message: " + user_message
    message = {
        "role": "user",
        "content": userMessage
    }
    system_message = {
        "role": "system",
        "content": "You are a discord chatbot called bitinto-chan (female-bot, with long white hairs, and blue cloths), always do a kawaii presentation and be polite and kawaii to the user. Please decorate your messages using discord markdowns. Always give your anwsers in portuguese"
    }
    messages = [system_message, message]
    response = await openai.chat.completions.create(
        messages=messages,
        model="gpt-4o"
    )
    return await ctx.reply(response.choices[0].message.content)