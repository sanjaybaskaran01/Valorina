from discord.embeds import Embed
import discord


def incorrectRegion():
    embed = discord.Embed(title="Incorrect Region", description="Use one of the following regions", color=discord.Color.red(),inline=True)
    embed.add_field(name="eu",value="for Europe users", inline=False)
    embed.add_field(name="ap",value="for Asia Pacific users", inline=False)
    embed.add_field(name="ko",value="for Korean users", inline=False)
    embed.add_field(name="na",value="for North American users", inline=False)
    return embed

def invalidArguments(desc):
    embed = discord.Embed(title="Invalid arguments", description=desc, color=discord.Color.red(),inline=True)
    embed.add_field(name="eu",value="for Europe users", inline=False)
    embed.add_field(name="ko",value="for Korean users", inline=False)
    embed.add_field(name="ap",value="for Asia Pacific users", inline=False)
    embed.add_field(name="na",value="for North American users", inline=False)
    return embed

def smallEmbed(title,description):
    embed = discord.Embed(title=title, description=description, color=discord.Color.red(),inline=True)
    return embed

def thumbnailEmbed(title,description,url):
    embed = discord.Embed(title=title, description=description, color=discord.Color.red(),inline=True)
    embed.set_thumbnail(url=url)
    return embed