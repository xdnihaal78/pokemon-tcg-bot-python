import random
import discord
from discord.ext import commands
import supabase
import requests
import os

# Load environment variables from Railway
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
POKEMON_TCG_API_URL = "https://api.pokemontcg.io/v2/cards"

# Initialize Supabase client
supabase_client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)

class WonderPick(commands.Cog):
    def __init__(self, bot):
        """
        Initializes the WonderPick system as a Discord cog.
        """
        self.bot = bot
        self.supabase = supabase_client

    def fetch_card_info(self, card_id):
        """
        Fetches Pokémon card details from the Pokémon TCG API.
        """
        response = requests.get(f"{POKEMON_TCG_API_URL}/{card_id}")
        if response.status_code == 200:
            return response.json().get("data", {})
        return None

    def get_user_collection(self, user_id):
        """
        Retrieves a user's card collection from Supabase.
        """
        response = self.supabase.table("user_collections").select("cards").eq("user_id", user_id).execute()
        if response.data:
            return response.data[0]["cards"]
        return []

    def update_user_collection(self, user_id, new_card):
        """
        Adds a new card to the user's collection in Supabase.
        """
        existing_collection = self.get_user_collection(user_id)
        if new_card not in existing_collection:
            updated_collection = existing_collection + [new_card]
            self.supabase.table("user_collections").update({"cards": updated_collection}).eq("user_id", user_id).execute()

    @commands.command(name="wonderpick")
    async def wonderpick(self, ctx, pack_opener: discord.Member):
        """
        Allows a user to gamble and get a card from another user's pack.
        """
        gambler_id = str(ctx.author.id)
        pack_opener_id = str(pack_opener.id)

        # Fetch the last opened pack from Supabase
        response = self.supabase.table("opened_packs").select("cards").eq("user_id", pack_opener_id).order("opened_at", desc=True).limit(1).execute()
        if not response.data:
            await ctx.send(f"🚫 {pack_opener.mention} has not opened any packs recently.")
            return

        pack = response.data[0]["cards"]
        if not pack:
            await ctx.send(f"🚫 No cards available from {pack_opener.mention}'s pack!")
            return

        # Select a random card
        chosen_card = random.choice(pack)
        card_info = self.fetch_card_info(chosen_card)
        card_name = card_info.get("name", "Unknown Card")

        # Update both users' collections
        self.update_user_collection(gambler_id, chosen_card)
        self.update_user_collection(pack_opener_id, chosen_card)

        # Send Discord message
        embed = discord.Embed(
            title="🎰 WonderPick!",
            description=f"{ctx.author.mention} used WonderPick and won **{card_name}** from {pack_opener.mention}!",
            color=discord.Color.gold()
        )
        if "images" in card_info and "large" in card_info["images"]:
            embed.set_thumbnail(url=card_info["images"]["large"])

        await ctx.send(embed=embed)

# Add Cog to Bot
def setup(bot):
    bot.add_cog(WonderPick(bot))
