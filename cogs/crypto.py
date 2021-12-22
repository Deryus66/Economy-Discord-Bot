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


# #API To Track Crypto (Must call locally inside function commands in order to fetch live feed each time command is called)
# URL = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd'
# cryptoRequest = requests.get(url=URL)
# cryptoData = cryptoRequest.json()

class crypto(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    


    @commands.command()
    
    async def crypto(self, ctx, *, Crypto):

        URL = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd'
        cryptoRequest = requests.get(url=URL)
        cryptoData = cryptoRequest.json()
        
        cryptoName = None
        cryptoPrice = None
        cryptoimageUrl = None
        cryptoSymbol = None
        cryptoPriceChange = None
        cryptoMarketCap = None
        cryptoMarketCapChange = None
        cryptoSupply = None
        for i in range(len(cryptoData)):
            if((cryptoData[i]['symbol'].lower()) == Crypto.lower()):
                cryptoName = cryptoData[i]['name']
                cryptoPrice = cryptoData[i]['current_price']
                cryptoimageUrl = cryptoData[i]['image']
                cryptoSymbol = cryptoData[i]['symbol']
                cryptoPriceChange = cryptoData[i]['price_change_24h']
                cryptoMarketCap = cryptoData[i]['market_cap']
                cryptoMarketCapChange = cryptoData[i]['market_cap_change_percentage_24h']
                cryptoSupply = cryptoData[i]['circulating_supply']
                
                

        
        embed = discord.Embed(
            title = f"{cryptoName} Info",
            color = discord.Color.dark_magenta()
        )
        
        if(float(cryptoPrice) < 0.01):
            decimalPrice = str("{:.16f}".format(float(cryptoPrice))).strip('0')
            
            embed.add_field(name="Current Price 💰", value=f"$0{decimalPrice}")
        else:
            embed.add_field(name="Current Price 💰", value="${:,}".format(cryptoPrice))

        if(abs(float(cryptoPriceChange)) < 0.01):
            decimalPrice = str("{:.16f}".format(float(cryptoPriceChange))).strip('0')
            
            embed.add_field(name="Price Change 24hr 📈", value=f"${decimalPrice}")
        else:
            embed.add_field(name="Price Change 24hr 📈", value="${:,}".format(cryptoPriceChange))

        
        embed.add_field(name="Market Cap 🧢", value="${:,}".format(cryptoMarketCap))
        embed.add_field(name="Market Cap Change 24hr 📉", value="{:,}%".format(cryptoMarketCapChange))

        embed.add_field(name="Circulating-Supply 🚚", value="${:,}".format(cryptoSupply))
        embed.set_thumbnail(url=cryptoimageUrl)

        await ctx.send(embed=embed)
    
    
    @commands.command()
    
    async def mycrypto(self, ctx, *, pageNumber):
        URL = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd'
        cryptoRequest = requests.get(url=URL)
        cryptoData = cryptoRequest.json()
        user_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
        user_name = str(ctx.author)
        
        crypto_profile = await self.bot.pg_con.fetch("SELECT * FROM crypto_profiles WHERE user_id = $1 AND guild_id = $2", user_id, guild_id)
        
        
        if not crypto_profile:
            emptyList = []
            await self.bot.pg_con.execute("INSERT into crypto_profiles(user_id, guild_id, user_name, crypto_names, crypto_symbols, crypto_amount, crypto_balance) VALUES ($1, $2, $3, $4, $5, $6, $7)", user_id, guild_id, user_name, emptyList, emptyList, emptyList, emptyList)
            await ctx.send("You have no crypto")
        else:

            cryptoNameList = crypto_profile[0]['crypto_names']
            cryptoAmountList = crypto_profile[0]['crypto_amount']
            cryptoSymbolList = crypto_profile[0]['crypto_symbols']
            previousPriceList = crypto_profile[0]['crypto_balance']
            
            num_of_Pages = len(cryptoNameList)

            
            if(int(pageNumber) < 0):
                embed1001 = discord.Embed(
                    title="ERROR ❌",
                    description="Page number can't be negative"
                )
                await ctx.send(embed=embed1001)

            elif(int(pageNumber) > num_of_Pages):
                embed100 = discord.Embed(
                    title="ERROR ❌",
                    description="Page number does not exist"
                )
                await ctx.send(embed=embed100)
            else:

                
                index = int(pageNumber) - 1

                cryptoNewPrice = 0 
                cryptoAvatarUrl = ""
                for i in range(len(cryptoData)):
                    if((cryptoData[i]['symbol']).lower() == cryptoSymbolList[index]):
                        cryptoNewPrice = float(cryptoData[i]['current_price']) * float(cryptoAmountList[index])
                        cryptoAvatarUrl = cryptoData[i]['image']
                        

                
                Net_Profit = (float(cryptoNewPrice))  - float(previousPriceList[index])
                

                New_Balance = float(cryptoNewPrice) 

                if(Net_Profit >= 0.0):
                    embed = discord.Embed(
                    title = f"{ctx.author.name}'s Crypto 🪙 Pg: {pageNumber}/{num_of_Pages}",
                    color = discord.Color.teal()
                    )

                    embed.add_field(name="Crypto Name 📝", value=cryptoNameList[index])
                    embed.add_field(name="Amount 🔢", value=cryptoAmountList[index])
                    embed.add_field(name="Amount In USD 💵", value="${:,.2f}".format(New_Balance))
                    if(Net_Profit < 0.01 and Net_Profit != 0.0):
                        decimalPrice = str("{:.16f}".format(Net_Profit)).strip('0')
                        embed.add_field(name="Net Profit 📈", value=f"+0{decimalPrice}")
                    else:
                        embed.add_field(name="Net Profit 📈", value="+{:,.2f}".format(Net_Profit))

                    embed.set_thumbnail(url=cryptoAvatarUrl)
                else:
                    embed = discord.Embed(
                    title = f"{user_name}'s Crypto 🪙 Pg: {pageNumber}/{num_of_Pages}",
                    color = discord.Color.red()
                    )

                    embed.add_field(name="Crypto Name 📝", value=cryptoNameList[index])
                    embed.add_field(name="Amount 🔢", value=cryptoAmountList[index])
                    embed.add_field(name="Amount In USD 💵", value="${:,.2f}".format(New_Balance))
                    if(Net_Profit > 0.01):
                        decimalPrice = str("{:.16f}".format(Net_Profit)).strip('0')
                        embed.add_field(name="Net Profit 📉", value=f"0{decimalPrice}")
                    else:
                        embed.add_field(name="Net Profit 📉", value="{:,.2f}".format(Net_Profit))
                    embed.set_thumbnail(url=cryptoAvatarUrl)

                await ctx.send(embed=embed)

    @commands.command()
    async def buycrypto(self,ctx, Crypto, *, amount):
        URL = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd'
        cryptoRequest = requests.get(url=URL)
        cryptoData = cryptoRequest.json()
        user_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
        user_name = str(ctx.author)
        cryptoPrice = None
        cryptoFound = False
        cryptoName = None
        cryptoSymbol = None
        
    
        current_balanceList = await self.bot.pg_con.fetch("SELECT money FROM user_info WHERE user_id = $1 AND guild_id = $2", user_id, guild_id)
        
        current_balance = float(current_balanceList[0]['money'])
        
        for i in range(len(cryptoData)):
            if((cryptoData[i]['symbol'].lower()) == Crypto.lower()):
                cryptoPrice = cryptoData[i]['current_price']
                cryptoName = cryptoData[i]['name']
                cryptoSymbol = cryptoData[i]['symbol']
                
                cryptoFound = True

        
        if(cryptoFound == False):
            embed = discord.Embed(
                title="ERROR ❌",
                description=f'Crypto "{Crypto}" does not exist'
            )
            await ctx.send(embed=embed)
        elif(int(amount) < 0):
            embed527 = discord.Embed(
                title="ERROR ❌",
                description=f'You can not buy negative amounts!'
            )
            await ctx.send(embed=embed527)

        else:
            
            amount_needed = float(cryptoPrice) * float(amount)

            amountneededFormat = "${:,.2f}".format(amount_needed)

            
            
            if(float(current_balance) < (float(amount_needed))):

                embed2 = discord.Embed(
                title="ERROR ❌",
                description=f"You need {amountneededFormat} to buy {amount} {cryptoName}"
                )
                await ctx.send(embed=embed2)
                
            else:
                
                
                currentCrypto = await self.bot.pg_con.fetch("SELECT * FROM crypto_profiles WHERE user_id = $1 AND guild_id = $2", user_id, guild_id)
                
                if not currentCrypto:
                    embed3 = discord.Embed(
                    title="ERROR ❌",
                    description=f"Try again!"
                    )
                    await ctx.send(embed=embed3)
                    emptyList = []
                    await self.bot.pg_con.execute("INSERT into crypto_profiles(user_id, guild_id, user_name, crypto_names, crypto_symbols, crypto_amount, crypto_balance) VALUES ($1, $2, $3, $4, $5, $6, $7)", user_id, guild_id, user_name, emptyList, emptyList, emptyList, emptyList)
                else:
                    embed4 = discord.Embed(
                    title="Crypto Purchase 💰 ",
                    description=f"You just bought {amount} {cryptoName}"
                    )
                    await ctx.send(embed=embed4)
                    crypto_names = await self.bot.pg_con.fetch("SELECT crypto_names FROM crypto_profiles WHERE user_id = $1 AND guild_id = $2", user_id, guild_id)
                    crypto_symbols = await self.bot.pg_con.fetch("SELECT crypto_symbols FROM crypto_profiles WHERE user_id = $1 AND guild_id = $2", user_id, guild_id)
                    price_bought = await self.bot.pg_con.fetch("SELECT crypto_balance FROM crypto_profiles WHERE user_id = $1 AND guild_id = $2", user_id, guild_id)
                    crypto_amount= await self.bot.pg_con.fetch("SELECT crypto_amount FROM crypto_profiles WHERE user_id = $1 AND guild_id = $2", user_id, guild_id)

                    crypto_namesList = []
                    crypto_symbolsList = []
                    price_boughtList = []
                    crypto_amountList = []

                    cryptoAlreadyBought = False
                    cryptoIndex = 0
                    index = 0
                    for name in crypto_names[0]['crypto_names']:
                        if(cryptoName == crypto_names[0]['crypto_names'][index]):
                            cryptoAlreadyBought = True
                            
                            cryptoIndex = index
                        
                        crypto_namesList.append(name)

                        index = index + 1
                    
                    for symbols in crypto_symbols[0]['crypto_symbols']:
                        crypto_symbolsList.append(symbols)

                    for prices in price_bought[0]['crypto_balance']:
                        price_boughtList.append(prices)

                    for amounts in crypto_amount[0]['crypto_amount']:
                        crypto_amountList.append(amounts)

                    
                    
                    if(cryptoAlreadyBought == False):
                        
                    
                    
                        crypto_namesList.append(cryptoName)
                        
                        crypto_symbolsList.append(cryptoSymbol)
                        
                        price_boughtList.append(str(amount_needed))
                        crypto_amountList.append(int(amount))
                        
                        await self.bot.pg_con.execute("UPDATE crypto_profiles SET crypto_names = $1 WHERE user_id = $2 AND guild_id = $3", crypto_namesList, user_id, guild_id)
                        await self.bot.pg_con.execute("UPDATE crypto_profiles SET crypto_symbols = $1 WHERE user_id = $2 AND guild_id = $3", crypto_symbolsList, user_id, guild_id)
                        await self.bot.pg_con.execute("UPDATE crypto_profiles SET crypto_balance = $1 WHERE user_id = $2 AND guild_id = $3", price_boughtList, user_id, guild_id)
                        await self.bot.pg_con.execute("UPDATE crypto_profiles SET crypto_amount = $1 WHERE user_id = $2 AND guild_id = $3", crypto_amountList, user_id, guild_id)
                    

                    else:
                        
                        
                        new_amount = int(crypto_amount[0]['crypto_amount'][cryptoIndex]) + int(amount)
                        new_priceBought = float(price_bought[0]['crypto_balance'][cryptoIndex]) + float(amount_needed)  
                        

                        
                        crypto_amountList[cryptoIndex] = new_amount
                        

                        price_boughtList[cryptoIndex] = str(new_priceBought)
                        

                    

                        


                        await self.bot.pg_con.execute("UPDATE crypto_profiles SET crypto_amount = $1 WHERE user_id = $2 and guild_id = $3", crypto_amountList, user_id, guild_id)
                        await self.bot.pg_con.execute("UPDATE crypto_profiles SET crypto_balance = $1 WHERE user_id = $2 and guild_id = $3", price_boughtList, user_id, guild_id)
                        
                        



                    new_amount = float(current_balance) - float(amount_needed)

                    await self.bot.pg_con.execute("UPDATE user_info SET money = $1 WHERE user_id = $2 AND guild_id = $3", str(new_amount), user_id, guild_id)

   
   
    @commands.command()
    async def sellcrypto(self,ctx, Crypto, *, amount):
        URL = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd'
        cryptoRequest = requests.get(url=URL)
        cryptoData = cryptoRequest.json()

        user_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
        user_name = str(ctx.author)
        
        
    
        current_balanceList = await self.bot.pg_con.fetch("SELECT money FROM user_info WHERE user_id = $1 AND guild_id = $2", user_id, guild_id)
        
        current_balance = float(current_balanceList[0]['money'])

        currentCrypto = await self.bot.pg_con.fetch("SELECT * FROM crypto_profiles WHERE user_id = $1 AND guild_id = $2", user_id, guild_id)

        if not currentCrypto:
            embed1 = discord.Embed(
                        title ="ERROR ❌",
                        description=f"You have no crypto to sell!"
                        
                    )
            await ctx.send(embed=embed1)

        else:
            symbolList = currentCrypto[0]['crypto_symbols']
            nameList = currentCrypto[0]['crypto_names']
            amountList = currentCrypto[0]['crypto_amount']
            balanceBoughtAt = currentCrypto[0]['crypto_balance']
            
            
            symbolFound = False
            cryptoIndex = 0
            index = 0
            for symbols in symbolList:
                if (symbols.lower() == Crypto.lower()):
                    symbolFound = True
                    cryptoIndex = index

                index = index + 1
            
            
            if(symbolFound == False):
                embed2 = discord.Embed(
                        title ="ERROR ❌",
                        description=f"You do not own {Crypto}! Type $help to make sure your typing the command right!"
                        
                )
                
                await ctx.send(embed=embed2)
            else:

            
                if(int(amount) < 0):

                    embed9 = discord.Embed(
                        title ="ERROR ❌",
                        description="You can not sell negative amounts!"
                        
                    )
                    await ctx.send(embed=embed9)
                elif(int(amount) > int(amountList[cryptoIndex])):

                    embed12 = discord.Embed(
                        title ="ERROR ❌",
                        description=f"You do not have {amount} {nameList[cryptoIndex]}"
                        
                    )

                    await ctx.send(embed=embed12)

                
                
                elif(int(amount) == int(amountList[cryptoIndex])):
                    
                    current_CryptoPrice = 0
                    for i in range(len(cryptoData)):
                        if((cryptoData[i]['symbol'].lower()) == Crypto.lower()):
                            current_CryptoPrice = cryptoData[i]['current_price']
                    
                    amount_withdraw = float(current_CryptoPrice) * float(amountList[cryptoIndex])
                    
                    
                    symbolList.pop(cryptoIndex)
                    nameList.pop(cryptoIndex)
                    amountList.pop(cryptoIndex)
                    balanceBoughtAt.pop(cryptoIndex)
                    
                    

                    await self.bot.pg_con.execute("UPDATE crypto_profiles SET crypto_names = $1 WHERE user_id = $2 AND guild_id = $3", nameList, user_id, guild_id)
                    
                    await self.bot.pg_con.execute("UPDATE crypto_profiles SET crypto_symbols = $1 WHERE user_id = $2 AND guild_id = $3", symbolList, user_id, guild_id)
                    await self.bot.pg_con.execute("UPDATE crypto_profiles SET crypto_amount = $1 WHERE user_id = $2 AND guild_id = $3", amountList, user_id, guild_id)
                    await self.bot.pg_con.execute("UPDATE crypto_profiles SET crypto_balance = $1 WHERE user_id = $2 AND guild_id = $3", balanceBoughtAt, user_id, guild_id)

                    new_money = current_balance + amount_withdraw
                    withdrawDisplay = "${:,.2f}".format(amount_withdraw)
                    embed = discord.Embed(
                        title ="Crypto Sale 💰 ",
                        description=f"{ctx.author.name} sold {amount} {Crypto} for {withdrawDisplay}"
                        
                    )
                    
                    
                    await self.bot.pg_con.execute("UPDATE user_info SET money = $1 WHERE user_id = $2 AND guild_id = $3", str(new_money), user_id, guild_id)
                    
                    await ctx.send(embed=embed)
                    
                elif (int(amount) < int(amountList[cryptoIndex])):
                
                    current_CryptoPrice = 0
                    for i in range(len(cryptoData)):
                        if((cryptoData[i]['symbol'].lower()) == Crypto.lower()):
                            current_CryptoPrice = cryptoData[i]['current_price']

                    
                    
                    
                    amount_withdraw = float(current_CryptoPrice) * float(amount)
                    
                    new_amount = int(amountList[cryptoIndex]) - int(amount)

                    
                    
                    amountList[cryptoIndex] = new_amount
                    currentbalanceboughtat = float(balanceBoughtAt[cryptoIndex])
                    balanceBoughtAt[cryptoIndex] = str(currentbalanceboughtat -  float(amount_withdraw))

                

                
                    
                    
                    await self.bot.pg_con.execute("UPDATE crypto_profiles SET crypto_amount = $1 WHERE user_id = $2 AND guild_id = $3", amountList, user_id, guild_id)
                    await self.bot.pg_con.execute("UPDATE crypto_profiles SET crypto_balance = $1 WHERE user_id = $2 AND guild_id = $3", balanceBoughtAt, user_id, guild_id)
                    
                    new_money = current_balance + amount_withdraw
                    withdrawDisplay = "${:,.2f}".format(amount_withdraw)
                    embed5 = discord.Embed(
                        title ="Crypto Sale 💰 ",
                        description=f"{ctx.author.name} sold {amount} {Crypto} for {withdrawDisplay}"
                        
                    )
                    
                    
                    await self.bot.pg_con.execute("UPDATE user_info SET money = $1 WHERE user_id = $2 AND guild_id = $3", str(new_money), user_id, guild_id)

                    await ctx.send(embed=embed5)
                

def setup(bot):
    bot.add_cog(crypto(bot))