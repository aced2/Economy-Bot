import discord

from discord.utils import get
from discord.ext import tasks, commands
from datetime import datetime, timezone, timedelta
from discord_components import Button, ButtonStyle, InteractionType


class Game(commands.Cog):

    time_ = "night"
    classes_stats = {
        "warrior": {"atk": 5, "hp": 20, "armor": 5, "gold_per_hunt": {"low": 20, "high": 30}},
        "mage": {"atk": 11, "hp": 10, "armor": 0, "gold_per_hunt": {"low": 23, "high": 26}},
        "ninja": {"atk": 8, "hp": 12, "armor": 35, "gold_per_hunt": {"low": 25, "high": 25}},
        "werewolf": {"atk": 3, "hp": 30, "armor": 5, "gold_per_hunt": {"low": 20, "high": 30}},
        "vampire": {"atk": 9, "hp": 7, "armor": 4, "gold_per_hunt": {"low": 23, "high": 36}},
        "zombie": {"atk": 5, "hp": 10, "armor": 5, "gold_per_hunt": {"low": 25, "high": 25}}
    }

    def __init__(self, bot):
        self.bot = bot
        self.change_time.start()
    
    @tasks.loop(seconds=3600 * 6)
    async def change_time(self):
        '''Change Game time every 6 hours'''

        if Game.time_ == "day":
            Game.time_ = "night"
        else:
            Game.time_ = "day"
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        '''When user leaves server, remove them from database'''

        delete_query = "DELETE FROM user_info WHERE id = $1"
        await self.bot.db.execute(delete_query, member.id)
        print(f"NAME: {member.name} ID: {member.id} REMOVED FROM DATABASE")
    
    @commands.command()
    async def classes(self, ctx):
        '''Display information about the different Classes'''

        description = """
                    :crossed_swords: = Attack\n:heart: = HP\n:shield: = Armor\n:coin: = Gold per Hunt
                    \nDay -> Warrior, Mage, Ninja x2 Gold\nNight -> Werewolf, Vampire, Zombie x2 Gold
                    \nUse **$time** for more info
                    Use **$select class_name** to select a Class\n\u200b
                    """
        
        embed = discord.Embed(
            title="Classes", 
            color=discord.Color.default(),
            description=description
            )
        
        embed.add_field(name="Warrior :man_supervillain:", value=":crossed_swords: 5\n:heart: 20\n:shield: 5\n:coin: 20-30", inline=True)
        embed.add_field(name="Mage :man_mage:", value=":crossed_swords: 11\n:heart: 10\n:shield: 0\n:coin: 23-26", inline=True)
        embed.add_field(name="Ninja :ninja:", value=":crossed_swords: 8\n:heart: 12\n:shield: 3\n:coin: 25", inline=True)
        embed.add_field(name="Werewolf :wolf:", value=":crossed_swords: 3\n:heart: 30\n:shield: 5\n:coin: 20-30", inline=True)
        embed.add_field(name="Vampire :man_vampire:", value=":crossed_swords: 9\n:heart: 7\n:shield: 4\n:coin: 23-26", inline=True)
        embed.add_field(name="Zombie :man_zombie:", value=":crossed_swords: 5\n:heart: 10\n:shield: 5\n:coin: 25", inline=True)
        
        await ctx.send(embed=embed)

    @commands.command(name="time")
    async def display_time(self, ctx):
        '''Display information about time'''

        #Get game times
        if Game.time_ == "day":
            opposite_time = "night"
            extra_gold = "Warrior :man_supervillain: Mage :man_mage: Ninja :ninja:"
            time_emoji, opposite_emoji = ":sunny:", ":new_moon:"
        else:
            opposite_time = "day"
            extra_gold = "Werewolf :wolf: Vampire :man_vampire: Zombie :man_zombie:"
            time_emoji, opposite_emoji = ":new_moon:", ":sunny:"
        
        #Get time left until opposite time of day
        time_left = self.change_time.next_iteration - datetime.now(timezone.utc)
        hours = time_left.seconds // 3600
        minutes = (time_left.seconds % 3600) // 60
        seconds = (time_left.seconds % 3600) % 60
        
        description = f"""
                    Time changes between Day and Night every 6 hours. Certain classes earn extra Gold during these times.
                    \n**Current Time**: {Game.time_.capitalize()} {time_emoji}
                    \nThese classes earn x2 Gold during this time: {extra_gold}
                    \nIt will be **{opposite_time.capitalize()}** {opposite_emoji} in {hours} hours {minutes} minutes and {seconds} seconds.
                    """
        
        embed = discord.Embed(
            title="Time", 
            color=discord.Color.default(),
            description=description
            )

        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_role(868589512354332793)
    async def restart(self, ctx):
        '''User can restart progress'''
        
        embed = discord.Embed(title="Restart Account", description="Are you sure you want to restart? All progress will be permanently deleted.")
        components = [
            Button(style=ButtonStyle.green, label= "YES"),
            Button(style=ButtonStyle.red, label="NO")
        ]
        message = await ctx.send(embed=embed, components=[components])
    
        response = await self.bot.wait_for("button_click", timeout=15, check=lambda i: i.author.id == ctx.author.id)

        #Check which option was chosen
        if response.component.label == "YES":
            #Remove Roles then delete user from Database
            for role in ctx.author.roles[1:]:
                await ctx.author.remove_roles(role)
            await self.bot.db.execute("DELETE FROM user_info WHERE id = $1", ctx.author.id)
            
            new_embed = discord.Embed(title="Account Deleted", description=f"{ctx.author.mention} Your account has been deleted. Use $classes to select a class.")
            await message.edit(embed=new_embed, components=[])
            print(f"NAME: {ctx.author.name} ID: {ctx.author.id} REMOVED FROM DATABASE")
        else:
            await message.edit(embed=discord.Embed(description=f"{ctx.author.mention} Your account was not deleted."), components=[])
        
        await message.delete(delay=10)
        await ctx.message.delete(delay=10)

    @commands.command()
    async def test(self, ctx):
        #test function for testing
        await self.bot.db.execute("DELETE FROM user_info WHERE id = $1", 1234)


def setup(bot):
    bot.add_cog(Game(bot))