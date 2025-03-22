import discord
from discord.ext import commands
import os
import logging
from database import Database

from modules.database import Database

# Load environment variables (Railway automatically provides them)
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("discord_bot")

# Check if the bot token is set
if not TOKEN:
    logger.error("❌ DISCORD_BOT_TOKEN is missing. Please set it in Railway environment variables.")
    exit(1)

# Define bot prefix and intents
intents = discord.Intents.default()
intents.message_content = True  # Required for processing commands
bot = commands.Bot(command_prefix="!", intents=intents)

# Initialize database connection
db = Database()

@bot.event
async def on_ready():
    logger.info(f'✅ Logged in as {bot.user}')

# Load all command files from the 'commands' folder
def load_commands():
    command_folder = "commands"
    if not os.path.exists(command_folder):
        logger.warning(f"⚠️ Command folder '{command_folder}' not found. Skipping command loading.")
        return

    for filename in os.listdir(command_folder):
        if filename.endswith(".py"):
            try:
                bot.load_extension(f"{command_folder}.{filename[:-3]}")
                logger.info(f"✅ Loaded command: {filename}")
            except Exception as e:
                logger.error(f"❌ Failed to load {filename}: {e}")

# Load commands before starting the bot
load_commands()

# Run the bot
bot.run(TOKEN)
