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
            return await ctx.send("🚫 You can't trade with yourself!")

        if not my_pokemon.strip() or not their_pokemon.strip():
            return await ctx.send("⚠️ Invalid Pokémon names. Please specify valid Pokémon to trade.")

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
            return await ctx.send(f"❌ You don't own a **{my_pokemon}**!")
        if not their_pokemon_exists:
            return await ctx.send(f"❌ {member.name} doesn't own a **{their_pokemon}**!")

        # Create trade request embed
        embed = discord.Embed(
            title="🔄 Trade Request",
            description=f"{ctx.author.mention} wants to trade their **{my_pokemon}** for {member.mention}'s **{their_pokemon}**.\n\n"
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
                async with db_pool.acquire() as conn:
                    async with conn.transaction():
                        # Swap Pokémon between users
                        await conn.execute(
                            """
                            UPDATE user_pokemon 
                            SET user_id = CASE 
                                WHEN user_id = $1 AND pokemon_name = $2 THEN $3
                                WHEN user_id = $3 AND pokemon_name = $4 THEN $1
                            END
                            WHERE (user_id = $1 AND pokemon_name = $2) 
                               OR (user_id = $3 AND pokemon_name = $4)
                            """,
                            user_id, my_pokemon, target_id, their_pokemon
                        )

                await ctx.send(f"✅ Trade successful! {ctx.author.mention} traded **{my_pokemon}** for {member.mention}'s **{their_pokemon}**!")

            else:
                await ctx.send(f"❌ {member.mention} declined the trade.")

        except TimeoutError:
            await ctx.send("⏳ Trade request timed out.")
        except asyncpg.PostgresError as e:
            await ctx.send(f"⚠️ Database error: {str(e)}")
        except Exception as e:
            await ctx.send(f"⚠️ An unexpected error occurred: {str(e)}")

async def setup(bot):
    await bot.add_cog(Trade(bot))
