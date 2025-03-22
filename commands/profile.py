import discord
import asyncpg
from discord.ext import commands

class Profile(commands.Cog):
    """Handles the Pokémon Trainer Profile command."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="profile")
    async def profile(self, ctx):
        """Displays the user's Pokémon Trainer Profile."""
        user_id = ctx.author.id
        db_pool: asyncpg.Pool = self.bot.db_pool

        async with db_pool.acquire() as conn:
            user_data = await conn.fetchrow("""
                SELECT 
                    COALESCE((SELECT COUNT(*) FROM user_pokemon WHERE user_id = $1), 0) AS total_pokemon,
                    COALESCE((SELECT MAX(cp) FROM user_pokemon WHERE user_id = $1), 'N/A') AS highest_cp,
                    COALESCE((SELECT wins FROM users WHERE user_id = $1), 0) AS battles_won,
                    COALESCE((SELECT losses FROM users WHERE user_id = $1), 0) AS battles_lost
            """, user_id)

        # If user has no data
        if not user_data:
            embed = discord.Embed(
                title="Trainer Profile Not Found",
                description="You haven't started your Pokémon journey yet! Open a pack or battle to get started.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)

        # Extract Data
        total_pokemon = user_data["total_pokemon"]
        highest_cp = user_data["highest_cp"]
        battles_won = user_data["battles_won"]
        battles_lost = user_data["battles_lost"]

        # Profile Embed
        embed = discord.Embed(
            title=f"{ctx.author.name}'s Pokémon Trainer Profile",
            color=discord.Color.gold()
        )
        if ctx.author.avatar:
            embed.set_thumbnail(url=ctx.author.avatar.url)

        embed.add_field(name="Total Pokémon Owned", value=f"**{total_pokemon}**", inline=True)
        embed.add_field(name="Highest CP Pokémon", value=f"**{highest_cp}**", inline=True)
        embed.add_field(name="🏆 Battles Won", value=f"**{battles_won}**", inline=True)
        embed.add_field(name="💀 Battles Lost", value=f"**{battles_lost}**", inline=True)

        await ctx.send(embed=embed)

async def setup(bot):
    """Loads the Profile cog into the bot."""
    await bot.add_cog(Profile(bot))
