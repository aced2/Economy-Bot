import discord
import typing

from discord.utils import get
from discord.ext import tasks, commands
from datetime import datetime, timezone, timedelta
from discord_components import Button, ButtonStyle, InteractionType


class Game(commands.Cog):

    time_ = "night"
    classes_stats = {
        "warrior": {"atk": 5, "hp": 20, "armor": 5, "gold_per_hunt": {"low": 20, "high": 30}, "emoji": ":man_supervillain:"},
        "mage": {"atk": 11, "hp": 10, "armor": 0, "gold_per_hunt": {"low": 23, "high": 26}, "emoji": ":man_mage:"},
        "ninja": {"atk": 8, "hp": 12, "armor": 35, "gold_per_hunt": {"low": 25, "high": 25}, "emoji": ":ninja"},
        "werewolf": {"atk": 3, "hp": 30, "armor": 5, "gold_per_hunt": {"low": 20, "high": 30}, "emoji": ":wolf:"},
        "vampire": {"atk": 9, "hp": 7, "armor": 4, "gold_per_hunt": {"low": 23, "high": 36}, "emoji": ":man_vampire:"},
        "zombie": {"atk": 5, "hp": 10, "armor": 5, "gold_per_hunt": {"low": 25, "high": 25}, "emoji": ":man_zombie:"}
    }

    food_prices = {"carrot": 3, "corn": 5, "watermelon": 7, "strawberry": 5}

    shop_items = {"water": {"price": 24, "description": "Use $farm to double profits when holding water."}}


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

        delete_user_query = "DELETE FROM user_info WHERE id = $1"
        delete_food_query = "DELETE FROM user_food WHERE id = $1"
        await self.bot.db.execute(delete_user_query, member.id)
        await self.bot.db.execute(delete_food_query, member.id)

        print(f"NAME: {member.name} ID: {member.id} REMOVED FROM DATABASE")
    
    @commands.command()
    async def classes(self, ctx):
        '''Display information about the different Classes'''

        description = """
                    :crossed_swords: = Attack\n:heart: = HP\n:shield: = Armor\n:coin: = Gold per Hunt
                    \nDay -> Warrior, Mage, Ninja x2 Gold\nNight -> Werewolf, Vampire, Zombie x2 Gold
                    \nUse **$time** for more info
                    Use **$select [class]** to select a Class\n\u200b
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
    async def profile(self, ctx, *, user: discord.Member):
        '''Get profile of a user'''

        roles = "\n".join(role.mention for role in user.roles[1:])
        joined = user.joined_at.strftime(r"%A, %d. %B %Y %I:%M%p")
        
        #Choose status color
        if user.status == discord.Status.online:
            status_string = "```diff\n+ Online +\n```"
        elif user.status == discord.Status.idle:
            status_string = "```fix\n< Idle >\n```"
        elif user.status in [discord.Status.dnd, discord.Status.do_not_disturb]:
            status_string = "```diff\n- Do not distrub -\n```"

        user_data = await self.bot.db.fetchrow("SELECT * FROM user_info WHERE id = $1", user.id)
        food_data = await self.bot.db.fetchrow("SELECT * FROM user_food WHERE id = $1", user.id)
        
        #Check if user is in database
        if user_data == None:
            await ctx.send(f"{ctx.author.mention} {user.name} has not selected a Class yet.", delete_after=10)
            await ctx.message.delete(delay=10)
            return

        user_class = user_data["class"].capitalize()
        user_gold = str(user_data["gold"]) + ":coin:"
        food_string = f"{food_data['carrot']} :carrot: {food_data['corn']} :corn: {food_data['watermelon']} :watermelon: {food_data['strawberry']} :strawberry: {food_data['water']} :droplet:"

        embed = discord.Embed(title=user.name, description=f"**Joined on:** {joined}")
        embed.set_thumbnail(url=user.avatar_url)
        embed.add_field(name="Class", value=user_class, inline=True)
        embed.add_field(name="Total Gold", value=user_gold, inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)
        embed.add_field(name="Roles", value=roles, inline=True)
        embed.add_field(name="Status", value=status_string, inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)
        embed.add_field(name="Food Inventory", value=food_string, inline=True)
        embed.set_footer(text=f"ID: {user.id}")
        
        await ctx.send(embed=embed)
    
    @commands.command()
    async def shop(self, ctx):
        '''Display shop items'''

        embed = discord.Embed(title="Shop", description="Use $buy [item] to buy an item")
        for item in Game.shop_items.keys():
            embed.add_field(name=f"{item.capitalize()} - {Game.shop_items[item]['price']} :coin:", value=Game.shop_items[item]['description'])
        
        await ctx.send(embed=embed)
    
    @commands.command()
    async def buy(self, ctx, *, item):
        '''User can buy an item'''

        if item not in Game.shop_items.keys():
            await ctx.send(f"{ctx.author.mention} Invalid Item. Use $shop to see list of items", delete_after=10)
            await ctx.message.delete(delay=10)
            return
        
        user_gold = (await self.bot.db.fetchrow("SELECT gold FROM user_info WHERE id = $1", ctx.author.id))["gold"]
        if item == "water":
            if user_gold < Game.shop_items["water"]["price"]:
                await ctx.send(f"{ctx.author.mention} You do not have enough money to buy this.", delete_after=10)
                await ctx.message.delete(delay=10)
                return

            user_water = (await self.bot.db.fetchrow("SELECT water FROM user_food WHERE id = $1", ctx.author.id))["water"]
            user_water += 1 
            user_gold -= Game.shop_items["water"]["price"]
            await self.bot.db.execute("UPDATE user_info SET gold = $1 WHERE id = $2", user_gold, ctx.author.id)
            await self.bot.db.execute("UPDATE user_food SET water = $1 WHERE id = $2", user_water, ctx.author.id)
            await ctx.send(f"{ctx.author.mention} Water purchase. Your balance is now {user_gold} :coin:")
            return

    @commands.command()
    async def test(self, ctx):
        #test function for testing
        x = dict(await self.bot.db.fetchrow("SELECT * FROM user_food WHERE id = $1", ctx.author.id))
        for i in x.keys():
            print(i, x[i])


def setup(bot):
    bot.add_cog(Game(bot))