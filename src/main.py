import logging

# Setup logging for discord.py
logging.basicConfig(level=logging.INFO)  # Or use logging.DEBUG for more detailed logs
discord_logger = logging.getLogger("discord")
discord_logger.setLevel(logging.INFO)

# Setup logging for plex or any other custom components
plex_logger = logging.getLogger("plex")
plex_logger.setLevel(logging.INFO)

# Rest of your imports
import client
import plex
import asyncio

# Including necessary functions
import on_message
import commands

async def main():
    await asyncio.gather(
        plex.run_server(),  # Running your custom server
        client.start()  # Starting the discord bot
    )

if __name__ == "__main__":
    # You don't need to pass `debug=True` here; logging is managed separately
    asyncio.run(main())
