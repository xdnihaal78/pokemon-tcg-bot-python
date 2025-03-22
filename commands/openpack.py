import discord
import random
import aiohttp
from discord.ext import commands
from database import Database  # ✅ Correct Import
from pokemontcgsdk import Card  # ✅ Pokémon TCG SDK

# ✅ Initialize the database instance
db = Database()

class OpenPack(commands.Cog):
    """Handles Pokémon pack openings."""

    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        """Connect to the database when the cog loads."""
        await db.connect()

    async def cog_unload(self):
        """Disconnect from the database when the cog unloads."""
        await db.disconnect()

    async def fetch_cards(self):
        """Fetch a random set of Pokémon cards using the Pokémon TCG SDK."""
        try:
            cards = Card.where(pageSize=250)  # ✅ Fetch 250 random cards
            return cards
        except Exception:
            return None  # ✅ Fail safely if API is down

    @commands.command(name="openpack")
    async def open_pack(self, ctx):
        """Opens a random Pokémon pack and gives the user 5 cards."""
        user_id = str(ctx.author.id)  # ✅ Ensure user ID is a string
        user = await db.get_user_collection(user_id)

        if user is None:
            await ctx.send("❌ You need to register first using `/start`.")
            return

        cards = await self.fetch_cards()
        if not cards or len(cards) < 5:
            await ctx.send("⚠️ Failed to retrieve enough cards. Please try again later.")
            return

        selected_cards = random.sample(cards, 5)  # ✅ Select 5 random cards

        main_embed = discord.Embed(
            title=f"🎉 {ctx.author.name} opened a Pokémon Pack!",
            description="Here are your new Pokémon cards:",
            color=discord.Color.blue()
        )

        image_urls = []  # ✅ Store image URLs
        for card in selected_cards:
            await db.add_card_to_collection(user_id, card.id)  # ✅ Store in DB
            main_embed.add_field(
                name=f"✨ {card.name}",
                value=f"🆔 `{card.id}`",
                inline=True
            )
            if card.images and "small" in card.images:
                image_urls.append(card.images["small"])

        await ctx.send(embed=main_embed)

        # ✅ Send images in groups to avoid spam
        if image_urls:
            image_embed = discord.Embed(color=discord.Color.blue())
            for img_url in image_urls:
                image_embed.set_image(url=img_url)
                await ctx.send(embed=image_embed)

        await ctx.message.add_reaction("🎉")  # ✅ Celebration Reaction

async def setup(bot):
    """Loads the OpenPack cog into the bot."""
    await bot.add_cog(OpenPack(bot))
