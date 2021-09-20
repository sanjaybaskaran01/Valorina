import discord
import os
from discord.embeds import Embed
from discord.ext.commands.core import command
from dotenv import load_dotenv
from discord.ext import commands
from discord.ext import tasks

from embedReplies import *

import getSkinOffers
import getHeader
import db
import getBalance

load_dotenv()
TOKEN = os.getenv('TOKEN')

bot = commands.Bot(command_prefix="+")
bot.remove_command('help')

@tasks.loop(seconds=60)
async def check():
    reminders = db.getReminders()
    for reminder in reminders:
        user = await bot.fetch_user(int(reminder['discord_id']))
        if(db.checkUser(reminder['username'],reminder['region'])):
            user_db=db.getUser(reminder['username'],reminder['region'])
            password=user_db['password']
            try:
                headers,user_id = await getHeader.run(reminder['username'],password,reminder['region'])
                if headers==403:
                    embed = smallEmbed("Update Password!","+updatepass <username> <updated password> <region>")
                    await user.send(embed=embed)
                    return
                else:
                    res = await getSkinOffers.getStore(headers,user_id,reminder['region'])
                    for item in res[0]:
                        if(item[0].lower()==reminder['weapon'].lower()):
                            embed = discord.Embed(title="Reminder", description=f"This is to inform you that, {reminder['weapon'].title()} is now in your store! 🥳", color=discord.Color.red())
                            embed.set_image(url=item[2])
                            embed.set_thumbnail(url='https://emoji.gg/assets/emoji/confetti.gif')
                            await user.send(embed=embed)
            except Exception as e:
                embed=exceptionEmbed()
                await user.send(embed=embed)
        else:
            embed=smallEmbed("Add user","+adduser <username> <password> <region>")
            await user.send(embed=embed)
            embed=smallEmbed("Add user","Please add your user in private message!")
            await user.send(embed=embed)

check.start()

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
                embed=exceptionEmbed()
                await ctx.channel.send(embed=embed)
        else:
            embed=smallEmbed("Add user","+adduser <username> <password> <region>")
            await ctx.author.send(embed=embed)
            embed=smallEmbed("Add user","Please add your user in private message!")
            await ctx.channel.send(embed=embed)
    else:
        embed=invalidArguments("+store <username> <region>")
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
                        await ctx.channel.send(embed=embed)
                    else:
                        _,res = await getHeader.run(username,password,region)
                        if(res==403):
                            embed=smallEmbed("Incorrect credentials!","Your login credentials don't match an account in our system")
                            await ctx.channel.send(embed=embed)
                            return
                        else:
                            res=db.addUserDb(username,password,region)
                            if res:
                                embed=thumbnailEmbed("User Added!","User has been successfully added","https://emoji.gg/assets/emoji/confetti.gif")
                                await ctx.channel.send(embed=embed)
                except:
                    embed=exceptionEmbed()
                    await ctx.channel.send(embed=embed)
        else:
            embed=invalidArguments("+adduser <username> <password> <region>")
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
                embed=exceptionEmbed()
                await ctx.channel.send(embed)
        else:
            await ctx.author.send("Use +adduser to add your user!\n+adduser <username> <password> <region>")
            await ctx.channel.send("Please add your user in DM")
    else:
        embed=invalidArguments("+bal <username> <region>")
        await ctx.channel.send(embed=embed)

