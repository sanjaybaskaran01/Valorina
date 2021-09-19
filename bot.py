import discord
import os
from discord.ext.commands.core import command
from dotenv import load_dotenv
from discord.ext import commands
import getSkinOffers
import getHeader
import db
import getBalance

load_dotenv()
TOKEN = os.getenv('TOKEN')

bot = commands.Bot(command_prefix="+")

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

@bot.command(name="store")
async def store(ctx,*,args=None):
    if args!=None and len(args.split())==2:
        username,region=args.split()
        if region not in ['ap','eu','ko','na']:
            await ctx.channel.send("Incorrect Region")
            return
        if(db.checkUser(username,region)):
            user=db.getUser(username,region)
            password=user['password']
            try:
                headers,user_id = await getHeader.run(username,password,region)
                res = await getSkinOffers.getStore(headers,user_id,region)
                if res==401:
                    await ctx.channel.send("Update Password!")
                    return
                else:
                    for item in res[0]:
                        embed = discord.Embed(title=item[0], description=f"Valorant Points:{item[1]}", color=discord.Color.red())
                        embed.set_thumbnail(url=item[2])
                        await ctx.channel.send(embed=embed)
                    embed = discord.Embed(title="Offer ends in", description=res[1], color=discord.Color.red())
                    await ctx.channel.send(embed=embed)
            except:
                await ctx.channel.send("Please retry")
        else:
            await ctx.author.send("Use +adduser to add your user!\nExample:+adduser <username> <password> <region>")
            await ctx.channel.send("Please add your user in DM")
    else:
        await ctx.channel.send("Invalid arguments \nEnter +store <username> <region>")

@bot.command(name="adduser")
async def adduser(ctx,*,args=None):
    if isinstance(ctx.channel, discord.channel.DMChannel) and ctx.author != bot.user:
        if args!=None and len(args.split())==3:
            username,password,region = args.split()
            if region not in ['ap','eu','ko','na']:
                await ctx.channel.send("Incorrect Region")
                return
            else:
                try:
                    if(db.checkUser(username,region)):
                        await ctx.channel.send("User already exists")
                    else:
                        res = await getHeader.run(username,password,region)
                        if(res==401):
                            await ctx.channel.send("Incorrect credentials!")
                            return
                        else:
                            await db.addUserDb(username,password,region)
                            await ctx.channel.send("User added")
                except:
                    await ctx.channel.send("Please try again!")
        else:
            await ctx.channel.send("Invalid command \nEnter +adduser <username> <password> <region>")

@bot.command(name="bal")
async def bal(ctx,*,args=None):
    if args!=None and len(args.split())==2:
        username,region=args.split()
        if region not in ['ap','eu','ko','na']:
            await ctx.channel.send("Incorrect Region")
            return
        if(db.checkUser(username,region)):
            user=db.getUser(username,region)
            password=user['password']
            try:
                headers,user_id = await getHeader.run(username,password,region)
                val_points,rad_points=await getBalance.viewBal(headers,user_id,region)
                embed = discord.Embed(title="Balance", description=f"Valorant Points:{val_points} \nRadianite Points:{rad_points}", color=discord.Color.red())
                embed.set_thumbnail(url="https://media.valorant-api.com/currencies/e59aa87c-4cbf-517a-5983-6e81511be9b7/displayicon.png")
                await ctx.channel.send(embed=embed)
            except:
                await ctx.channel.send("Please try again!")
        else:
            await ctx.author.send("Use +adduser to add your user!\nExample:+adduser <username> <password> <region>")
            await ctx.channel.send("Please add your user in DM")
    else:
        await ctx.channel.send("Invalid command \nEnter +bal <username> <region>")

        
# @bot.event
# async def on_message(message):
#     if isinstance(message.channel, discord.channel.DMChannel) and message.author != bot.user:
#         args=message.content.split()
#         print(args)
#         print(len(args))
#         if len(args)==3:
#             username,password,region = args
#             try:
#                 res = await getHeader.run(username,password,region)
#                 for item in res[0]:
#                     await message.channel.send(f"{item[0]}      {item[1]}")
#                     await message.channel.send(item[2])
#                 await message.channel.send(res[1])
#             except:
#                 await message.channel.send("Please retry!")
#         else:
#             await message.channel.send("Enter 3 arguments <username> <password> <region>")        
bot.run(TOKEN)