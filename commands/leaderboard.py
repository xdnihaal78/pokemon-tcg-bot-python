import discord
from discord.ext import commands
import asyncpg

async def leaderboard(ctx, db_pool):
    """Displays the top trainers based on Pokémon collection count and battles won."""

    async with db_pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT u.username, 
                   COUNT(up.pokemon_id) AS pokemon_count,
                   COALESCE(u.battles_won, 0) AS battles_won
            FROM users u
            LEFT JOIN user_pokemon up ON u.id = up.user_id
            GROUP BY u.id, u.battles_won
            ORDER BY battles_won DESC, pokemon_count DESC
            LIMIT 10
        """)

    embed = discord.Embed(
        title="🏆 Pokémon Leaderboard",
        description="Top trainers ranked by battles won and Pokémon collected!",
        color=0xFFD700
    )

    if rows:
        for index, row in enumerate(rows, start=1):
            embed.add_field(
                name=f"#{index} {row['username']}",
                value=(
                    f"🏅 Battles Won: **{row['battles_won']}**\n"
                    f"📦 Pokémon Collected: **{row['pokemon_count']}**"
                ),
                inline=False
            )
    else:
        embed.add_field(name="No data yet!", value="Be the first to battle and collect Pokémon!", inline=False)

    await ctx.send(embed=embed)
