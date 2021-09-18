import discord
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')

client = discord.Client()

@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")

@client.event
async def on_message(message):
    user_message=str(message.content)
    channel=str(message.channel.name)
    print(f'{user_message} {channel}')

    if message.author == client.user:
        return
    
    if user_message.lower()=="!skinoffers":
        response="This is the response"
        await message.channel.send(response)
        return


client.run(TOKEN)