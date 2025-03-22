import discord
import random
import os
import aiohttp
from discord.ext import commands
from database import get_user, add_card_to_user  # Import database functions

POKEMON_TCG_API_KEY = os.getenv("POKEMON_TCG_API_KEY")
POKEMON_TCG_API_URL = "https://api.pokemontcg.io/v2/cards"

class OpenPack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def fetch_cards(self):
        """Fetch a random set of Pokémon cards from the Pokémon TCG API."""
        headers = {"X-Api-Key": POKEMON_TCG_API_KEY}
        params = {"pageSize": 50}  # Fetch a large pool to randomize from

        async with aiohttp.ClientSession() as session:
            async with session.get(POKEMON_TCG_API_URL, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["data"]
                else:
                    return None

    @commands.command(name="openpack")
    async def open_pack(self, ctx):
        """Opens a random Pokémon pack and gives the user cards."""
        user = get_user(ctx.author.id)
        if not user:
            await ctx.send("You need to register first using `/start`.")
            return

        cards = await self.fetch_cards()
        if not cards:
            await ctx.send("Failed to retrieve cards. Try again later.")
            return

        selected_cards = random.sample(cards, 5)  # Open 5 random cards

        embed = discord.Embed(title=f"{ctx.author.name} opened a Pokémon Pack!", color=discord.Color.blue())

        for card in selected_cards:
            card_name = card["name"]
            card_image = card["images"]["small"]
            add_card_to_user(ctx.author.id, card["id"])  # Store in database
            embed.add_field(name=card_name, value="🎴", inline=True)
            embed.set_thumbnail(url=card_image)

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(OpenPack(bot))
