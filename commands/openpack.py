import discord
import random
import os
import aiohttp
from discord.ext import commands
from database.database import get_user, add_card_to_user  # Fixed import

POKEMON_TCG_API_KEY = os.getenv("POKEMON_TCG_API_KEY")
POKEMON_TCG_API_URL = "https://api.pokemontcg.io/v2/cards"

class OpenPack(commands.Cog):
    """Handles Pokémon pack openings."""

    def __init__(self, bot):
        self.bot = bot

    async def fetch_cards(self):
        """Fetch a random set of Pokémon cards from the Pokémon TCG API."""
        headers = {"X-Api-Key": POKEMON_TCG_API_KEY}
        params = {"pageSize": 100}  # Fetch more cards for better randomness

        async with aiohttp.ClientSession() as session:
            async with session.get(POKEMON_TCG_API_URL, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", [])
                return None

    @commands.command(name="openpack")
    async def open_pack(self, ctx):
        """Opens a random Pokémon pack and gives the user 5 cards."""
        user = await get_user(ctx.author.id)  # Ensure async call
        if not user:
            await ctx.send("❌ You need to register first using `/start`.")
            return

        cards = await self.fetch_cards()
        if not cards:
            await ctx.send("⚠️ Failed to retrieve cards from the API. Please try again later.")
            return

        if len(cards) < 5:
            await ctx.send("⚠️ Not enough cards retrieved from API. Try again later.")
            return

        selected_cards = random.sample(cards, 5)  # Select 5 random cards

        main_embed = discord.Embed(
            title=f"🎉 {ctx.author.name} opened a Pokémon Pack!",
            description="Here are your new Pokémon cards:",
            color=discord.Color.blue()
        )

        card_images = []  # Store image URLs
        for card in selected_cards:
            card_name = card.get("name", "Unknown Pokémon")
            card_id = card.get("id", "Unknown ID")
            card_image = card.get("images", {}).get("small")

            await add_card_to_user(str(ctx.author.id), card_id)  # Ensure user ID is a string for Supabase
            main_embed.add_field(name=card_name, value="🎴", inline=True)

            if card_image:
                card_images.append(card_image)

        # Send the main embed
        await ctx.send(embed=main_embed)

        # Send each card image as a separate embed
        for img_url in card_images:
            image_embed = discord.Embed(color=discord.Color.blue())
            image_embed.set_image(url=img_url)
            await ctx.send(embed=image_embed)

async def setup(bot):
    """Loads the OpenPack cog into the bot."""
    await bot.add_cog(OpenPack(bot))
