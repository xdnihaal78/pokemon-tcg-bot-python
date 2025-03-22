import random
import discord
import aiohttp  # ✅ For async HTTP requests
import os
from discord.ext import commands
from supabase import create_client, Client

# ✅ Load environment variables securely
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# ✅ Check if credentials exist
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("⚠️ Supabase credentials are missing! Please check your environment variables.")

# ✅ Initialize Supabase client
supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

POKEMON_TCG_API_URL = "https://api.pokemontcg.io/v2/cards"

class WonderPick(commands.Cog):
    """Handles the WonderPick gambling feature in the bot."""

    def __init__(self, bot):
        self.bot = bot
        self.supabase = supabase_client

    async def fetch_card_info(self, card_id):
        """
        Fetches Pokémon card details from the Pokémon TCG API asynchronously.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{POKEMON_TCG_API_URL}/{card_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", {})
        return None

    async def get_user_collection(self, user_id):
        """
        Retrieves a user's card collection from Supabase.
        """
        response = self.supabase.table("user_collections").select("cards").eq("user_id", user_id).execute()
        if response.data and len(response.data) > 0:
            return response.data[0].get("cards", [])
        return []

    async def update_user_collection(self, user_id, new_card):
        """
        Adds a new card to the user's collection in Supabase.
        """
        existing_collection = await self.get_user_collection(user_id)
        if new_card not in existing_collection:
            updated_collection = existing_collection + [new_card]
            self.supabase.table("user_collections").update({"cards": updated_collection}).eq("user_id", user_id).execute()

    @commands.command(name="wonderpick")
    async def wonderpick(self, ctx, pack_opener: discord.Member):
        """
        Allows a user to gamble and randomly get a card from another user's opened pack.
        """
        gambler_id = str(ctx.author.id)
        pack_opener_id = str(pack_opener.id)

        # ✅ Fetch the last opened pack from Supabase
        response = self.supabase.table("opened_packs").select("cards").eq("user_id", pack_opener_id).order("opened_at", desc=True).limit(1).execute()
        
        if not response.data or len(response.data) == 0:
            return await ctx.send(f"🚫 {pack_opener.mention} has not opened any packs recently.")

        pack = response.data[0].get("cards", [])
        if not pack:
            return await ctx.send(f"🚫 No cards available from {pack_opener.mention}'s pack!")

        # ✅ Select a random card
        chosen_card = random.choice(pack)
        card_info = await self.fetch_card_info(chosen_card)
        
        if not card_info:
            return await ctx.send("⚠️ Failed to retrieve card details. Please try again later.")

        card_name = card_info.get("name", "Unknown Card")

        # ✅ Ensure the pack opener doesn't lose the card permanently
        if chosen_card in pack:
            pack.remove(chosen_card)
            self.supabase.table("opened_packs").update({"cards": pack}).eq("user_id", pack_opener_id).execute()

        # ✅ Update gambler's collection
        await self.update_user_collection(gambler_id, chosen_card)

        # ✅ Send success message
        embed = discord.Embed(
            title="🎰 WonderPick!",
            description=f"{ctx.author.mention} used WonderPick and won **{card_name}** from {pack_opener.mention}! 🎉",
            color=discord.Color.gold()
        )
        if "images" in card_info and "large" in card_info["images"]:
            embed.set_thumbnail(url=card_info["images"]["large"])

        await ctx.send(embed=embed)

# ✅ Load the WonderPick Cog
async def setup(bot):
    await bot.add_cog(WonderPick(bot))
