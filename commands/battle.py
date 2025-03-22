import random
from database import get_user_pokemon, get_pokemon_stats, update_user_wins, update_user_losses
from discord import Embed

async def battle(ctx, opponent):
    """Initiates a battle between two users based on their Pokémon stats."""
    
    # Get challenger and opponent
    challenger_id = ctx.author.id
    opponent_id = opponent.id

    # Fetch Pokémon for both players
    challenger_pokemon = get_user_pokemon(challenger_id)
    opponent_pokemon = get_user_pokemon(opponent_id)

    if not challenger_pokemon or not opponent_pokemon:
        await ctx.send("Both players must own at least one Pokémon to battle!")
        return

    # Select random Pokémon for battle
    challenger_pokemon_id = random.choice(challenger_pokemon)
    opponent_pokemon_id = random.choice(opponent_pokemon)

    # Fetch Pokémon stats
    challenger_stats = get_pokemon_stats(challenger_pokemon_id)
    opponent_stats = get_pokemon_stats(opponent_pokemon_id)

    if not challenger_stats or not opponent_stats:
        await ctx.send("Error retrieving Pokémon stats. Please try again later.")
        return

    # Battle calculations
    challenger_attack = challenger_stats["attack"]
    challenger_defense = challenger_stats["defense"]
    opponent_attack = opponent_stats["attack"]
    opponent_defense = opponent_stats["defense"]

    challenger_damage = max(1, challenger_attack - opponent_defense)
    opponent_damage = max(1, opponent_attack - challenger_defense)

    # Determine winner
    if challenger_damage > opponent_damage:
        winner = ctx.author
        loser = opponent
        update_user_wins(challenger_id)
        update_user_losses(opponent_id)
    elif opponent_damage > challenger_damage:
        winner = opponent
        loser = ctx.author
        update_user_wins(opponent_id)
        update_user_losses(challenger_id)
    else:
        winner = None

    # Embed battle result
    embed = Embed(title="Pokémon Battle!", color=0x00ff00)
    embed.add_field(name=f"{ctx.author.display_name}'s Pokémon", value=f"{challenger_stats['name']} (ATK: {challenger_attack}, DEF: {challenger_defense})", inline=True)
    embed.add_field(name=f"{opponent.display_name}'s Pokémon", value=f"{opponent_stats['name']} (ATK: {opponent_attack}, DEF: {opponent_defense})", inline=True)
    
    if winner:
        embed.add_field(name="Winner!", value=f"🏆 {winner.display_name} wins!", inline=False)
    else:
        embed.add_field(name="Result", value="It's a draw!", inline=False)

    await ctx.send(embed=embed)
