import asyncpg
import os
import json

# Load PostgreSQL connection URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL is not set! Check your environment variables.")

class Database:
    def __init__(self):
        """Initializes the Database connection for the Discord bot."""
        self.pool = None

    async def connect(self):
        """Creates a database connection pool."""
        try:
            if not self.pool:
                self.pool = await asyncpg.create_pool(DATABASE_URL)
                print("✅ Database connected successfully!")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")

    async def disconnect(self):
        """Closes the database connection pool."""
        if self.pool:
            await self.pool.close()
            self.pool = None
            print("✅ Database connection closed.")

    async def get_user_collection(self, user_id: int):
        """Retrieves a user's card collection. If user doesn't exist, create an entry."""
        if not self.pool:
            raise RuntimeError("❌ Database connection not established.")

        async with self.pool.acquire() as conn:
            async with conn.transaction():
                row = await conn.fetchrow("SELECT cards FROM user_collections WHERE user_id = $1", user_id)

                if not row:
                    # Insert a new user with an empty collection
                    await conn.execute(
                        "INSERT INTO user_collections (user_id, cards) VALUES ($1, $2)",
                        user_id, json.dumps([])
                    )
                    return []

                return json.loads(row["cards"])  # Convert JSONB back to a Python list

    async def add_card_to_collection(self, user_id: int, card_id: str):
        """Adds a card to the user's collection."""
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                existing_collection = await self.get_user_collection(user_id)

                if card_id not in existing_collection:
                    updated_collection = existing_collection + [card_id]
                    await conn.execute(
                        "UPDATE user_collections SET cards = $1 WHERE user_id = $2",
                        json.dumps(updated_collection), user_id
                    )

    async def log_opened_pack(self, user_id: int, pack: list):
        """Logs an opened pack."""
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "INSERT INTO opened_packs (user_id, cards, opened_at) VALUES ($1, $2, NOW())",
                    user_id, json.dumps(pack)
                )

    async def get_last_opened_pack(self, user_id: int):
        """Gets the last opened pack."""
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                row = await conn.fetchrow(
                    "SELECT cards FROM opened_packs WHERE user_id = $1 ORDER BY opened_at DESC LIMIT 1",
                    user_id
                )
