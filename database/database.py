import os
from supabase import create_client, Client

# Load environment variables from Railway
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class Database:
    def __init__(self):
        """Initializes the Database connection for the Discord bot."""
        self.supabase = supabase_client

    async def get_user_collection(self, user_id: str):
        """
        Retrieves a user's card collection from Supabase.
        :param user_id: The Discord user ID as a string.
        :return: List of card IDs.
        """
        response = await self.supabase.table("user_collections").select("cards").eq("user_id", user_id).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]["cards"]
        return []

    async def add_card_to_collection(self, user_id: str, card_id: str):
        """
        Adds a card to the user's collection in Supabase.
        :param user_id: The Discord user ID.
        :param card_id: The card ID from Pokémon TCG.
        """
        existing_collection = await self.get_user_collection(user_id)
        if card_id not in existing_collection:
            updated_collection = existing_collection + [card_id]
            await self.supabase.table("user_collections").update({"cards": updated_collection}).eq("user_id", user_id).execute()

    async def log_opened_pack(self, user_id: str, pack: list):
        """
        Logs an opened pack in Supabase.
        :param user_id: The Discord user ID.
        :param pack: List of card IDs in the pack.
        """
        await self.supabase.table("opened_packs").insert({"user_id": user_id, "cards": pack}).execute()

    async def get_last_opened_pack(self, user_id: str):
        """
        Retrieves the most recent pack opened by a user.
        :param user_id: The Discord user ID.
        :return: List of card IDs.
        """
        response = await self.supabase.table("opened_packs").select("cards").eq("user_id", user_id).order("opened_at", desc=True).limit(1).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]["cards"]
        return []
