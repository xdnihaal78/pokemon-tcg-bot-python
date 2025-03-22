import discord
import asyncio
from discord.ext import commands
from database import Database  # ✅ Use Supabase Database class

# ✅ Initialize Database
db = Database()

class Trade(commands.Cog):
    """Handles Pokémon trading between users."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="trade")
    async def trade(self, ctx, member: discord.Member, my_pokemon: str, their_pokemon: str):
        """Propose a trade to another user."""
        if ctx.author == member:
            return await ctx.send("🚫 You can't trade with yourself!")

        if not my_pokemon.strip() or not their_pokemon.strip():
            return await ctx.send("⚠️ Invalid Pokémon names. Please specify valid Pokémon to trade.")

        user_id = str(ctx.author.id)  # ✅ Convert user IDs to strings for Supabase
        target_id = str(member.id)

        # ✅ Check if both users own the Pokémon
        my_pokemon_exists = await db.fetchval(
            "SELECT COUNT(*) FROM user_pokemon WHERE user_id = %s AND pokemon_name = %s",
            user_id, my_pokemon
        )
        their_pokemon_exists = await db.fetchval(
            "SELECT COUNT(*) FROM user_pokemon WHERE user_id = %s AND pokemon_name = %s",
            target_id, their_pokemon
        )

        if not my_pokemon_exists:
            return await ctx.send(f"❌ You don't own a **{my_pokemon}**!")
        if not their_pokemon_exists:
            return await ctx.send(f"❌ {member.name} doesn't own a **{their_pokemon}**!")

        # ✅ Create trade request embed
        embed = discord.Embed(
            title="🔄 Trade Request",
            description=f"{ctx.author.mention} wants to trade **{my_pokemon}** for {member.mention}'s **{their_pokemon}**.\n\n"
                        "React with ✅ to accept or ❌ to decline.",
            color=discord.Color.blue()
        )
        
        trade_message = await ctx.send(embed=embed)
        await trade_message.add_reaction("✅")
        await trade_message.add_reaction("❌")

        def check(reaction, user):
            return user == member and str(reaction.emoji) in ["✅", "❌"]

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)

            if str(reaction.emoji) == "✅":
                # ✅ Perform the trade in Supabase
                async with db.transaction():  # ✅ Ensure atomic transaction
                    await db.execute(
                        """
                        UPDATE user_pokemon 
                        SET user_id = CASE 
                            WHEN user_id = %s AND pokemon_name = %s THEN %s
                            WHEN user_id = %s AND pokemon_name = %s THEN %s
                        END
                        WHERE (user_id = %s AND pokemon_name = %s) 
                           OR (user_id = %s AND pokemon_name = %s)
                        """,
                        user_id, my_pokemon, target_id,  # Move my Pokémon to the other user
                        target_id, their_pokemon, user_id,  # Move their Pokémon to me
                        user_id, my_pokemon, target_id, their_pokemon  # Conditions for selection
                    )

                await ctx.send(f"✅ Trade successful! {ctx.author.mention} traded **{my_pokemon}** for {member.mention}'s **{their_pokemon}**!")

            else:
                await ctx.send(f"❌ {member.mention} declined the trade.")

        except asyncio.TimeoutError:  # ✅ Fixed TimeoutError
            await ctx.send("⏳ Trade request timed out.")
        except Exception as e:
            await ctx.send(f"⚠️ An unexpected error occurred: {str(e)}")

# ✅ Load the Trade Cog
async def setup(bot):
    await bot.add_cog(Trade(bot))
