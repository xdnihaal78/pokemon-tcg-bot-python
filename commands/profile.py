import discord
from discord.ext import commands
from database import Database  # ✅ Use Supabase Database class

# ✅ Initialize Database
db = Database()

class Profile(commands.Cog):
    """Handles the Pokémon Trainer Profile command."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="profile")
    async def profile(self, ctx):
        """Displays the user's Pokémon Trainer Profile."""
        user_id = str(ctx.author.id)  # ✅ Ensure ID is a string for Supabase

        # ✅ Fetch user data from the database
        user_data = await db.fetchrow("""
            SELECT 
                (SELECT COUNT(*) FROM user_pokemon WHERE user_id = %s) AS total_pokemon,
                (SELECT MAX(cp) FROM user_pokemon WHERE user_id = %s) AS highest_cp,
                (SELECT wins FROM users WHERE user_id = %s) AS battles_won,
                (SELECT losses FROM users WHERE user_id = %s) AS battles_lost
        """, user_id, user_id, user_id, user_id)

        # If user has no data
        if not user_data:
            embed = discord.Embed(
                title="Trainer Profile Not Found",
                description="⚠️ You haven't started your Pokémon journey yet!\nOpen a pack or battle to get started.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)

        # ✅ Extract Data Safely
        total_pokemon = user_data["total_pokemon"] or 0
        highest_cp = user_data["highest_cp"] or "N/A"
        battles_won = user_data["battles_won"] or 0
        battles_lost = user_data["battles_lost"] or 0

        # ✅ Profile Embed
        embed = discord.Embed(
            title=f"🎒 {ctx.author.name}'s Pokémon Trainer Profile",
            color=discord.Color.gold()
        )
        if ctx.author.avatar:
            embed.set_thumbnail(url=ctx.author.avatar.url)

        embed.add_field(name="🐉 Total Pokémon Owned", value=f"**{total_pokemon}**", inline=True)
        embed.add_field(name="💪 Highest CP Pokémon", value=f"**{highest_cp}**", inline=True)
        embed.add_field(name="🏆 Battles Won", value=f"**{battles_won}**", inline=True)
        embed.add_field(name="💀 Battles Lost", value=f"**{battles_lost}**", inline=True)

        await ctx.send(embed=embed)

# ✅ Load the Profile Cog
async def setup(bot):
    await bot.add_cog(Profile(bot))
