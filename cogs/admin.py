import discord

from discord.ext import commands


class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    @commands.is_owner()
    async def kick(self, ctx, user: discord.User):
        '''Kick user and remove from database'''
        
        await ctx.guild.kick(user)
        await ctx.send(f"{user.name} has been kicked.")


def setup(bot):
    bot.add_cog(AdminCommands(bot))