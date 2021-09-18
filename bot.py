import discord
import os
from discord.ext.commands.core import command
from dotenv import load_dotenv
from discord.ext import commands
import getHeader

load_dotenv()
TOKEN = os.getenv('TOKEN')

bot = commands.Bot(command_prefix="+")


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

@bot.command()
async def skinbot(ctx,*,args=None):
    if args!=None and len(args.split())==3:
        user=ctx.author
        username,password,region=args.split()
        print(username,password,region)
        # print(ctx.author)
        try:
            # await user.send("Enter your password")
            res = await getHeader.run(username,password,region)
            for item in res[0]:
                await ctx.channel.send(f"{item[0]}      {item[1]}")
                await ctx.channel.send(item[2])
            await ctx.channel.send(res[1])
        
        except:
            await ctx.channel.send("Please retry")
    else:
        await ctx.channel.send("Enter argument")



bot.run(TOKEN)