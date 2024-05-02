from quart import Quart, request
from consts import PORT, PLEX_CHANNEL_ID
import json
import os
import client
import discord

app = Quart(__name__)


@app.route('/plex_wh', methods=['POST'])
async def receive_data():
    form = await request.form
    files = await request.files
    payload = form['payload']
    data = json.loads(payload)
    
    if files:
        img = files["thumb"]
        await img.save("src/thumb.jpg")

        if data["event"] == "library.new":
            await handle_new_addtition(data)
        elif data["event"] == "media.play":
            await handle_play(data)

    return 'Data received successfully!', 200

async def handle_new_addtition(data):
    title = data["Metadata"]["title"]
    file = discord.File("src/thumb.jpg", filename="thumb.jpg")

    embed = discord.Embed()
    embed.title = "Movie added"
    embed.description = f"**{title}**"
    embed.color = discord.Color.green()
    embed.set_thumbnail(url="attachment://thumb.jpg")
    
    channel = client.bot.get_channel(PLEX_CHANNEL_ID)
    await channel.send(embed=embed, file=file)

    os.remove("src/thumb.jpg")

async def handle_play(data):
    title = data["Metadata"]["title"]
    user = data["Account"]["title"]
    file = discord.File("src/thumb.jpg", filename="thumb.jpg")

    embed = discord.Embed()
    embed.title = "Movie played"
    embed.description = f"**{user}** is watching **{title}**"
    embed.color = discord.Color.yellow()
    embed.set_thumbnail(url="attachment://thumb.jpg")

    channel = client.bot.get_channel(PLEX_CHANNEL_ID)
    await channel.send(embed=embed, file=file)

    os.remove("src/thumb.jpg")

async def run_server():
    print("Starting plex listener")
    await app.run_task(host="0.0.0.0", port=PORT)