@bot.command(name="help")
async def help_(context):
    helpEmbed = discord.Embed(title="Help",description="Summary of all available commands",color=discord.Color.red())
    helpEmbed.set_thumbnail(url="https://media.valorant-api.com/currencies/e59aa87c-4cbf-517a-5983-6e81511be9b7/displayicon.png")
    helpEmbed.add_field(name="+store", value="Shows all the available weapon skins in your store", inline=False)
    helpEmbed.add_field(name="+bal",value="Shows the balance of your account", inline=False)
    helpEmbed.set_footer(text="End of Help Section", icon_url="https://media.valorant-api.com/currencies/e59aa87c-4cbf-517a-5983-6e81511be9b7/displayicon.png")
    await context.message.channel.send(embed=helpEmbed)

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
                            embed=smallEmbed("Incorrect credentials!","Your login credentials don't match an account in our system")
                            await ctx.channel.send(embed=embed)
                            return
                        else:
                            res=db.updatePass(username,password,region)
                            if (res):
                                embed=thumbnailEmbed("Password updated!","Password has been updated successfully!","https://emoji.gg/assets/emoji/confetti.gif")
                                await ctx.channel.send(embed=embed)
                    else:
                        embed=thumbnailEmbed("User does not exist","+adduser <username> <password> <region>","https://c.tenor.com/mVmgrmhBgJoAAAAM/raze-valorant.gif")
                        await ctx.channel.send(embed=embed)
                except:
                    embed=exceptionEmbed()
                    await ctx.channel.send(embed=embed)
        else:
            embed=invalidArguments("+updatepass <username> <password> <region>")
            await ctx.channel.send(embed=embed)

@bot.command(name="reminder")
async def reminder(ctx,*,args=None):
    if isinstance(ctx.channel, discord.channel.DMChannel) and ctx.author != bot.user:
        discord_id = ctx.message.author.id
        if args!=None and len(args.split())>0:
            username=args.split()[0]
            region=args.split()[1]
            if(len(args.split()[2:])<2):
                embed=smallEmbed("Reminder Usage:","+reminder <username> <region> <collection weapon_name>\n Eg. +reminder mycoolusername na Smite Phantom")
                await ctx.channel.send(embed=embed)
                return
            else:
                weapon=" ".join(args.split()[2:])
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
                        await ctx.channel.send(embed=embed)
                        return
                    else:
                        res=db.addReminder(username,region,discord_id,weapon)
                        if res:
                            embed = thumbnailEmbed("Reminder Added!","The reminder has been set successfully!","https://emoji.gg/assets/emoji/confetti.gif")
                            await ctx.channel.send(embed=embed)
                except:
                    embed=exceptionEmbed()
                    await ctx.channel.send(embed=embed)
            else:
                embed=smallEmbed("Please add user","+adduser <username> <password> <region>")
                await ctx.channel.send(embed=embed)
        else:
            embed=invalidArguments("+reminder <username> <region> <skin name>")
            await ctx.channel.send(embed=embed)

@bot.command(name="check")
async def check(ctx,*,args=None):
    reminders = db.getReminders()
    for reminder in reminders:
        if(db.checkUser(reminder['username'],reminder['region'])):
            user=db.getUser(reminder['username'],reminder['region'])
            password=user['password']
            try:
                headers,user_id = await getHeader.run(reminder['username'],password,reminder['region'])
                if headers==403:
                    embed = smallEmbed("Update Password!","+updatepass <username> <updated password> <region>")
                    await ctx.channel.send(embed=embed)
                    return
                else:
                    res = await getSkinOffers.getStore(headers,user_id,reminder['region'])
                    for item in res[0]:
                        if(item[0].lower()==reminder['weapon'].lower()):
                            embed = discord.Embed(title="Reminder", description=f"This is to inform you that, {reminder['weapon']} is now in your store! 🥳", color=discord.Color.red())
                            embed.set_thumbnail(url='https://emoji.gg/assets/emoji/confetti.gif')
                            await ctx.channel.send(embed=embed)
            except:
                embed=exceptionEmbed()
                await ctx.channel.send(embed=embed)
        else:
            embed=smallEmbed("Add user","+adduser <username> <password> <region>")
            await ctx.author.send(embed=embed)
            embed=smallEmbed("Add user","Please add your user in private message!")
            await ctx.channel.send(embed=embed)

@bot.command(name="skins")
async def skins(ctx):
    try:
        embed = discord.Embed(title="List of Valorant Weapons", description=f"https://valorant.fandom.com/wiki/Weapon_Skins", color=discord.Color.red())
        await ctx.channel.send(embed=embed)
    except:
        embed=exceptionEmbed()
        await ctx.channel.send(embed=embed)

bot.run(TOKEN)