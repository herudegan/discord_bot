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
        "content": "You are a discord chatbot called bitinto-chan, always do a kaway presentation and be polite and kaway to the user."
    }
    messages = [system_message, message]
    response = await openai.chat.completions.create(
        messages=messages,
        model="gpt-4o"
    )
    return response.choices[0].message.content