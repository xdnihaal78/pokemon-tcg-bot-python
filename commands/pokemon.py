import discord
import aiohttp
from discord.ext import commands
from database import Database  # ✅ Import the Database class

# ✅ Initialize Database
db = Database()

POKEAPI_URL = "https://pokeapi.co/api/v2/pokemon/"

class Pokemon(commands.Cog):
    """Handles Pokémon lookups and user collections."""

    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        """Connect to the database when the cog loads."""
        await db.connect()

    async def cog_unload(self):
        """Disconnect from the database when the cog unloads."""
        await db.disconnect()

    async def get_pokemon_data(self, name_or_id: str):
        """Fetch Pokémon details from the PokéAPI."""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{POKEAPI_URL}{name_or_id.lower()}") as response:
                if response.status == 200:
                    return await response.json()
                return None

    @commands.command(name="pokedex")
    async def pokedex(self, ctx, name_or_id: str):
        """Fetch Pokémon details by name or ID."""
        pokemon = await self.get_pokemon_data(name_or_id)
        if not pokemon:
            embed = discord.Embed(
                title="Pokédex Error",
                description=f"❌ Couldn't find a Pokémon named `{name_or_id}`.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)

        # ✅ Extract Pokémon details safely
        name = pokemon.get("name", "Unknown").capitalize()
        poke_id = pokemon.get("id", "N/A")
        height = pokemon.get("height", "N/A")
        weight = pokemon.get("weight", "N/A")
        base_experience = pokemon.get("base_experience", "N/A")
        sprite_url = pokemon.get("sprites", {}).get("front_default", None)

        types = ", ".join(t["type"]["name"].capitalize() for t in pokemon.get("types", [])) or "Unknown"
        abilities = ", ".join(a["ability"]["name"].capitalize() for a in pokemon.get("abilities", [])) or "Unknown"

        # ✅ Create the embed
        embed = discord.Embed(title=name, description=f"ID: **{poke_id}**", color=discord.Color.blue())
        if sprite_url:
            embed.set_thumbnail(url=sprite_url)
        embed.add_field(name="Height", value=f"{height} dm", inline=True)
        embed.add_field(name="Weight", value=f"{weight} hg", inline=True)
        embed.add_field(name="Base Experience", value=f"{base_experience}", inline=True)
        embed.add_field(name="Type", value=types, inline=True)
        embed.add_field(name="Abilities", value=abilities, inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="mypokemon")
    async def mypokemon(self, ctx):
        """Show user's collected Pokémon from the database."""
        user_id = str(ctx.author.id)  # ✅ Ensure IDs are stored as strings

        # ✅ Use Database class instead of direct connection
        rows = await db.fetch("SELECT pokemon_name FROM user_pokemon WHERE user_id = $1", user_id)

        if not rows:
            embed = discord.Embed(
                title="Your Pokémon Collection",
                description="⚠️ You don't own any Pokémon yet! Open a pack to get some!",
                color=discord.Color.orange()
            )
            return await ctx.send(embed=embed)

        # ✅ Format Pokémon list safely
        pokemon_list = "\n".join(f"- {row['pokemon_name'].capitalize()}" for row in rows)

        embed = discord.Embed(
            title=f"{ctx.author.name}'s Pokémon Collection",
            description=pokemon_list,
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

# ✅ Load the Pokémon Cog
async def setup(bot):
    await bot.add_cog(Pokemon(bot))
