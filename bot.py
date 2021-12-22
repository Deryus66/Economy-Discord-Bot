import discord
from discord.ext.commands.converter import EmojiConverter
import random
from discord.ext import commands
from discord.ext.commands import has_permissions
from discord.message import Message
from discord.utils import get
import math
import asyncio
import asyncpg
from asyncpg.pool import create_pool
import requests
import os





intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='+', intents=intents)
bot.remove_command("help")

async def create_db_pool():
    bot.pg_con = await asyncpg.create_pool(database="databasename",user="databaseusername",password="databasepassword")
    


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='🤑'))
    print("Ready")


@bot.event
async def on_guild_join(guild):
    pass

@bot.event
async def on_member_join(member):
    
    
   
    user_name = str(member.name)
    user_nametag = str(member)
    author_id = str(member.id)
    guild_id = str(member.guild.id)
    guild_roles = member.guild.roles

    
    guild_roleNames = []
    guild_roleIDs = []
    guild_rolePrices = []


    user = await bot.pg_con.fetch("SELECT * FROM user_info WHERE user_id = $1 AND guild_id = $2",  author_id, guild_id)

    #This block of code is used to determine if the user is in our database if not it will put their info in the database
    #The if conditions are if the user decides to change their name, since we keep track of the user id, we know if they change their username
    #This block of code is for the user_info database
    if not user:
        await bot.pg_con.execute("INSERT into user_info (user_name, user_nametag, user_id, guild_id, level, exp, money) VALUES ($1, $2, $3, $4, 1, 0, '0')", user_name, user_nametag, author_id, guild_id)
    elif (user_nametag != user[0]['user_nametag'] and user_name != user[0]['user_name']):
        await bot.pg_con.execute("UPDATE user_info SET user_nametag = $1 WHERE user_id = $2 AND guild_id = $3", user_nametag, author_id, guild_id)
        await bot.pg_con.execute("UPDATE user_info SET user_name = $1 WHERE user_id = $2 AND guild_id = $3", user_name, author_id, guild_id)
    elif (user_nametag != user[0]['user_nametag'] ):
        await bot.pg_con.execute("UPDATE user_info SET user_nametag = $1 WHERE user_id = $2 AND guild_id = $3", user_nametag, author_id, guild_id)
    elif (user_name != user[0]['user_name'] ):
        await bot.pg_con.execute("UPDATE user_info SET user_name = $1 WHERE user_id = $2 AND guild_id = $3", user_name, author_id, guild_id)
        
    #This block of code is used to determine if the server itself is in our database
    #This database keeps track of server information
    #This block of code is for the server_banks information
   
    server = await bot.pg_con.fetch("SELECT * FROM server_banks WHERE guild_id = $1",  guild_id)
    if not server:
        await bot.pg_con.execute("INSERT into server_banks (guild_id, server_roles, server_rolesid, server_rolesprice, server_balance) VALUES ($1, $2, $3, $4, '1000000000000')", guild_id, guild_roleNames, guild_roleIDs, guild_rolePrices)
    else:
    
        await bot.pg_con.execute("UPDATE server_banks SET server_roles = $1 WHERE guild_id = $2", guild_roleNames,  guild_id)
        await bot.pg_con.execute("UPDATE server_banks SET server_rolesid = $1 WHERE guild_id = $2", guild_roleIDs, guild_id)
        


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f'Be patient! You must wait {round(error.retry_after, 2)} seconds before using this command!')

async def add_experience(user, server, exp):

    
    
    fetch_exp = await bot.pg_con.fetch("SELECT exp FROM user_info WHERE user_id = $1 AND guild_id = $2", str(user), str(server))
    current_exp= int(fetch_exp[0]['exp'])
    
    new_exp = int(current_exp + int(exp))
    
    await bot.pg_con.execute("UPDATE user_info SET exp = $1 WHERE user_id = $2 AND guild_id = $3", new_exp, str(user), str(server))


async def level_up(user, server, channel):
     fetch_exp = await bot.pg_con.fetch("SELECT exp FROM user_info WHERE user_id = $1 AND guild_id = $2", str(user.id), str(server))
     fetch_lvl = await bot.pg_con.fetch("SELECT level FROM user_info WHERE user_id = $1 AND guild_id = $2", str(user.id), str(server))

     lvl_start = int(fetch_lvl[0]['level'])
     exp = int(fetch_exp[0]['exp'])

     lvl_end = int(exp ** (1/4))

     if(not user.bot and lvl_start < lvl_end):
         
         await bot.pg_con.execute("UPDATE user_info SET level = $1 WHERE user_id = $2 AND guild_id = $3", int(lvl_start) + 1, str(user.id), str(server))
         await channel.send(f"{user.mention} leveled up to level {int(lvl_start) + 1}")

