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

class Card(object):
    def __init__(self, suit, val):
        self.suit = suit
        self.value = val

    def show(self):
        return f"{self.suit} {self.value}"

class Deck(object):
    def __init__(self):
        self.cards = []
        self.build() #builds our deck in order
        

    def build(self):
        
        for suit in ["♦️", "♥️", "♠️", "♣️"]:
            for value in range(2, 15):
                if(value == 11):
                    value = 'J'
                elif(value == 12):
                    value = 'Q'
                elif(value == 13):
                    value = 'K'
                elif(value == 14):
                    value = 'A'


                self.cards.append(Card(suit, value))

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self):
        return self.cards.pop()
class blackjackPlayer(object):
    def __init__(self):
        self.hand = []

    def draw(self, deck):
        self.hand.append(deck.draw())



    
            
 
        

class games(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    

    
    
    @commands.command()
    async def blackjack(self, ctx, bet):
      

        author_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
       
        money = await self.bot.pg_con.fetch("SELECT money FROM user_info WHERE user_id = $1 AND guild_id = $2", author_id, guild_id)
        
        money_float = float(money[0]['money'])
        winmoney = float(bet) + money_float
        losemoney = money_float - float(bet)
    
        if(float(bet) < 0):
            embed = discord.Embed(
                title="ERROR ❌",
                description="You can not bet negative amounts"
            )
            await ctx.send(embed=embed)

        elif(money_float < float(bet)):
            embed = discord.Embed(
                title="ERROR ❌",
                description=f"You do not have ${bet}"
            )
            await ctx.send(embed=embed)

        else:
            def check(reaction, user):
                return user == ctx.author and (str(reaction) == '✅' or str(reaction) == '❌')
            
            embed = discord.Embed(
                title =f"{ctx.author.name}'s Blackjack ♦️ ♥️ ♠️ ♣️",
                description = "Here is your deck"
                
            )
            deck = Deck()
            deck.shuffle()
            player1 = blackjackPlayer() #TheUser's Hand
            player2 = blackjackPlayer() #TheBot's Hand
            player1.draw(deck)
            player1.draw(deck)
            player2.draw(deck)
            player2.draw(deck)

            

            starting_hand = []
            for cards in player1.hand:
                cardshow = cards.show()
                starting_hand.append(str(cardshow))

            
                
            embed.add_field(name="Deck:", value=str(starting_hand))
            
        
            message = await ctx.send(embed=embed)
            await message.add_reaction('✅')
            await message.add_reaction('❌')
            isBust = False
            while(isBust == False):
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout = 60.0, check = check)

                    if (str(reaction) == '✅'):
                        player1.draw(deck)
                        new_hand = []
                        for cards in player1.hand:
                            cardshow = cards.show()

                            new_hand.append(str(cardshow))
                        

                        embed2 = discord.Embed(
                            title =f"{ctx.author.name}'s Blackjack ♦️ ♥️ ♠️ ♣️",
                            description = "Here is your deck"
                        )
                        embed2.add_field(name="Deck:", value = new_hand)

                        

                        totalValue = 0
                        aceExist = False
                        numOfAces = 0
                        i = 0
                        for cards in new_hand:
                            index = new_hand[i]
                            index_value = 0
                            if(index[-1] == '0' and index[-2] == '1'):
                                index_value = 10
                            elif(index[-1] == 'J' or index[-1] == 'Q' or index[-1] == 'K' ):
                                index_value = 10
                            elif(index[-1] == 'A'):
                                index_value = 11
                                aceExist = True
                                numOfAces = numOfAces + 1
                            else:
                                index_value = int(index[-1])

                            totalValue = totalValue + index_value
                            i = i + 1

                    

                        bustEmbed = discord.Embed(
                            title="BUST!",
                            description="You went over 21"
                        )
                        
                        if(totalValue > 21):
                            if(aceExist == True):
                                totalValue = totalValue - 10
                                if(numOfAces >= 2):
                                    totalValue = totalValue - ((numOfAces - 1) * 10)
                                if(totalValue > 21):
                                    
                                    bustEmbed.add_field(name="Deck", value=new_hand)
                                    await ctx.send(embed=bustEmbed)
                                    await self.bot.pg_con.execute("UPDATE user_info SET money = $1 WHERE user_id = $2 AND guild_id = $3", str(losemoney), author_id, guild_id)
                                    isBust = True
                                else:

                                    message2 = await ctx.send(embed=embed2)
                                    await message2.add_reaction('✅')
                                    await message2.add_reaction('❌')

                            else:

                                bustEmbed.add_field(name="Deck", value=new_hand)
                                await ctx.send(embed=bustEmbed)
                                await self.bot.pg_con.execute("UPDATE user_info SET money = $1 WHERE user_id = $2 AND guild_id = $3", str(losemoney), author_id, guild_id)
                                isBust = True

                        else:
                            message2 = await ctx.send(embed=embed2)
                            await message2.add_reaction('✅')
                            await message2.add_reaction('❌')

                        


                        
                        
                        
                    elif(str(reaction)== '❌'):
                        bots_hand = []
                        for cards in player2.hand:
                            cardshow = cards.show()
                            bots_hand.append(str(cardshow))


                        players_hand = []
                        
                        for cards in player1.hand:
                            cardshow = cards.show()
                            players_hand.append(str(cardshow))

                        
                        #Calculates the Player's Cards added up
                        playerValue = 0
                        i = 0
                        aceExist = False
                        numOfAces = 0
                        for cards in players_hand:
                            index = players_hand[i]
                            index_value = 0
                            if(index[-1] == '0' and index[-2] == '1'):
                                index_value = 10
                            elif(index[-1] == 'J' or index[-1] == 'Q' or index[-1] == 'K' ):
                                index_value = 10
                            elif(index[-1] == 'A'):
                                index_value = 11
                                aceExist = True
                                numOfAces = numOfAces + 1
                                
                            else:
                                index_value = int(index[-1])

                            playerValue = playerValue + index_value
                            i = i + 1


                        botsValue = 0
                        numOfBotAces = 0
                        j = 0
                        for cards in bots_hand:
                            index = bots_hand[j]
                            index_value = 0
                            if(index[-1] == '0' and index[-2] == '1'):
                                index_value = 10

                            elif(index[-1] == 'J' or index[-1] == 'Q' or index[-1] == 'K' ):
                                index_value = 10
                            elif(index[-1] == 'A'):
                                index_value = 11
                                numOfBotAces = numOfBotAces + 1
                                
                            else:
                                index_value = int(index[-1])

                            botsValue = botsValue + index_value
                            j = j + 1
                        if(playerValue > 21):
                            if(numOfAces == 1):
                                playerValue = playerValue - (numOfAces * 10)
                            else:
                                playerValue = playerValue - ((numOfAces-1) * 10)

                        if(numOfBotAces == 2):
                            botsValue = 12 #If bot has two aces one counts as 11 one counts as 1
                        if(botsValue > playerValue):
                            loseEmbed = discord.Embed(
                                title=f"{ctx.author.name} Lost!",
                                
                            )
                            loseEmbed.add_field(name="House's Hand: ", value=bots_hand)
                            loseEmbed.add_field(name="Your Hand: ", value=players_hand)
                            await ctx.send(embed=loseEmbed)
                            await self.bot.pg_con.execute("UPDATE user_info SET money = $1 WHERE user_id = $2 AND guild_id = $3", str(losemoney), author_id, guild_id)
                        elif(playerValue > botsValue):
                            winEmbed = discord.Embed(
                                title=f"{ctx.author.name} Won!",
                                
                            )
                            winEmbed.add_field(name="House's Hand: ", value=bots_hand)
                            winEmbed.add_field(name="Your Hand: ", value=players_hand)
                            await ctx.send(embed=winEmbed)
                            await self.bot.pg_con.execute("UPDATE user_info SET money = $1 WHERE user_id = $2 AND guild_id = $3", str(winmoney), author_id, guild_id)
                        elif(playerValue == botsValue):
                            tieEmbed = discord.Embed(
                                title=f"{ctx.author.name} Tied, House Wins!",
                                
                            )
                            tieEmbed.add_field(name="House's Hand: ", value=bots_hand)
                            tieEmbed.add_field(name="Your Hand: ", value=players_hand)
                            await ctx.send(embed=tieEmbed)
                            await self.bot.pg_con.execute("UPDATE user_info SET money = $1 WHERE user_id = $2 AND guild_id = $3", str(losemoney), author_id, guild_id)

                        isBust = True


                except:
                    await message.delete()
                    isBust = True
        
            

                

                
                    

            

        


def setup(bot):
    bot.add_cog(games(bot))



