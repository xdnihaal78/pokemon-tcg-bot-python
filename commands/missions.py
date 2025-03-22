import discord
from discord.ext import commands
from database import Database  # ✅ Correct Import

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
        missions = await db.get_user_missions(user_id)  # ✅ Use Database method

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

        # Fetch missions to check if the mission exists
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

        # Attempt to claim the reward
        reward = await db.claim_mission_reward(user_id, mission_id)  # ✅ Use Database method
        if reward:
            embed = discord.Embed(title="🎁 Mission Reward", description=f"✅ You claimed **{reward}**!", color=discord.Color.green())
        else:
            embed = discord.Embed(title="🎁 Mission Reward", description="❌ Reward already claimed or an error occurred!", color=discord.Color.red())

        await ctx.send(embed=embed)

async def setup(bot):
    """Loads the Missions cog into the bot."""
    await bot.add_cog(Missions(bot))
