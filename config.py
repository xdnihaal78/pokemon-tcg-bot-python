import os
from dotenv import load_dotenv

# Load environment variables from Railway (or a .env file for local development)
load_dotenv()

# Discord Bot
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Supabase Credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Pokémon TCG API
POKEMON_TCG_API_KEY = os.getenv("POKEMON_TCG_API_KEY")

# Other Configuration Variables (if needed)
