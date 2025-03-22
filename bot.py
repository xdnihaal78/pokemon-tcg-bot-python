import os
import discord
from discord.ext import commands
import asyncio
from dotenv import load_dotenv
from database import Database  # ✅ Import Database class

# Load environment variables
load_dotenv()

# Bot configuration
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
COMMANDS_FOLDER = "commands"

# Check if token is set
if not DISCORD_TOKEN:
    raise ValueError("❌ DISCORD_TOKEN is missing! Check your .env file.")

# Intents setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Initialize bot
bot = commands.Bot(command_prefix="!", intents=intents)
db = Database()  # ✅ Initialize the database instance

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    await load_extensions()

async def load_extensions():
    """Loads all command extensions (cogs)."""
    command_folder = os.path.join(os.path.dirname(__file__), COMMANDS_FOLDER)

    for filename in os.listdir(command_folder):
        if filename.endswith(".py") and not filename.startswith("_"):
            extension = f"{COMMANDS_FOLDER}.{filename[:-3]}"
            try:
                await bot.load_extension(extension)  # ✅ Properly awaited
                print(f"✅ Loaded command: {filename}")
            except Exception as e:
                print(f"❌ Failed to load {filename}: {e}")

async def main():
    """Main function to start the bot and connect to the database."""
    try:
        print("🔄 Connecting to database...")
        await db.connect()  # ✅ Connect to the database before starting the bot
        print("✅ Database connection successful!")

        async with bot:
            print("🚀 Starting bot...")
            await bot.start(DISCORD_TOKEN)

    except discord.LoginFailure:
        print("❌ Invalid DISCORD_TOKEN! Please check your .env file.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        print("🔄 Disconnecting database...")
        await db.disconnect()
        print("✅ Database disconnected.")

if __name__ == "__main__":
    try:
        asyncio.run(main())  # ✅ Ensures the bot starts safely
    except RuntimeError:  
        # Fix issue where event loop is already running
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
