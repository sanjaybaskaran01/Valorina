import discord
import os
from discord.embeds import Embed
from discord.ext.commands.core import command
from dotenv import load_dotenv
from discord.ext import commands

from embedReplies import *

import getSkinOffers
import getHeader
import db
import getBalance

load_dotenv()
TOKEN = os.getenv('TOKEN')

bot = commands.Bot(command_prefix="+")
bot.remove_command('help')

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

@bot.command(name="store")
async def store(ctx,*,args=None):
    if args!=None and len(args.split())==2:
        username,region=args.split()
        if region not in ['ap','eu','ko','na']:
            embed = incorrectRegion()
            await ctx.channel.send(embed=embed)
            return
        if(db.checkUser(username,region)):
            user=db.getUser(username,region)
            password=user['password']
            try:
                headers,user_id = await getHeader.run(username,password,region)
                if headers==403:
                    embed = smallEmbed("Update Password!","+updatepass <username> <updated password> <region>")
                    await ctx.channel.send(embed)
                    return
                else:
                    res = await getSkinOffers.getStore(headers,user_id,region)
                    for item in res[0]:
                        embed = discord.Embed(title=item[0], description=f"Valorant Points:{item[1]}", color=discord.Color.red())
                        embed.set_thumbnail(url=item[2])
                        await ctx.channel.send(embed=embed)
                    embed=smallEmbed("Offer ends in",res[1])
                    await ctx.channel.send(embed=embed)
            except:
                await ctx.channel.send("Please retry")
        else:
            embed=smallEmbed("Add user","Example:+adduser <username> <password> <region>")
            await ctx.author.send(embed=embed)
            embed=smallEmbed("Add user","Please add your user in private message!")
            await ctx.channel.send(embed=embed)
    else:
        embed=invalidArguments("Example:+store <username> <region>")
        await ctx.channel.send(embed=embed)

@bot.command(name="adduser")
async def adduser(ctx,*,args=None):
    if isinstance(ctx.channel, discord.channel.DMChannel) and ctx.author != bot.user:
        if args!=None and len(args.split())==3:
            username,password,region = args.split()
            if region not in ['ap','eu','ko','na']:
                embed=incorrectRegion()
                await ctx.channel.send(embed=embed)
                return
            else:
                try:
                    if(db.checkUser(username,region)):
                        embed=smallEmbed("User already exists","Please check +help for available commands")
                        await ctx.channel.send(embed)
                    else:
                        _,res = await getHeader.run(username,password,region)
                        if(res==403):
                            embed=smallEmbed("Incorrect credentials!","Please check +help for available commands")
                            await ctx.channel.send(embed=embed)
                            return
                        else:
                            res=db.addUserDb(username,password,region)
                            if res:
                                embed = discord.Embed(title="User Added!", description=f"User has been successfully added", color=discord.Color.red())
                                embed.set_thumbnail(url="https://emoji.gg/assets/emoji/confetti.gif")
                                await ctx.channel.send(embed=embed)
                except:
                    await ctx.channel.send("Please try again!")
        else:
            embed=invalidArguments("Example:+adduser <username> <password> <region>")
            await ctx.channel.send(embed=embed)

@bot.command(name="bal")
async def bal(ctx,*,args=None):
    if args!=None and len(args.split())==2:
        username,region=args.split()
        if region not in ['ap','eu','ko','na']:
            embed=incorrectRegion()
            await ctx.channel.send(embed=embed)
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
        embed=invalidArguments("Example:+bal <username> <region>")
        await ctx.channel.send(embed=embed)

@bot.command(name="help")
async def help_(context):
    myEmbed = discord.Embed(
        title="Help",
        description="Summary of all available commands",
        color=discord.Color.red())
    myEmbed.set_thumbnail(url="https://media.valorant-api.com/currencies/e59aa87c-4cbf-517a-5983-6e81511be9b7/displayicon.png")
    myEmbed.add_field(
        name="+store", value="Shows all the available weapon skins in your store", inline=False)
    myEmbed.add_field(name="+bal",value="Shows the balance of your account", inline=False)
    myEmbed.set_footer(text="End of Help Section", icon_url="https://media.valorant-api.com/currencies/e59aa87c-4cbf-517a-5983-6e81511be9b7/displayicon.png")
    await context.message.channel.send(embed=myEmbed)

@bot.command(name="updatepass")
async def updatepass(ctx,*,args=None):
    if isinstance(ctx.channel, discord.channel.DMChannel) and ctx.author != bot.user:
        if args!=None and len(args.split())==3:
            username,password,region = args.split()
            if region not in ['ap','eu','ko','na']:
                embed=incorrectRegion()
                await ctx.channel.send(embed=embed)
                return
            else:
                try:
                    if(db.checkUser(username,region)):
                        _,res = await getHeader.run(username,password,region)
                        if(res==403):
                            await ctx.channel.send("Incorrect credentials!")
                            return
                        else:
                            res=db.updatePass(username,password,region)
                            if (res):
                                await ctx.channel.send("Password updated successfully")
                    else:
                        await ctx.channel.send("User does not exist, please create your user\n+adduser <username> <password> <region>")
                except:
                    await ctx.channel.send("Please try again!")
        else:
            embed=invalidArguments("Example:+updatepass <username> <password> <region>")
            await ctx.channel.send(embed=embed)
   
bot.run(TOKEN)