import client
import plex
import asyncio

# so it gets ran
import on_message
import commands

async def main():
    await client.start()
    await plex.run_server()

if __name__ == "__main__":
    asyncio.run(main())