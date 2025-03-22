import random
import discord
from discord import Embed
from discord.ext import commands
from database.database import get_user_pokemon, get_pokemon_stats, update_user_wins, update_user_losses  # Fixed import

class Battle(commands.Cog):
    """Handles Pokémon battles between users."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="battle")
    async def battle(self, ctx: commands.Context, opponent: discord.Member):
        """Initiates a battle between two users based on their Pokémon stats."""
        if ctx.author.id == opponent.id:
            await ctx.send("❌ You cannot battle yourself!")
            return

        challenger_id = str(ctx.author.id)  # Ensure IDs are strings
        opponent_id = str(opponent.id)

        # Fetch Pokémon for both players
        challenger_pokemon = await get_user_pokemon(challenger_id)
        opponent_pokemon = await get_user_pokemon(opponent_id)

        if not challenger_pokemon:
            await ctx.send(f"⚠️ {ctx.author.mention}, you have no Pokémon to battle with!")
            return
        if not opponent_pokemon:
            await ctx.send(f"⚠️ {opponent.mention} has no Pokémon to battle with!")
            return

        # Select random Pokémon for battle
        challenger_pokemon_data = random.choice(challenger_pokemon)
        opponent_pokemon_data = random.choice(opponent_pokemon)

        challenger_pokemon_id = challenger_pokemon_data.get("pokemon_id")  # Ensure correct field
        opponent_pokemon_id = opponent_pokemon_data.get("pokemon_id")

        # Fetch Pokémon stats
        challenger_stats = await get_pokemon_stats(challenger_pokemon_id)
        opponent_stats = await get_pokemon_stats(opponent_pokemon_id)

        if not challenger_stats or not opponent_stats:
            await ctx.send("❌ Error retrieving Pokémon stats. Please try again later.")
            return

        # Battle calculations
        challenger_attack = challenger_stats.get("attack", 10)  # Default values for safety
        challenger_defense = challenger_stats.get("defense", 5)
        opponent_attack = opponent_stats.get("attack", 10)
        opponent_defense = opponent_stats.get("defense", 5)

        challenger_damage = max(1, challenger_attack - opponent_defense)
        opponent_damage = max(1, opponent_attack - challenger_defense)

        # Determine winner
        if challenger_damage > opponent_damage:
            winner = ctx.author
            loser = opponent
            await update_user_wins(challenger_id)
            await update_user_losses(opponent_id)
        elif opponent_damage > challenger_damage:
            winner = opponent
            loser = ctx.author
            await update_user_wins(opponent_id)
            await update_user_losses(challenger_id)
        else:
            winner = None

        # Embed battle result
        embed = Embed(title="🔥 Pokémon Battle! 🔥", color=discord.Color.gold())
        embed.add_field(
            name=f"⚔️ {ctx.author.display_name}'s Pokémon",
            value=f"**{challenger_stats.get('name', 'Unknown')}**\nATK: {challenger_attack}, DEF: {challenger_defense}",
            inline=True,
        )
        embed.add_field(
            name=f"⚔️ {opponent.display_name}'s Pokémon",
            value=f"**{opponent_stats.get('name', 'Unknown')}**\nATK: {opponent_attack}, DEF: {opponent_defense}",
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
