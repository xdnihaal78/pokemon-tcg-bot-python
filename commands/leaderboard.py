import discord
from discord.ext import commands
from database import Database  # ✅ Import the Database class

# ✅ Initialize the database instance
db = Database()

class Leaderboard(commands.Cog):
    """Leaderboard command to display the top Pokémon trainers."""

    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        """Connect to the database when the cog loads."""
        await db.connect()

    async def cog_unload(self):
        """Disconnect from the database when the cog unloads."""
        await db.disconnect()

    @commands.command(name="leaderboard")
    async def leaderboard(self, ctx):
        """Displays the top trainers based on Pokémon collection count and battles won."""
        
        # ✅ Use Database connection instead of self.bot.db_pool
        async with db.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT u.username, 
                       COUNT(up.pokemon_id) AS pokemon_count,
                       COALESCE(u.battles_won, 0) AS battles_won
                FROM users u
                LEFT JOIN user_pokemon up ON u.id = up.user_id
                GROUP BY u.id, u.username, u.battles_won
                ORDER BY battles_won DESC, pokemon_count DESC
                LIMIT 10
            """)

        embed = discord.Embed(
            title="🏆 Pokémon Leaderboard",
            description="Top trainers ranked by battles won and Pokémon collected!",
            color=discord.Color.gold()
        )

        if rows:
            for index, row in enumerate(rows, start=1):
                username = row["username"] or "Unknown Trainer"  # ✅ Ensure NULL-safe username
                embed.add_field(
                    name=f"#{index} {username}",
                    value=(
                        f"🏅 Battles Won: **{row['battles_won']}**\n"
                        f"📦 Pokémon Collected: **{row['pokemon_count']}**"
                    ),
                    inline=False
                )
        else:
            embed.add_field(name="No data yet!", value="Be the first to battle and collect Pokémon!", inline=False)

        await ctx.send(embed=embed)

# ✅ Load the Leaderboard Cog
async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
