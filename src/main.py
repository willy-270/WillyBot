from client import start
from plex import run_server
import asyncio

#so that fucntions get included
import on_message
import commands

async def main():
    await asyncio.gather(start(), run_server())

if __name__ == "__main__":
    asyncio.run(main())
    


