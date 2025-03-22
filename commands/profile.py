import discord
from discord.ext import commands
import asyncpg

class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="profile")
    async def profile(self, ctx):
        """Displays the user's Pokémon Trainer Profile"""
        user_id = ctx.author.id
        db_pool: asyncpg.Pool = self.bot.db_pool

        async with db_pool.acquire() as conn:
            user_data = await conn.fetchrow("""
                SELECT 
                    (SELECT COUNT(*) FROM user_pokemon WHERE user_id = $1) AS total_pokemon,
                    (SELECT MAX(cp) FROM user_pokemon WHERE user_id = $1) AS highest_cp,
                    (SELECT wins FROM users WHERE user_id = $1) AS battles_won,
                    (SELECT losses FROM users WHERE user_id = $1) AS battles_lost
            """, user_id)

        if not user_data:
            return await ctx.send(embed=discord.Embed(
                title="Trainer Profile Not Found",
                description="You haven't started your Pokémon journey yet! Open a pack or battle to get started.",
                color=discord.Color.red()
            ))

        # Extract Data
        total_pokemon = user_data["total_pokemon"] or 0
        highest_cp = user_data["highest_cp"] or "N/A"
        battles_won = user_data["battles_won"] or 0
        battles_lost = user_data["battles_lost"] or 0

        # Profile Embed
        embed = discord.Embed(
            title=f"{ctx.author.name}'s Pokémon Trainer Profile",
            color=discord.Color.gold()
        )
        embed.set_thumbnail(url=ctx.author.avatar.url)
        embed.add_field(name="Total Pokémon Owned", value=f"**{total_pokemon}**", inline=True)
        embed.add_field(name="Highest CP Pokémon", value=f"**{highest_cp}**", inline=True)
        embed.add_field(name="🏆 Battles Won", value=f"**{battles_won}**", inline=True)
        embed.add_field(name="💀 Battles Lost", value=f"**{battles_lost}**", inline=True)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Profile(bot))