@bot.event
async def on_message(message):

    

    user_name = str(message.author.name)
    user_nametag = str(message.author)
    author_id = str(message.author.id)
    guild_id = str(message.guild.id)
    guild_roles = message.guild.roles
    
    
    guild_roleNames = []
    guild_roleIDs = []
    guild_rolePrices = []

    
    for role in guild_roles:
        guild_roleNames.append(str(role.name))
        guild_roleIDs.append(str(role.id))
        guild_rolePrices.append('0')
    
    
    
    
    

  
    user = await bot.pg_con.fetch("SELECT * FROM user_info WHERE user_id = $1 AND guild_id = $2",  author_id, guild_id)
    #user is a list/tuple cause a database
   
    
    #This block of code is used to determine if the user is in our database if not it will put their info in the database
    #The if conditions are if the user decides to change their name, since we keep track of the user id, we know if they change their username
    #This block of code is for the user_info database
    if not user:
        await bot.pg_con.execute("INSERT into user_info (user_name, user_nametag, user_id, guild_id, level, exp, money) VALUES ($1, $2, $3, $4, 1, 0, '0')", user_name, user_nametag, author_id, guild_id)
    elif (user_nametag != user[0]['user_nametag'] and user_name != user[0]['user_name']):
        await bot.pg_con.execute("UPDATE user_info SET user_nametag = $1 WHERE user_id = $2 AND guild_id = $3", user_nametag, author_id, guild_id)
        await bot.pg_con.execute("UPDATE user_info SET user_name = $1 WHERE user_id = $2 AND guild_id = $3", user_name, author_id, guild_id)
    elif (user_nametag != user[0]['user_nametag'] ):
        await bot.pg_con.execute("UPDATE user_info SET user_nametag = $1 WHERE user_id = $2 AND guild_id = $3", user_nametag, author_id, guild_id)
    elif (user_name != user[0]['user_name'] ):
        await bot.pg_con.execute("UPDATE user_info SET user_name = $1 WHERE user_id = $2 AND guild_id = $3", user_name, author_id, guild_id)
        
    #This block of code is used to determine if the server itself is in our database
    #This database keeps track of server information
    #This block of code is for the server_banks information
   
    server = await bot.pg_con.fetch("SELECT * FROM server_banks WHERE guild_id = $1",  guild_id)
    if not server:
        await bot.pg_con.execute("INSERT into server_banks (guild_id, server_roles, server_rolesid, server_rolesprice, server_balance) VALUES ($1, $2, $3, $4, '1000000000000')", guild_id, guild_roleNames, guild_roleIDs, guild_rolePrices)
    else:
    
        await bot.pg_con.execute("UPDATE server_banks SET server_roles = $1 WHERE guild_id = $2", guild_roleNames,  guild_id)
        await bot.pg_con.execute("UPDATE server_banks SET server_rolesid = $1 WHERE guild_id = $2", guild_roleIDs, guild_id)
        
    await add_experience(author_id, guild_id, 1)
    await level_up(message.author, guild_id, message.channel)
    
    await bot.process_commands(message)
    
@bot.group(invoke_without_command=True)
async def help(ctx):
    embed = discord.Embed(
        title=f"Help Page",
        description ="Use +help <command> for more info"
    )
    embed.add_field(name = "Info Commands", value = "myinfo, viewinfo")
    embed.add_field(name = "Economy Commands", value = "mybank, viewbank, serverbank, payday, steal")
    embed.add_field(name = "Crypto Commands", value = "crypto, mycrypto, buycrypto, sellcrypto")
    embed.add_field(name = "Games/Fun", value = "blackjack")
    
    await ctx.send(embed=embed)
@help.command()
async def myinfo(ctx):
    embed = discord.Embed(
        title=f"myinfo Command",
        description ="Use +myinfo to view your discord server information"
    )
    await ctx.send(embed=embed)

@help.command()
async def viewinfo(ctx):
    embed = discord.Embed(
        title=f"viewinfo Command",
        description ="Use +viewinfo <@username> in order to view other people's information"
    )
    await ctx.send(embed=embed)
