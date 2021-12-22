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




class economy(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    @commands.command()
    async def mybank(self,ctx):
        author_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
        money = await self.bot.pg_con.fetch("SELECT money FROM user_info WHERE user_id = $1 AND guild_id = $2", author_id, guild_id)
        embed = discord.Embed(
            title = f"{ctx.author.name}'s Bank"
            
            
        )
        moneyInt = float(money[0]['money'])
        embed.add_field(name="Balance: ", value=  f'{"${:,.2f}".format(moneyInt)}')
        await ctx.send(embed=embed)

    @commands.command()
    async def viewbank(self,ctx, user:discord.Member):
        author_id = str(user.id)
        guild_id = str(user.guild.id)
        money = await self.bot.pg_con.fetch("SELECT money FROM user_info WHERE user_id = $1 AND guild_id = $2", author_id, guild_id)
        

        embed = discord.Embed(
            title = f"{user.name}'s Bank"
            
            
        )
        moneyfloat = float(money[0]['money'])
        embed.add_field(name="Balance: ", value=  f'{"${:,.2f}".format(moneyfloat)}')
        await ctx.send(embed=embed)

    @commands.command()
    @has_permissions(administrator=True)
    async def admingivemoney(self, ctx, user: discord.Member, *, amount):
        receiver_id = str(user.id)
        receiver_guild_id = str(user.guild.id)
        current_money = await self.bot.pg_con.fetch("SELECT money FROM user_info WHERE user_id = $1 AND guild_id = $2", receiver_id, receiver_guild_id)
        
        
        
        if(int(amount) > 999999999):
        
            await ctx.send("You cannot give this amount of money")
        
        else:
        
            new_moneyFloat = float(current_money[0]['money']) + float(amount)
            await self.bot.pg_con.execute("UPDATE user_info SET money = $1 WHERE user_id = $2 AND guild_id = $3", str(new_moneyFloat), receiver_id, receiver_guild_id)

            await ctx.send(f"{ctx.author.name} gave {user.name} ${amount}")
        

        
    
    @commands.command()
    @has_permissions(administrator=True)
    async def adminremovemoney(self, ctx, user: discord.Member, *, amount):
        receiver_id = str(user.id)
        receiver_guild_id = str(user.guild.id)
        current_money = await self.bot.pg_con.fetch("SELECT money FROM user_info WHERE user_id = $1 AND guild_id = $2", receiver_id, receiver_guild_id)
        
        new_moneyFloat = float(current_money[0]['money']) - float(amount)

        if(new_moneyFloat < 0.0):
            await ctx.send("This person does not have this much money to take!")

        else:
            await self.bot.pg_con.execute("UPDATE user_info SET money = $1 WHERE user_id = $2 AND guild_id = $3", str(new_moneyFloat), receiver_id, receiver_guild_id)

            await ctx.send(f"{ctx.author.name} removed ${amount} from {user.name}")

    

    @commands.command()
    @commands.cooldown(1, 3600, commands.BucketType.member)
    async def payday(self, ctx):
        author_id=str(ctx.author.id)
        guild_id=str(ctx.guild.id)
        level_fetch = await self.bot.pg_con.fetch("SELECT level FROM user_info WHERE user_id = $1 AND guild_id = $2", author_id, guild_id)
        level = int(level_fetch[0]['level'])
      

        salary = (10000) + (level*10000)
      

        old_moneyFetch = await self.bot.pg_con.fetch("SELECT money FROM user_info WHERE user_id = $1 AND guild_id = $2", author_id, guild_id)
        old_money = float(old_moneyFetch[0]['money'])
       
        new_money = float(salary) + old_money
       

        await self.bot.pg_con.execute("UPDATE user_info SET money = $1 WHERE user_id = $2 AND guild_id = $3", str(new_money), author_id, guild_id)

        await ctx.send(f"You got paid ${salary}")

    @commands.command()
    @commands.cooldown(1, 500, commands.BucketType.user)
    async def steal(self, ctx, user: discord.Member):
        random_int = random.randint(1,100)
        robber_id = str(ctx.author.id)
        robber_guild_id = str(ctx.guild.id)
        victim_id = str(user.id)
        victim_guild_id = str(user.guild.id)
        fetch_current_victim_money = await self.bot.pg_con.fetch("SELECT money FROM user_info WHERE user_id = $1 AND guild_id = $2", victim_id, victim_guild_id)
        current_victim_money = float(fetch_current_victim_money[0]['money'])

        fetch_current_robber_money = await self.bot.pg_con.fetch("SELECT money FROM user_info WHERE user_id = $1 AND guild_id = $2", robber_id, robber_guild_id)
        current_robber_money = float(fetch_current_robber_money[0]['money'])


        lucky_number = 75
        one_HundredDollarRange = range(75,101) #1/4 chance to steal
        five_HundredDollarRange = range(75, 86) #1/10 chance to steal
        one_thousandDollarRange = lucky_number #1/100 chance to steal



        if(current_victim_money < 5000.00):
            await ctx.send("He is too broke for you to steal. Come on man")
        else:
            if(random_int == lucky_number):
                victim_newMoney = current_victim_money - 1000.00
                robber_newMoney = current_robber_money + 1000.00
                await self.bot.pg_con.execute("UPDATE user_info SET money = $1 WHERE user_id = $2 AND guild_id = $3", str(victim_newMoney), victim_id, victim_guild_id)
                await self.bot.pg_con.execute("UPDATE user_info SET money = $1 WHERE user_id = $2 AND guild_id = $3", str(robber_newMoney), robber_id, robber_guild_id)
                await ctx.send(f"{ctx.author.name} stole $1000 from {user.name}")

            elif(random_int in five_HundredDollarRange):
                victim_newMoney = current_victim_money - 500.00
                robber_newMoney = current_robber_money + 500.00
                await self.bot.pg_con.execute("UPDATE user_info SET money = $1 WHERE user_id = $2 AND guild_id = $3", str(victim_newMoney), victim_id, victim_guild_id)
                await self.bot.pg_con.execute("UPDATE user_info SET money = $1 WHERE user_id = $2 AND guild_id = $3", str(robber_newMoney), robber_id, robber_guild_id)
                await ctx.send(f"{ctx.author.name} stole $500 from {user.name}")

            elif(random_int in one_HundredDollarRange):
                victim_newMoney = current_victim_money - 100.00
                robber_newMoney = current_robber_money + 100.00
                await self.bot.pg_con.execute("UPDATE user_info SET money = $1 WHERE user_id = $2 AND guild_id = $3", str(victim_newMoney), victim_id, victim_guild_id)
                await self.bot.pg_con.execute("UPDATE user_info SET money = $1 WHERE user_id = $2 AND guild_id = $3", str(robber_newMoney), robber_id, robber_guild_id)
                await ctx.send(f"{ctx.author.name} stole $100 from {user.name}")

            else:
                
                
                robber_newMoney = current_robber_money - 1000.00
                if(robber_newMoney < 0):
                    await self.bot.pg_con.execute("UPDATE user_info SET money = $1 WHERE user_id = $2 AND guild_id = $3", '0.00', robber_id, robber_guild_id)
                    await ctx.send(f"{ctx.author.name} received a $1000 fine and went bankrupt cause of it! Make better choices!")

                else:
                    await self.bot.pg_con.execute("UPDATE user_info SET money = $1 WHERE user_id = $2 AND guild_id = $3", str(robber_newMoney), robber_id, robber_guild_id)
                    await ctx.send(f"{ctx.author.name} got caught and received a 1000$ fine")

    

def setup(bot):
    bot.add_cog(economy(bot))