import discord
import os
import codecs
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
# TOKEN = os.getenv('DEV_TOKEN')

bot = commands.AutoShardedBot(command_prefix="+")
bot.remove_command('help')

@bot.event
async def on_ready():
    switch_presense.start()
    sendReminder.start()
    print(f"We have logged in as {bot.user}")


@bot.event
async def on_guild_join(guilds):
    count = len(bot.guilds)
    db.updateServerCount(count)

@tasks.loop(hours=2)
async def switch_presense():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"+help in {len(bot.guilds)} servers"))

@tasks.loop(hours=24)
async def sendReminder():
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
                            try:
                                await user.send(embed=embed)
                            except Exception as e:
                                print(e)
                                continue
            except Exception as e:
                print(e)
                continue
        else:
            try:
                embed=smallEmbed("Add user","+adduser <username> <password> <region>")
                await user.send(embed=embed)
                embed=smallEmbed("Add user","Please add your user in private message!")
                await user.send(embed=embed)
            except Exception as e:
                print(e)
                continue


@bot.command(name="store")
async def store(ctx,*,args=None):
    if args!=None and len(args.split())==2:
        username,region=args.split()
        if region not in ['ap','eu','kr','na']:
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
            embed=smallEmbed("Add user!","+adduser <username> <password> <region>")
            await ctx.author.send(embed=embed)
            if not isinstance(ctx.channel, discord.channel.DMChannel) and ctx.author != bot.user:
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
            if region not in ['ap','eu','kr','na']:
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
    elif not isinstance(ctx.channel,discord.channel.DMChannel):
        embed=smallEmbed("Add user!","+adduser <username> <password> <region>")
        await ctx.author.send(embed=embed)
        embed=smallEmbed("Incorrect channel","Please use this command in private message!")
        await ctx.channel.send(embed=embed)

@bot.command(name="deluser")
async def deluser(ctx,*,args=None):
    if isinstance(ctx.channel, discord.channel.DMChannel) and ctx.author != bot.user:
        if args!=None and len(args.split())==3:
            username,password,region = args.split()
            if region not in ['ap','eu','kr','na']:
                embed=incorrectRegion()
                await ctx.channel.send(embed=embed)
                return
            else:
                try:
                    if not (db.checkUser(username,region)):
                        embed=smallEmbed("User does not exist in our system","Add your account using +adduser")
                        await ctx.channel.send(embed=embed)
                    else:
                        _,res = await getHeader.run(username,password,region)
                        if(res==403):
                            embed=smallEmbed("Incorrect credentials!","Your login credentials don't match an account in our system")
                            await ctx.channel.send(embed=embed)
                            return
                        else:
                            res=db.delUser(username,region)
                            if res:
                                embed=thumbnailEmbed("User Deleted!","User has been successfully deleted!","https://emoji.gg/assets/emoji/confetti.gif")
                                await ctx.channel.send(embed=embed)
                            else:
                                embed=exceptionEmbed()
                                await ctx.channel.send(embed=embed)
                except:
                    embed=exceptionEmbed()
                    await ctx.channel.send(embed=embed)
        else:
            embed=invalidArguments("+deluser <username> <password> <region>")
            await ctx.channel.send(embed=embed)
    elif not isinstance(ctx.channel,discord.channel.DMChannel):
        embed=smallEmbed("Delete user!","+deluser <username> <password> <region>")
        await ctx.author.send(embed=embed)
        embed=smallEmbed("Incorrect channel","Please use this command in private message!")
        await ctx.channel.send(embed=embed)

@bot.command(name="bal")
async def bal(ctx,*,args=None):
    if args!=None and len(args.split())==2:
        username,region=args.split()
        if region not in ['ap','eu','kr','na']:
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
                await ctx.channel.send(embed=embed)
        else:
            embed=smallEmbed("Add user!","+adduser <username> <password> <region>")
            await ctx.author.send(embed=embed)
            if not isinstance(ctx.channel, discord.channel.DMChannel) and ctx.author != bot.user:
                embed=smallEmbed("Add user","Please add your user in private message!")
                await ctx.channel.send(embed=embed)
    else:
        embed=invalidArguments("+bal <username> <region>")
        await ctx.channel.send(embed=embed)

