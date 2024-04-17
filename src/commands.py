from discord.ext import tasks
from datetime import datetime, time
from minecraft import minecraft, minecraft_auth
from AI import ai
import discord
import client
import random
import operator
from consts import OWNER_ID, LOG_CHANNEL_ID, PLAYER_LIST_CHANNEL_ID
import plex


@client.bot.tree.command(
    name = "ask", 
    description = "ask thing", 
)
async def self(
    interaction: discord.Interaction, 
    input: str
):
    await interaction.response.send_message("Thinking...")

    try:
        response = ai.get_reponse(input)
    except Exception as e:
        await interaction.edit_original_response(content=f"Something went wrong!, {e}")

    await interaction.edit_original_response(content=response)


running = False
player_list = discord.Message

@client.bot.tree.command(
    name = "toggle_player_list", 
    description = "yep",
)
async def self(
    interaction: discord.Interaction,
):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("fuck you landan", ephemeral=True)
        return

    global running
    global player_list

    if running == True:
        running = False
        update_list.cancel()
        await player_list.delete()
        await interaction.response.send_message("Stopped!", ephemeral=True)
        return
    
    running = True

    r = discord.Embed(
        title="Thinking... (this will take around 20s)"
    )
    await interaction.response.send_message("done", ephemeral=True)
    player_list = await interaction.channel.send(embed=r)

    while running == True:
        minecraft.service_token = minecraft_auth.get_service_token()
        await update_list.start()
        prev_embed = player_list.embeds[0]
        await player_list.delete()
        player_list = await interaction.channel.send(embed=prev_embed)


prev_gamertags = []

@tasks.loop(minutes=1, count=720)
async def update_list():
    print(f"updating list...")

    global player_list
    global prev_gamertags
    
    gamertags = await minecraft.get_online_gamertags()
    gamertags.sort(key=operator.itemgetter('gamertag'))

    join_leave_logs_id = LOG_CHANNEL_ID
    join_leaves = client.bot.get_channel(join_leave_logs_id)

    just_gamertags = []
    for player in gamertags:
        just_gamertags.append(player["gamertag"])
        
    if just_gamertags != prev_gamertags:
        log = discord.Embed()

        joined_players = set(just_gamertags) - set(prev_gamertags)
        left_players = set(prev_gamertags) - set(just_gamertags)

        if joined_players:
            log.description = f"**{' & '.join(joined_players)}** joined the realm!"
            log.color = discord.Color.green()
            await join_leaves.send(embed=log) 

        if left_players:
            log.description = f"**{' & '.join(left_players)}** left the realm!"
            log.color = discord.Color.red()
            await join_leaves.send(embed=log) 

        prev_gamertags = just_gamertags

    r = discord.Embed()
    r.description = ""
    r.set_thumbnail(url="https://www.pngkit.com/png/full/182-1827420_block-of-grass-from-the-game-minecraft-minecraft.png")

    if len(gamertags) == 0:
        r.title = "No One Online!"
        r.description = "You should get on."
        r.color = discord.Color.red()
        r.set_footer(text=f"as of {datetime.today().strftime('%I:%M %p')}")
        await player_list.edit(embed=r)
        return

    r.title = "**Current Online Players:**"
    r.color = discord.Color.green() 

    for player in gamertags:
        time_now = datetime.now()
        time_joined = player["time_joined"]

        time_since_join = time_now - time_joined
        seconds_since_join = time_since_join.total_seconds()

        if seconds_since_join < 60:
            r.description += f"• **{player['gamertag']}** for < 1min"
        elif seconds_since_join >= 60:
            r.description += f"• **{player['gamertag']}** for {int(seconds_since_join // 60)}min(s)"
        else:
            r.description += f"• **{player['gamertag']}** for {int(seconds_since_join // 3600)}hr(s) and {int((seconds_since_join % 3600) // 60)}min(s)"
        

    r.set_footer(text=f"as of {datetime.today().strftime('%I:%M %p')}")
    print(f"list updated on {datetime.today().strftime('%I:%M %p')}")
    await player_list.edit(embed=r)
    

@client.bot.tree.command(
    name = "test", 
    description = "yep",
)
async def self(
    interaction: discord.Interaction,
    user: discord.User,
    msg: str
):
    owner = await client.bot.fetch_user(OWNER_ID)

    await owner.send(f"{interaction.user}: {msg} \nto {user}")
    await user.send(msg)
    
    await interaction.response.send_message("done", ephemeral=True)


@client.bot.tree.command(
    name = "ping_random_member", 
    description = "yep",
)
async def self(
    interaction: discord.Interaction,
):
    members = interaction.guild.members
    chosen = random.choice(members)
    
    await interaction.response.send_message(content=chosen.mention)

@client.bot.tree.command(
    name = "shutdown",
    description = "yep",
)
async def self(
    interaction: discord.Interaction,
):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("You can't do that!", ephemeral=True)
        return
    await interaction.response.send_message("Shutting down...", ephemeral=True)
    await client.bot.close()

# alex_msgs_left = 3
# alex_id = 905459622884814868

# tz = datetime.now().astimezone().tzinfo
# midnight = time(hour=0, minute=0, second=0, microsecond=0, tzinfo=tz)

# @tasks.loop(time=midnight)
# async def reset_alex_msgs():
#     global alex_msgs_left
#     alex_msgs_left = 3

@client.bot.event 
async def on_message(message):
    if isinstance(message.channel,discord.DMChannel) and message.author != client.bot.user:
        user = message.author
        name = user.display_name

        willy_user = await client.bot.fetch_user(OWNER_ID)
        await willy_user.send(f"{name}: {message.content}")

    if message.channel.id == PLAYER_LIST_CHANNEL_ID and message.author != client.bot.user and message.author.id != OWNER_ID:
        await message.author.send("GET THE FUCK OUT OF MY CHANNEL")
        await message.delete()

    msg_lower = message.content.lower()
    if "skibidi" in msg_lower and message.author != client.bot.user:
        await message.reply("SKIBIDI TOILET RIZZ IN OHIO?!!!?!? https://images.sftcdn.net/images/t_app-cover-l,f_auto/p/4f7aac60-2de4-47e6-94f1-2f642827824c/1253432816/skibidi-toilet-1-screenshot.png")  

    global alex_msgs_left

    # if message.author.id == alex_id:
    #     if alex_msgs_left > 0:
    #         alex_msgs_left -= 1
    #         await message.reply(f"Messages left today: {alex_msgs_left}")
    #     else:
    #         await message.delete()

        
