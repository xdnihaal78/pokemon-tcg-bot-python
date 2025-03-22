import asyncpg
import os
import json

# ✅ Load PostgreSQL connection URL securely
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL is not set! Check your environment variables.")

class Database:
    """Handles all database interactions for the Discord bot."""

    def __init__(self):
        """Initializes the database connection pool."""
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

    async def get_user(self, user_id: int):
        """Fetches user data, inserting them into the database if necessary."""
        if not self.pool:
            raise RuntimeError("❌ Database connection not established.")

        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)
            if not row:
                await conn.execute("INSERT INTO users (user_id) VALUES ($1)", user_id)
                return {"user_id": user_id}
            return dict(row)

    async def get_user_missions(self, user_id: int):
        """Fetches a user's missions, returning an empty list if none exist."""
        if not self.pool:
            raise RuntimeError("❌ Database connection not established.")

        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT missions FROM user_missions WHERE user_id = $1", user_id)
            return json.loads(row["missions"]) if row else []

    async def get_user_pokemon(self, user_id: int):
        """Fetches a user's Pokémon collection, returning an empty list if none exist."""
        if not self.pool:
            raise RuntimeError("❌ Database connection not established.")

        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT pokemon FROM user_pokemon WHERE user_id = $1", user_id)
            return json.loads(row["pokemon"]) if row else []

    async def get_user_collection(self, user_id: int):
        """Retrieves a user's card collection, initializing an entry if necessary."""
        if not self.pool:
            raise RuntimeError("❌ Database connection not established.")

        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT cards FROM user_collections WHERE user_id = $1", user_id)
            if not row:
                await conn.execute(
                    "INSERT INTO user_collections (user_id, cards) VALUES ($1, $2)",
                    user_id, json.dumps([])
                )
                return []
            return json.loads(row["cards"])

    async def add_card_to_collection(self, user_id: int, card_id: str):
        """Adds a card to the user's collection if it's not already present."""
        if not self.pool:
            raise RuntimeError("❌ Database connection not established.")

        async with self.pool.acquire() as conn:
            collection = await self.get_user_collection(user_id)
            if card_id not in collection:
                collection.append(card_id)
                await conn.execute(
                    "UPDATE user_collections SET cards = $1 WHERE user_id = $2",
                    json.dumps(collection), user_id
                )

    async def log_opened_pack(self, user_id: int, pack: list):
        """Logs an opened pack with a timestamp."""
        if not self.pool:
            raise RuntimeError("❌ Database connection not established.")

        async with self.pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO opened_packs (user_id, cards, opened_at) VALUES ($1, $2, NOW())",
                user_id, json.dumps(pack)
            )

    async def get_last_opened_pack(self, user_id: int):
        """Retrieves the most recent opened pack, or an empty list if none exist."""
        if not self.pool:
            raise RuntimeError("❌ Database connection not established.")

        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT cards FROM opened_packs WHERE user_id = $1 ORDER BY opened_at DESC LIMIT 1",
                user_id
            )
            return json.loads(row["cards"]) if row else []
