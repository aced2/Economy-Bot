import asyncpg
import asyncio

from json import load


class Database:
    '''Create connection pool and common commands'''

    def __init__(self):
        self.pool = None
    
    async def create_pool(self):
        '''Create connection Pool'''
        with open(r"database_login.json", "r") as file:
            login = load(file)

        self.pool = await asyncpg.create_pool(**login)
    
    async def add_user(self, query, *args):
        '''Add new user to database (after they select a Class)'''
        async with self.pool.acquire() as con:
            print("ADDING USER TO DATABASE")
            return await con.execute(query, *args)

    async def fetchrow(self, query, *args):
        '''Fetch a user's info'''
        async with self.pool.acquire() as con:
            return await con.fetchrow(query, *args)
    
    async def execute(self, query, *args):
        '''Execute a query'''
        async with self.pool.acquire() as con:
            return await con.execute(query, *args)
        

        