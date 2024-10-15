from consts import PLAYER_LIST_CHANNEL_ID, OWNER_ID, HALL_OF_SHAME_CHANNEL_ID
from client import bot
import discord
from datetime import datetime
from pytz import timezone

# alex_msgs_left = 3
# alex_id = 905459622884814868

# tz = datetime.now().astimezone().tzinfo
# midnight = time(hour=0, minute=0, second=0, microsecond=0, tzinfo=tz)

# @tasks.loop(time=midnight)
# async def reset_alex_msgs():
#     global alex_msgs_left
#     alex_msgs_left = 3

@bot.event 
async def on_message(message: discord.Message):
    if isinstance(message.channel,discord.DMChannel) and message.author != bot.user:
        user = message.author
        name = user.display_name

        willy_user = await bot.fetch_user(OWNER_ID)
        await willy_user.send(f"{name}: {message.content}")

    if message.channel.id == PLAYER_LIST_CHANNEL_ID and message.author != bot.user and message.author.id != OWNER_ID:
        await message.author.send("GET THE FUCK OUT OF MY CHANNEL")
        await message.delete()

    msg_lower = message.content.lower()
    if "skibidi" in msg_lower and message.author != bot.user:
        await message.reply("SKIBIDI TOILET RIZZ IN OHIO?!!!?!")  
        await message.channel.send("https://images.sftcdn.net/images/t_app-cover-l,f_auto/p/4f7aac60-2de4-47e6-94f1-2f642827824c/1253432816/skibidi-toilet-1-screenshot.png")

    if "nigger" in msg_lower:
        embed = discord.Embed(title=message.author.display_name, 
                              description=f"{message.content}\n\n{message.jump_url}",
                              color=discord.Color.red())
        embed.set_thumbnail(url=message.author.avatar.url)
        embed.set_footer(text=f"{message.created_at.replace(tzinfo=timezone('UTC')).astimezone(timezone('America/Chicago')).strftime('%-m/%-d/%Y, %-I:%M %p')}")
        hos_msg = await bot.get_channel(HALL_OF_SHAME_CHANNEL_ID).send(embed=embed)

        await message.reply(f"This will not be forgetten.\n{hos_msg.jump_url}")
        

    # global alex_msgs_left

    # if message.author.id == alex_id:
    #     if alex_msgs_left > 0:
    #         alex_msgs_left -= 1
    #         await message.reply(f"Messages left today: {alex_msgs_left}")
    #     else:
    #         await message.delete()
