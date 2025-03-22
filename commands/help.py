import discord
from discord.ext import commands

class HelpCommand(commands.Cog):
    """Help command cog for displaying available bot commands."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="customhelp")
    async def help_command(self, ctx):
        """Displays the help menu with all available commands in an embed."""
        
        embed = discord.Embed(
            title="📜 Pokémon TCG Bot Commands",
            description="Here are all the available commands:",
            color=0xFFD700
        )

        embed.add_field(name="📦 `!openpack`", value="Opens a Pokémon card pack.", inline=False)
        embed.add_field(name="⚔ `!battle @user`", value="Battle another trainer using your Pokémon.", inline=False)
        embed.add_field(name="📜 `!missions`", value="Check your available missions.", inline=False)
        embed.add_field(name="🏆 `!leaderboard`", value="View the top trainers.", inline=False)
        embed.add_field(name="👤 `!profile`", value="Check your trainer profile and stats.", inline=False)
        embed.add_field(name="🎲 `!wonderpick`", value="Pick a random Pokémon with some luck involved!", inline=False)
        embed.add_field(name="🔄 `!trade @user [pokemon_name]`", value="Trade Pokémon with another trainer.", inline=False)
        embed.add_field(name="📖 `!pokemon [name]`", value="View details of a specific Pokémon.", inline=False)

        embed.set_footer(text="Use these commands to become the ultimate Pokémon trainer!")

        await ctx.send(embed=embed)

# Add this cog to the bot
async def setup(bot):
    await bot.add_cog(HelpCommand(bot))
