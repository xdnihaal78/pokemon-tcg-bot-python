import discord
from discord.ext import commands
from database import get_user_missions, complete_mission, claim_mission_reward

class Missions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="missions")
    async def missions(self, ctx):
        """Displays the user's available missions and progress."""
        user_id = ctx.author.id
        missions = get_user_missions(user_id)

        if not missions:
            embed = discord.Embed(title="Missions", description="No active missions!", color=discord.Color.red())
        else:
            embed = discord.Embed(title="Missions", description="Here are your current missions:", color=discord.Color.blue())
            for mission in missions:
                status = "✅ Completed" if mission["completed"] else f"🔄 Progress: {mission['progress']}/{mission['goal']}"
                embed.add_field(name=mission["name"], value=f"{mission['description']}\n**Status:** {status}", inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="claim")
    async def claim(self, ctx, mission_id: int):
        """Allows the user to claim rewards for completed missions."""
        user_id = ctx.author.id
        reward = claim_mission_reward(user_id, mission_id)

        if reward:
            embed = discord.Embed(title="Mission Reward", description=f"You claimed **{reward}**!", color=discord.Color.green())
        else:
            embed = discord.Embed(title="Mission Reward", description="Mission not completed or invalid ID!", color=discord.Color.red())

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Missions(bot))