@help.command()
async def mybank(ctx):
    embed = discord.Embed(
        title=f"mybank Command",
        description ="Use +mybank to view how much money you have"
    )
    await ctx.send(embed=embed)

@help.command()
async def viewbank(ctx):
    embed = discord.Embed(
        title=f"viewbank Command",
        description ="Use +viewbank <@username> to view how much someone has"
    )
    await ctx.send(embed=embed)

@help.command()
async def serverbank(ctx):
    embed = discord.Embed(
        title=f"serverbank Command",
        description ="Use +serverbank to view the server's economy"
    )
    await ctx.send(embed=embed)

@help.command()
async def payday(ctx):
    embed = discord.Embed(
        title=f"payday Command",
        description ="Use +payday to receive a paycheck (Note: you acn only use this command every hour and paycheck is determined based off your level)"
    )
    await ctx.send(embed=embed)

@help.command()
async def steal(ctx):
    embed = discord.Embed(
        title=f"steal Command",
        description ="Use +steal <@username> to attempt to steal from someone (Note: you can only use this command every 5 minutes and if failed you will receive a fine)"
    )
    await ctx.send(embed=embed)

@help.command()
async def crypto(ctx):
    embed = discord.Embed(
        title=f"crypto Command",
        description ="Use +crypto <cryptosymbol> to view live crypto data if you wanted to view Bitcoin's crypto you would do +crypto BTC"
    )
    await ctx.send(embed=embed)

@help.command()
async def mycrypto(ctx):
    embed = discord.Embed(
        title=f"mycrypto Command",
        description ="Use +mycrypto <page number> to view your crypto owned Ex: +mycrypto 1"

    )
    await ctx.send(embed=embed)

@help.command()
async def buycrypto(ctx):
    embed = discord.Embed(
        title=f"buycrypto Command",
        description ="Use +buycrypto <cryptosymbol> <amount> to buy crypto. If you wanted to buy 2 bitcoin you would do +buycrypto BTC 2"
    )
    await ctx.send(embed=embed)

@help.command()
async def sellcrypto(ctx):
    embed = discord.Embed(
        title=f"sellcrypto Command",
        description = "Use +sellcrypto <cryptosymbol> <amount> to sell crypto. If you wanted to buy 2 bitcoin you would do +sellcrypto BTC 2"
    )
    await ctx.send(embed=embed)


@help.command()
async def blackjack(ctx):
    embed = discord.Embed(
        title=f"blackjack Command",
        description = "Use +blackjack <betamount> to play blackjack if you wanted to bet $50 you would do +blackjack 50 (Note: if you win you double your money if you lose you lose it)"
    )
    await ctx.send(embed=embed)





    

@bot.command()
async def myinfo(ctx):
    user = ctx.author
    username = ctx.author.name
    server = ctx.guild.id
    fetch_lvl = await bot.pg_con.fetch("SELECT level FROM user_info WHERE user_id = $1 AND guild_id = $2", str(user.id), str(server))
    level = fetch_lvl[0]['level']

    
    

    dateformat = "%b %d, %Y @ %I:%M %p" 
    embed = discord.Embed(
        title = f"{username}'s info",
        color = discord.Color.purple()
    )

    embed.add_field(name="Level 🔢", value = str(level))
    embed.add_field(name="Joined Discord 🚌", value = ctx.author.created_at.strftime(dateformat))
    embed.add_field(name="Joined Server 🚎", value = ctx.author.joined_at.strftime(dateformat))
    embed.set_thumbnail(url=user.avatar_url)

    await ctx.send(embed=embed)

@bot.command()
async def viewinfo(ctx, member: discord.Member):
    user = member
    username = member.display_name
    server = member.guild.id

    fetch_lvl = await bot.pg_con.fetch("SELECT level FROM user_info WHERE user_id = $1 AND guild_id = $2", str(user.id), str(server))
    level = fetch_lvl[0]['level']

    
    

    dateformat = "%b %d, %Y @ %I:%M %p" 
    embed = discord.Embed(
        title = f"{username}'s info",
        color = discord.Color.purple()
    )

    embed.add_field(name="Level 🔢", value = str(level))
    embed.add_field(name="Joined Discord 🚌", value = member.created_at.strftime(dateformat))
    embed.add_field(name="Joined Server 🚎", value = member.joined_at.strftime(dateformat))
    embed.set_thumbnail(url=user.avatar_url)

    await ctx.send(embed=embed)


    

    

bot.loop.run_until_complete(create_db_pool())

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')


bot.run('INSERT BOTS TOKEN HERE')