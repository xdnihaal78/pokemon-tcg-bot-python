import discord
from discord.ext import commands
from database import Database  # ✅ Correct Import
from pokemontcgsdk import Card  # ✅ Pokémon TCG SDK for reward Pokémon

# ✅ Initialize the database instance
db = Database()

class Missions(commands.Cog):
    """Handles player missions and rewards."""

    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        """Connect to the database when the cog loads."""
        await db.connect()

    async def cog_unload(self):
        """Disconnect from the database when the cog unloads."""
        await db.disconnect()

    @commands.command(name="missions")
    async def missions(self, ctx):
        """Displays the user's available missions and progress."""
        user_id = str(ctx.author.id)  # Ensure IDs are strings
        missions = await db.get_user_missions(user_id)  # ✅ Fetch missions safely

        embed = discord.Embed(title="📜 Missions", color=discord.Color.blue())

        if not missions:
            embed.description = "You have no active missions! 🎯"
            embed.color = discord.Color.red()
        else:
            embed.description = "Here are your current missions:"
            for mission in missions:
                status = "✅ **Completed**" if mission.get("completed") else f"🔄 **Progress:** {mission.get('progress', 0)}/{mission.get('goal', 1)}"
                embed.add_field(
                    name=f"🏆 {mission.get('name', 'Unknown Mission')}",
                    value=f"📖 {mission.get('description', 'No description')}\n**Status:** {status}",
                    inline=False
                )

        await ctx.send(embed=embed)

    @commands.command(name="claim")
    async def claim(self, ctx, mission_id: int):
        """Allows the user to claim rewards for completed missions."""
        user_id = str(ctx.author.id)  # Ensure IDs are strings

        # ✅ Fetch mission to check if it exists
        missions = await db.get_user_missions(user_id)
        mission = next((m for m in missions if m.get("id") == mission_id), None)

        if not mission:
            embed = discord.Embed(title="🎁 Mission Reward", description="❌ Invalid mission ID!", color=discord.Color.red())
            await ctx.send(embed=embed)
            return

        if not mission.get("completed"):
            embed = discord.Embed(title="🎁 Mission Reward", description="⚠️ You must complete the mission first!", color=discord.Color.orange())
            await ctx.send(embed=embed)
            return

        # ✅ Claim reward and fetch Pokémon reward
        reward = await db.claim_mission_reward(user_id, mission_id)  # ✅ Safe DB call
        pokemon_reward = None

        if reward:
            try:
                pokemon_reward = Card.find(reward)  # ✅ Fetch Pokémon TCG card
            except Exception:
                pass  # Fail gracefully if Pokémon API is unavailable

        embed = discord.Embed(title="🎁 Mission Reward", color=discord.Color.green())
        
        if pokemon_reward:
            embed.description = f"✅ You claimed **{pokemon_reward.name}**!"
            embed.set_thumbnail(url=pokemon_reward.images.large)
        else:
            embed.description = f"✅ You claimed **{reward}**!"

        await ctx.send(embed=embed)
        await ctx.message.add_reaction("🎉")  # ✅ Add celebration reaction

async def setup(bot):
    """Loads the Missions cog into the bot."""
    await bot.add_cog(Missions(bot))