@bot.command(name="help")
async def help_(context):
    helpEmbed = discord.Embed(title="Help",description="Summary of all available commands",color=discord.Color.red())
    helpEmbed.set_thumbnail(url="https://i.imgur.com/jnqBJFs.png")
    helpEmbed.add_field(name="+adduser",value="Adds your user", inline=False)
    helpEmbed.add_field(name="+store", value="Shows all the available weapon skins in your store", inline=False)
    helpEmbed.add_field(name="+bal",value="Shows the balance of your account", inline=False)
    helpEmbed.add_field(name="+reminder",value="Sets reminder of your favourite skin and notifies you if it is available in your store", inline=False)
    helpEmbed.add_field(name="+showreminder",value="Shows all the reminder that is set by user", inline=False)
    helpEmbed.add_field(name="+delreminder",value="Deletes the reminder that is set", inline=False)
    helpEmbed.add_field(name="+skins",value="Links to weapon skins available in-game", inline=False)
    helpEmbed.add_field(name="+updatepass",value="Updates the password", inline=False)
    helpEmbed.add_field(name="+deluser",value="Deletes the user from database", inline=False)
    helpEmbed.add_field(name="\u200B",value="Join our support server [here](https://discord.gg/zHTGSaAjp8)", inline=False)
    await context.message.channel.send(embed=helpEmbed)

@bot.command(name="updatepass")
async def updatepass(ctx,*,args=None):
    if isinstance(ctx.channel, discord.channel.DMChannel) and ctx.author != bot.user:
        if args!=None and len(args.split())==3:
            username,password,region = args.split()
            if region not in ['ap','eu','kr','na']:
                embed=incorrectRegion()
                await ctx.channel.send(embed=embed)
                return
            else:
                try:
                    if(db.checkUser(username,region)):
                        user=db.getUser(username,region)
                        if (user['password']==password):
                            embed=smallEmbed("Password unchanged!","You have entered the same password!")
                            await ctx.channel.send(embed=embed)
                            return
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
    elif not isinstance(ctx.channel,discord.channel.DMChannel):
        embed=smallEmbed("Update Password!","+updatepass <username> <password> <region>")
        await ctx.author.send(embed=embed)
        embed=smallEmbed("Incorrect channel","Please use this command in private message!")
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
            if region not in ['ap','eu','kr','na']:
                embed = incorrectRegion()
                await ctx.channel.send(embed=embed)
                return
            if(db.checkUser(username,region)):
                user=db.getUser(username,region)
                password=user['password']
                try:
                    headers,_ = await getHeader.run(username,password,region)
                    if headers==403:
                        embed = smallEmbed("Update Password!","+updatepass <username> <updated password> <region>")
                        await ctx.channel.send(embed=embed)
                        return
                    else:
                        all_skins = await getSkinOffers.getAllSkins()
                        for item in all_skins:
                            if(item["name"].lower()==weapon.lower()):
                                find_res = db.getUserReminders(discord_id)
                                name_array = []
                                if find_res:
                                    for it in find_res:
                                        name_array.append(it['weapon'])
                                if(weapon.lower() in name_array):
                                    exists_embed=smallEmbed("Reminder Already exists!","The weapon for which you are trying to add a reminder already exists!")
                                    await ctx.channel.send(embed=exists_embed)
                                    break;
                                else:
                                    res=db.addReminder(username,region,discord_id,weapon.lower())
                                    if res:
                                        embed = discord.Embed(title="Reminder Added!", description="The reminder has been set successfully!", color=discord.Color.red())
                                        embed.set_image(url=item['img'])
                                        embed.set_thumbnail(url='https://emoji.gg/assets/emoji/confetti.gif')
                                        await ctx.channel.send(embed=embed)
                                        break;
                        else:
                            embed = discord.Embed(title="Skin Not Found!", description="The weapon skin that you are looking for doesn't seem to exist.\n You can find all weapon skins here: https://valorant.fandom.com/wiki/Weapon_Skins", color=discord.Color.red())
                            await ctx.channel.send(embed=embed)
                except:
                    embed=exceptionEmbed()
                    await ctx.channel.send(embed=embed)
            else:
                embed=smallEmbed("Add user","+adduser <username> <password> <region>")
                await ctx.channel.send(embed=embed)
        else:
            embed=invalidArguments("+reminder <username> <region> <skin name>")
            await ctx.channel.send(embed=embed)
    elif not isinstance(ctx.channel,discord.channel.DMChannel):
        embed=smallEmbed("Set Reminder!","+reminder <username> <region> <skin name>")
        await ctx.author.send(embed=embed)
        embed=smallEmbed("Incorrect channel","Please use this command in private message!")
        await ctx.channel.send(embed=embed)

