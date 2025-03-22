import discord
from discord.ext import commands
from database import get_user_missions, complete_mission, claim_mission_reward

class Missions(commands.Cog):
    """Handles player missions and rewards."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="missions")
    async def missions(self, ctx):
        """Displays the user's available missions and progress."""
        user_id = ctx.author.id
        missions = await get_user_missions(user_id)  # Ensure async call

        embed = discord.Embed(title="Missions", color=discord.Color.blue())

        if not missions:
            embed.description = "No active missions!"
            embed.color = discord.Color.red()
        else:
            embed.description = "Here are your current missions:"
            for mission in missions:
                status = "✅ Completed" if mission["completed"] else f"🔄 Progress: {mission['progress']}/{mission['goal']}"
                embed.add_field(
                    name=mission["name"],
                    value=f"{mission['description']}\n**Status:** {status}",
                    inline=False
                )

        await ctx.send(embed=embed)

    @commands.command(name="claim")
    async def claim(self, ctx, mission_id: int):
        """Allows the user to claim rewards for completed missions."""
        user_id = ctx.author.id

        # Check if mission is completed before claiming
        missions = await get_user_missions(user_id)
        mission = next((m for m in missions if m["id"] == mission_id), None)

        if not mission:
            embed = discord.Embed(title="Mission Reward", description="Invalid mission ID!", color=discord.Color.red())
            await ctx.send(embed=embed)
            return

        if not mission["completed"]:
            embed = discord.Embed(title="Mission Reward", description="You must complete the mission first!", color=discord.Color.orange())
            await ctx.send(embed=embed)
            return

        # Claim the reward
        reward = await claim_mission_reward(user_id, mission_id)
        if reward:
            embed = discord.Embed(title="Mission Reward", description=f"You claimed **{reward}**!", color=discord.Color.green())
        else:
            embed = discord.Embed(title="Mission Reward", description="Reward already claimed or an error occurred!", color=discord.Color.red())

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Missions(bot))
