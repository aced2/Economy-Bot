import asyncio

from discord.ext import commands


class ErrorHandling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error: commands.CommandError):
        "Global error handler"

        print(f"Error: {error} Raised By: {ctx.command}")
        
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(f"{ctx.author.mention} Please enter a valid command.", delete_after=10)
            await ctx.message.delete(delay=10)

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"{ctx.author.mention} Please input correct arguments.", delete_after=10)
            await ctx.message.delete(delay=10)
        
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"{ctx.author.mention} This command is on cooldown. Please wait {round(error.retry_after)} seconds.", delete_after=10)
            await ctx.message.delete(delay=10)
        
        if isinstance(error, commands.MissingRole):
            if ctx.author.guild.get_role(error.missing_role).name == "Class Selected":
                await ctx.send(f"{ctx.author.mention} You have not selected a Class yet. Please use $select to select a Class or $classes for more info.", delete_after=10)
                await ctx.message.delete(delay=10)
        
        if isinstance(error, commands.MemberNotFound):
            await ctx.send(f"{ctx.author.mention} There is no user {error.argument}. Please input a valid user.", delete_after=10)
            await ctx.message.delete(delay=10)
        
        if isinstance(error, commands.CommandInvokeError):
            print(error.original, type(error.original))
            if isinstance(error.original, asyncio.TimeoutError):
                if ctx.command.name == "button":
                    await ctx.send(f"{ctx.author.mention} You did not select an option. Buttons are now inactive.")

        if isinstance(error, commands.NotOwner):
            await ctx.send(f"{ctx.author.mention} Only the owner can use this command.", delete_after=10)
            await ctx.message.delete(delay=10)

        if isinstance(error, commands.UserNotFound):
            await ctx.send(f"{ctx.author.mention} User not found.", delete_after=10)
            await ctx.message.delete(delay=10)

def setup(bot):
    bot.add_cog(ErrorHandling(bot))