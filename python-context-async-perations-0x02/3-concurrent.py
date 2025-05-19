import asyncio
import aiosqlite

async def async_fetch_users(db_path):
    # Fetch all users in the database
    async with aiosqlite.connect(db_path) as db:
        async with db.execute('SELECT * FROM users') as cursor:
            results = await cursor.fetchall()
            print('All users fetched')
            for row in results:
                print(row)
            return results

async def async_fetch_older_users(db_path):
    # Fetch users older than 40
    async with aiosqlite.connect(db_path) as db:
        async with db.execute('SELECT * FROM users WHERE age > ?', (40,)) as cursor:
            results = await cursor.fetchall()
            print('Fetching users over 40')
            for row in results:
                print(row)
            return results
        
async def fetch_concurrently():
    # run both fetch operations concurently
    db_path = 'exampl.db' 
    return await asyncio.gather(
        async_fetch_users(db_path),
        async_fetch_older_users(db_path)
    )
        
if __name__=="__main__":
    asyncio.run(fetch_concurrently())
