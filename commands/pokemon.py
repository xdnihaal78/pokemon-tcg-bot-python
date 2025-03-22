import discord
from discord.ext import commands
import asyncpg
import aiohttp

POKEAPI_URL = "https://pokeapi.co/api/v2/pokemon/"

class Pokemon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_pokemon_data(self, name_or_id):
        """Fetch Pokémon details from the PokéAPI"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{POKEAPI_URL}{name_or_id.lower()}") as response:
                if response.status == 200:
                    return await response.json()
                return None

    @commands.command(name="pokedex")
    async def pokedex(self, ctx, name_or_id: str):
        """Fetch Pokémon details by name or ID"""
        pokemon = await self.get_pokemon_data(name_or_id)
        if not pokemon:
            return await ctx.send(embed=discord.Embed(
                title="Pokédex Error",
                description=f"Couldn't find a Pokémon named `{name_or_id}`.",
                color=discord.Color.red()
            ))

        embed = discord.Embed(
            title=pokemon['name'].capitalize(),
            description=f"ID: **{pokemon['id']}**",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=pokemon['sprites']['front_default'])
        embed.add_field(name="Height", value=f"{pokemon['height']} dm", inline=True)
        embed.add_field(name="Weight", value=f"{pokemon['weight']} hg", inline=True)
        embed.add_field(name="Base Experience", value=f"{pokemon['base_experience']}", inline=True)

        types = ", ".join(t['type']['name'].capitalize() for t in pokemon['types'])
        embed.add_field(name="Type", value=types, inline=True)

        abilities = ", ".join(a['ability']['name'].capitalize() for a in pokemon['abilities'])
        embed.add_field(name="Abilities", value=abilities, inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="mypokemon")
    async def mypokemon(self, ctx):
        """Show user's collected Pokémon from the database"""
        user_id = ctx.author.id
        db_pool: asyncpg.Pool = self.bot.db_pool

        async with db_pool.acquire() as conn:
            rows = await conn.fetch("SELECT pokemon_name FROM user_pokemon WHERE user_id = $1", user_id)

        if not rows:
            return await ctx.send(embed=discord.Embed(
                title="Your Pokémon Collection",
                description="You don't own any Pokémon yet! Open a pack to get some!",
                color=discord.Color.orange()
            ))

        pokemon_list = "\n".join(f"- {row['pokemon_name'].capitalize()}" for row in rows)

        embed = discord.Embed(
            title=f"{ctx.author.name}'s Pokémon Collection",
            description=pokemon_list,
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Pokemon(bot))
