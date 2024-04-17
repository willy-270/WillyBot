import client
import commands
import plex
import asyncio

async def main():
    bot_task = asyncio.create_task(client.bot.start(client.BOT_TOKEN))
    await plex.run_server()
    await bot_task

if __name__ == "__main__":
    asyncio.run(main())