import random
import discord
from discord import Embed
from discord.ext import commands
from database import Database  # ✅ Correct Import
from pokemontcgsdk import Card  # ✅ Import Pokémon TCG SDK

# ✅ Initialize the database instance
db = Database()

class Battle(commands.Cog):
    """Handles Pokémon battles between users."""

    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        """Connect to the database when the cog loads."""
        await db.connect()

    async def cog_unload(self):
        """Disconnect from the database when the cog unloads."""
        await db.disconnect()

    @commands.command(name="battle")
    async def battle(self, ctx: commands.Context, opponent: discord.Member):
        """Initiates a battle between two users based on their Pokémon stats."""
        if ctx.author.id == opponent.id:
            await ctx.send("❌ You cannot battle yourself!")
            return

        challenger_id = str(ctx.author.id)
        opponent_id = str(opponent.id)

        # Fetch Pokémon for both players
        challenger_pokemon = await db.get_user_pokemon(challenger_id)
        opponent_pokemon = await db.get_user_pokemon(opponent_id)

        if not challenger_pokemon:
            await ctx.send(f"⚠️ {ctx.author.mention}, you have no Pokémon to battle with!")
            return
        if not opponent_pokemon:
            await ctx.send(f"⚠️ {opponent.mention} has no Pokémon to battle with!")
            return

        # Select random Pokémon for battle
        challenger_pokemon_data = random.choice(challenger_pokemon)
        opponent_pokemon_data = random.choice(opponent_pokemon)

        challenger_pokemon_id = challenger_pokemon_data.get("pokemon_id")
        opponent_pokemon_id = opponent_pokemon_data.get("pokemon_id")

        # Fetch Pokémon details from API
        try:
            challenger_pokemon_api = Card.find(challenger_pokemon_id)
            opponent_pokemon_api = Card.find(opponent_pokemon_id)
        except Exception:
            await ctx.send("❌ Error retrieving Pokémon data from the API.")
            return

        if not challenger_pokemon_api or not opponent_pokemon_api:
            await ctx.send("❌ Could not find Pokémon details. Check Pokémon IDs.")
            return

        # Battle calculations
        challenger_attack = random.randint(30, 100)  # Using random values for now
        challenger_defense = random.randint(20, 80)
        opponent_attack = random.randint(30, 100)
        opponent_defense = random.randint(20, 80)

        challenger_damage = max(1, challenger_attack - opponent_defense)
        opponent_damage = max(1, opponent_attack - challenger_defense)

        # Determine winner
        if challenger_damage > opponent_damage:
            winner = ctx.author
            loser = opponent
            await db.update_user_wins(challenger_id)
            await db.update_user_losses(opponent_id)
        elif opponent_damage > challenger_damage:
            winner = opponent
            loser = ctx.author
            await db.update_user_wins(opponent_id)
            await db.update_user_losses(challenger_id)
        else:
            winner = None

        # Embed battle result
        embed = Embed(title="🔥 Pokémon Battle! 🔥", color=discord.Color.gold())
        embed.set_thumbnail(url=challenger_pokemon_api.images.large)  # ✅ Pokémon image
        embed.add_field(
            name=f"⚔️ {ctx.author.display_name}'s Pokémon",
            value=f"**{challenger_pokemon_api.name}**\nATK: {challenger_attack}, DEF: {challenger_defense}",
            inline=True,
        )
        embed.add_field(
            name=f"⚔️ {opponent.display_name}'s Pokémon",
            value=f"**{opponent_pokemon_api.name}**\nATK: {opponent_attack}, DEF: {opponent_defense}",
            inline=True,
        )

        if winner:
            embed.add_field(name="🏆 Winner!", value=f"**{winner.mention}** wins!", inline=False)
        else:
            embed.add_field(name="⚔️ Result", value="It's a **draw**!", inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    """Loads the Battle cog into the bot."""
    await bot.add_cog(Battle(bot))
