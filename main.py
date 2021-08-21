import asyncio
import discord
import asyncpg

from discord.ext import commands
from json import load
from database.database_main import Database
from discord_components import DiscordComponents, Button


class EconomyBot(commands.Bot):
    def __init__(self, loop): 
        super().__init__(
            command_prefix="$",
            intents = discord.Intents.all(),
            activity = discord.Game("$help"),
            help_command=commands.MinimalHelpCommand()
            )

    async def on_connect(self):
        DiscordComponents(bot)
        
        #Connect to Database
        self.db = Database()
        await self.db.create_pool()

        print("Database Connected")
        print("Bot Connected")

    async def on_disconnect(self):
        await self.close()
        print("Bot Disconnected")
    
    async def on_ready(self):
        #Load cogs
        cogs = ["cogs.game", "cogs.player", "cogs.error_handling", "cogs.admin", "cogs.mini_games"]
        for cog in cogs:
            self.load_extension(cog)
        
        print("Cogs Loaded")
        print("Bot Ready")


if __name__ == "__main__":
    #Load Discord Token
    with open("token.json", "r") as file:
        TOKEN = load(file)["token"]

    loop = asyncio.get_event_loop()

    bot = EconomyBot(loop)

    try:
        loop.run_until_complete(bot.start(TOKEN))
    except KeyboardInterrupt:
        print("Closing Loop")
        loop.close()