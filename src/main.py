import client
import plex
import asyncio

#so that fucntions get included
import on_message
import commands

async def main():
    await asyncio.gather(client.start(), plex.run_server())

if __name__ == "__main__":
    asyncio.run(main())