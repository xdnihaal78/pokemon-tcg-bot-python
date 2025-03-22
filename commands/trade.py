import discord
from discord.ext import commands
import asyncpg

class Trade(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="trade")
    async def trade(self, ctx, member: discord.Member, my_pokemon: str, their_pokemon: str):
        """Propose a trade to another user"""
        if ctx.author == member:
            return await ctx.send("You can't trade with yourself!")

        db_pool: asyncpg.Pool = self.bot.db_pool
        user_id = ctx.author.id
        target_id = member.id

        async with db_pool.acquire() as conn:
            my_pokemon_exists = await conn.fetchval(
                "SELECT COUNT(*) FROM user_pokemon WHERE user_id = $1 AND pokemon_name = $2",
                user_id, my_pokemon
            )
            their_pokemon_exists = await conn.fetchval(
                "SELECT COUNT(*) FROM user_pokemon WHERE user_id = $1 AND pokemon_name = $2",
                target_id, their_pokemon
            )

        if not my_pokemon_exists:
            return await ctx.send(f"You don't own a **{my_pokemon}**!")
        if not their_pokemon_exists:
            return await ctx.send(f"{member.name} doesn't own a **{their_pokemon}**!")

        embed = discord.Embed(
            title="🔄 Trade Request",
            description=f"{ctx.author.mention} wants to trade their **{my_pokemon}** for {member.mention}'s **{their_pokemon}**.",
            color=discord.Color.blue()
        )
        embed.set_footer(text="React with ✅ to accept or ❌ to decline.")
        
        trade_message = await ctx.send(embed=embed)
        await trade_message.add_reaction("✅")
        await trade_message.add_reaction("❌")

        def check(reaction, user):
            return user == member and str(reaction.emoji) in ["✅", "❌"]

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)

            if str(reaction.emoji) == "✅":
                async with db_pool.acquire() as conn:
                    await conn.execute(
                        """
                        UPDATE user_pokemon 
                        SET user_id = CASE 
                            WHEN pokemon_name = $1 THEN $2 
                            WHEN pokemon_name = $3 THEN $4 
                        END
                        WHERE (user_id = $2 AND pokemon_name = $1) 
                           OR (user_id = $4 AND pokemon_name = $3)
                        """,
                        my_pokemon, target_id, their_pokemon, user_id
                    )

                await ctx.send(f"✅ Trade successful! {ctx.author.mention} traded **{my_pokemon}** for {member.mention}'s **{their_pokemon}**!")

            else:
                await ctx.send(f"❌ {member.mention} declined the trade.")

        except:
            await ctx.send("⏳ Trade request timed out.")

async def setup(bot):
    await bot.add_cog(Trade(bot))
