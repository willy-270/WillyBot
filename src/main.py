import client
import plex
import asyncio

#so that fucntions get included
import on_message
import commands

def main():
    # await asyncio.gather(client.start(), plex.run_server())
    client.start()

if __name__ == "__main__":
    # asyncio.run(main(), debug=True)
    main()