import asyncio
import aiosqlite

async def asyncfetchusers(db_path):
    """Fetch all users from the database"""
    async with aiosqlite.connect(db_path) as db:
        async with db.execute("SELECT * FROM users") as cursor:
            results = await cursor.fetchall()
            print("All users fetched:")
            for row in results:
                print(row)
            return results

async def asyncfetcholder_users(db_path):
    """Fetch users older than 40 from the database"""
    async with aiosqlite.connect(db_path) as db:
        async with db.execute("SELECT * FROM users WHERE age > ?", (40,)) as cursor:
            results = await cursor.fetchall()
            print("\nUsers older than 40 fetched:")
            for row in results:
                print(row)
            return results

async def fetch_concurrently():
    """Run both fetch operations concurrently"""
    db_path = "example.db"
    return await asyncio.gather(
        asyncfetchusers(db_path),
        asyncfetcholder_users(db_path)
    )

if __name__ == "__main__":
    # Run the concurrent fetches
    asyncio.run(fetch_concurrently())