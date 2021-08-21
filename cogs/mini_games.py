import discord

from discord_components import Button, ButtonStyle, InteractionType
from discord.ext import commands
from random import randint


class MiniGames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="highlow")
    @commands.has_role(868589512354332793)
    #@commands.cooldown(rate=1, per=45, type=commands.BucketType.user)
    async def high_low(self, ctx, *, amount: int):
        '''High Low minigame''' 

        user_gold = (await self.bot.db.fetchrow("SELECT gold FROM user_info WHERE id = $1", ctx.author.id))["gold"]
        
        #Check if user has enough gold
        if amount > user_gold:
            await ctx.send(f"{ctx.author.mention} You can't bet more than what you have", delete_after=10)
            await ctx.message.delete(delay=10)
            return
        elif amount <= 0:
            await ctx.send(f"{ctx.author.mention} You need to bet some amount", delete_after=10)
            await ctx.message.delete(delay=10)
            return

        number = randint(1, 100)
        position = randint(1, 100)

        embed = discord.Embed(
            title="High Low!", 
            description=f"We have number between 1 and 100. Is the number higher, lower, or exact to **{position}**?")
        
        components=[
                Button(style=ButtonStyle.green, label= "HIGHER"), 
                Button(style=ButtonStyle.red, label="LOWER"), 
                Button(style=ButtonStyle.gray, label="EXACT")
            ]   

        message = await ctx.send(embed=embed, components=[components])

        response = await self.bot.wait_for("button_click", timeout=15, check=lambda i: i.author.id == ctx.author.id)

        #Correct answer
        if number < position:
            answer = "LOWER"
        elif number > position:
            answer = "HIGHER"
        else:
            answer = "EXACT"
    
        #Check which option was chosen
        if response.component.label == answer:
            #Correct answer
            user_gold += amount*2
            embed = discord.Embed(title="You Won!", description=f"The number was {number}. You won {amount*2} :coin:", color=discord.Color.green())
        else:
            #Incorrect answer
            user_gold -= amount
            embed = discord.Embed(title="You Lost!", description=f"The number was {number}. You lost {amount} :coin:", color=discord.Color.red())

        await self.bot.db.execute("UPDATE user_info SET gold = $1 WHERE id = $2", user_gold, ctx.author.id)
        await message.edit(embed=embed, components=[])


def setup(bot):
    bot.add_cog(MiniGames(bot))