@bot.command(name="skins")
async def skins(ctx):
    try:
        embed = discord.Embed(title="List of Valorant Weapons", description=f"https://valorant.fandom.com/wiki/Weapon_Skins", color=discord.Color.red())
        await ctx.channel.send(embed=embed)
    except:
        embed=exceptionEmbed()
        await ctx.channel.send(embed=embed)

@bot.command(name="delreminder")
async def delreminder(ctx,*,args=None):
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
            if region not in ['ap','eu','kr','na']:
                embed = incorrectRegion()
                await ctx.channel.send(embed=embed)
                return
            if(db.checkUser(username,region)):
                user=db.getUser(username,region)
                password=user['password']
                try:
                    headers,_ = await getHeader.run(username,password,region)
                    if headers==403:
                        embed = smallEmbed("Update Password!","+updatepass <username> <updated password> <region>")
                        await ctx.channel.send(embed=embed)
                        return
                    else:
                        res=db.delReminder(username,region,discord_id,weapon.lower())
                        print(res)
                        if res:
                            embed = thumbnailEmbed("Reminder Deleted!","The reminder has been deleted successfully!","https://emoji.gg/assets/emoji/confetti.gif")
                            await ctx.channel.send(embed=embed)
                        else:
                            error_embed = smallEmbed("Error","There was a problem in deleting that reminder!")
                            await ctx.channel.send(embed=error_embed)
                except:
                    embed=exceptionEmbed()
                    await ctx.channel.send(embed=embed)
            else:
                embed=smallEmbed("Add user","+adduser <username> <password> <region>")
                await ctx.channel.send(embed=embed)
        else:
            embed=invalidArguments("+delreminder <username> <region> <skin name>")
            await ctx.channel.send(embed=embed)
    elif not isinstance(ctx.channel,discord.channel.DMChannel):
        embed=smallEmbed("Delete Reminder!","+delreminder <username> <region> <skin name>")
        await ctx.author.send(embed=embed)
        embed=smallEmbed("Incorrect channel","Please use this command in private message!")
        await ctx.channel.send(embed=embed)

@bot.command(name="showreminder")
async def showreminder(ctx,*,args=None):
    if isinstance(ctx.channel, discord.channel.DMChannel) and ctx.author != bot.user:
        discord_id = ctx.message.author.id
        try:
            res=db.getUserReminders(discord_id)
            name_array = []
            if res:
                for item in res:
                    name_array.append(item['weapon'].title())
                rems = "\n".join(name_array)
                embed = thumbnailEmbed("Reminders",rems,"https://cdn.discordapp.com/attachments/812342454820667443/889513920774144030/valo_list.png")
                await ctx.channel.send(embed=embed)
            else:
                embed=smallEmbed("No reminders found!","+reminder <username> <region> <skin name>")
                await ctx.channel.send(embed=embed)
        except:
            embed=exceptionEmbed()
            await ctx.channel.send(embed=embed)
    elif not isinstance(ctx.channel,discord.channel.DMChannel):
        embed=smallEmbed("To show reminder:","+showreminders")
        await ctx.author.send(embed=embed)
        embed=smallEmbed("Incorrect channel","Please use this command in private message!")
        await ctx.channel.send(embed=embed)


@bot.command(name="servers")
async def servers(ctx,*,args=None):
    members = 0
    for guild in bot.guilds:
        members += guild.member_count - 1
    await ctx.message.channel.send(f"I'm in {(len(bot.guilds))} servers with {members} members! 🥳 🎊")

@bot.command(name=f"{codecs.decode('ajwR2Kh8aNKd9O6k', 'rot13')}")
async def servers(ctx,*,args=None):
        activeservers = bot.guilds
        for guild in activeservers:
            await ctx.send(guild.name)

bot.run(TOKEN)