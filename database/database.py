import asyncpg
import os

# Load PostgreSQL connection URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL is not set! Check your .env file.")

class Database:
    def __init__(self):
        """Initializes the Database connection for the Discord bot."""
        self.pool = None

    async def connect(self):
        """Creates a database connection pool."""
        self.pool = await asyncpg.create_pool(DATABASE_URL)
        print("✅ Database connected successfully!")

    async def disconnect(self):
        """Closes the database connection pool."""
        if self.pool:
            await self.pool.close()
            print("✅ Database connection closed.")

    async def get_user_collection(self, user_id: int):
        """Retrieves a user's card collection. If user doesn't exist, create an entry."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT cards FROM user_collections WHERE user_id = $1", user_id)

            if not row:  
                # Insert a new user if they don’t exist
                await conn.execute("INSERT INTO user_collections (user_id, cards) VALUES ($1, $2)", user_id, [])
                return []

            return row["cards"]  # Return the cards list

    async def add_card_to_collection(self, user_id: int, card_id: str):
        """Adds a card to the user's collection."""
        async with self.pool.acquire() as conn:
            existing_collection = await self.get_user_collection(user_id)

            if card_id not in existing_collection:
                updated_collection = existing_collection + [card_id]
                await conn.execute("UPDATE user_collections SET cards = $1 WHERE user_id = $2", updated_collection, user_id)

    async def log_opened_pack(self, user_id: int, pack: list):
        """Logs an opened pack."""
        async with self.pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO opened_packs (user_id, cards) VALUES ($1, $2)", user_id, pack
            )

    async def get_last_opened_pack(self, user_id: int):
        """Gets the last opened pack."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT cards FROM opened_packs WHERE user_id = $1 ORDER BY opened_at DESC LIMIT 1", user_id
            )
            return row["cards"] if row else []

