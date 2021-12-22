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




class bank(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def serverbank(self, ctx):
        guild_id = str(ctx.guild.id)
       
        money = await self.bot.pg_con.fetch("SELECT server_balance FROM server_banks WHERE guild_id = $1", guild_id)
        await ctx.send("Test2")
        embed = discord.Embed(
            title ="Server Bank Balance",
            description= "This is the server's economy"
        )
        
        moneyFloat = float(money[0]['server_balance'])
        
        embed.add_field(name="Balance: ", value=  f'{"${:,.2f}".format(moneyFloat)}')
        await ctx.send(embed=embed)

    

 
def setup(bot):
    bot.add_cog(bank(bot))