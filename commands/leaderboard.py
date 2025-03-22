import discord
from discord.ext import commands
from database import Database  # ✅ Import the Database class
from pokemontcgsdk import Card  # ✅ Import Pokémon TCG SDK

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

        # ✅ Fetch leaderboard data safely
        query = """
            SELECT u.id, u.username, 
                   COUNT(up.pokemon_id) AS pokemon_count,
                   COALESCE(u.battles_won, 0) AS battles_won
            FROM users u
            LEFT JOIN user_pokemon up ON u.id = up.user_id
            GROUP BY u.id, u.username, u.battles_won
            ORDER BY battles_won DESC, pokemon_count DESC
            LIMIT 10
        """
        rows = await db.fetch_all(query)

        embed = discord.Embed(
            title="🏆 Pokémon Leaderboard",
            description="Top trainers ranked by battles won and Pokémon collected!",
            color=discord.Color.gold()
        )

        if rows:
            for index, row in enumerate(rows, start=1):
                username = row["username"] or "Unknown Trainer"  # ✅ NULL-safe username
                pokemon_count = row["pokemon_count"] or 0
                battles_won = row["battles_won"] or 0

                embed.add_field(
                    name=f"#{index} {username}",
                    value=(
                        f"🏅 Battles Won: **{battles_won}**\n"
                        f"📦 Pokémon Collected: **{pokemon_count}**"
                    ),
                    inline=False
                )

                # ✅ Add Pokémon Image for the top trainer (if available)
                if index == 1:
                    first_user_id = row["id"]
                    user_pokemon = await db.get_user_pokemon(first_user_id)

                    if user_pokemon:
                        top_pokemon_id = user_pokemon[0]["pokemon_id"]
                        try:
                            pokemon_card = Card.find(top_pokemon_id)
                            embed.set_thumbnail(url=pokemon_card.images.large)
                        except Exception:
                            pass  # Fallback if Pokémon API fails

        else:
            embed.add_field(name="No data yet!", value="Be the first to battle and collect Pokémon!", inline=False)

        await ctx.send(embed=embed)

# ✅ Load the Leaderboard Cog
async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
