import io
from consts import PLAYER_LIST_CHANNEL_ID, OWNER_ID, HALL_OF_SHAME_CHANNEL_ID, HALL_OF_FAME_CHANNEL_ID
from client import bot
import discord
from datetime import datetime
from pytz import timezone
import aiohttp

# alex_msgs_left = 3
# alex_id = 905459622884814868

# tz = datetime.now().astimezone().tzinfo
# midnight = time(hour=0, minute=0, second=0, microsecond=0, tzinfo=tz)

# @tasks.loop(time=midnight)
# async def reset_alex_msgs():
#     global alex_msgs_left
#     alex_msgs_left = 3

async def make_quote_embed(message: discord.Message, hof: bool) -> dict["embeds": list[discord.Embed], "files": list[discord.File]]:
    main_embed = discord.Embed(title=message.author.display_name, 
                          description=f"{message.content}\n\n[Jump to message]({message.jump_url})",
                          color=discord.Color.green() if hof else discord.Color.red())

    async with aiohttp.ClientSession() as session:
        async with session.get(message.author.guild_avatar.url if message.author.guild_avatar else message.author.display_avatar.url) as resp:
            img = await resp.read() 
            with io.BytesIO(img) as file:
                pfp = discord.File(file, 'testimage.png')
                main_embed.set_thumbnail(url=f"attachment://{pfp.filename}")
                await session.close()

    main_embed.set_footer(text=f"{message.created_at.replace(tzinfo=timezone('UTC')).astimezone(timezone('America/Chicago')).strftime('%-m/%-d/%Y, %-I:%M %p')}")

    embeds = [main_embed]
    other_attatchments = [pfp]

    idx = 0
    for attatchment in message.attachments:
        if "image" in attatchment.content_type:
            if idx == 0:
                main_embed.set_image(url=attatchment.url)
                if message.content == "":
                    main_embed.description += "\n ‎"
            else:
                image_embed = discord.Embed()
                image_embed.color = discord.Color.green() if hof else discord.Color.red()
                image_embed.set_image(url=attatchment.url)
                embeds.append(image_embed)
        else:
            other_attatchments.append(await attatchment.to_file())
        idx += 1

    return {"embeds": embeds, "files": other_attatchments}

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
        content = await make_quote_embed(message, False)

        hos_msg = await bot.get_channel(HALL_OF_SHAME_CHANNEL_ID).send(embeds=content["embeds"], files=content["files"])
        await message.reply(f"This will not be forgotten.\n{hos_msg.jump_url}")

    blacklisted_phrases = [
        "freedom",
        "taiwan",
        "tiananmen",
        "democracy",
        "diplomatic",
        "winne the pooh",
        "disagree",
        "human rights",
        "tiananmen square",
        "1989",
        "hong kong",
        "june 4th",
        "free blake",
        "blake",
        "censorship",
        "i hate my glorious leader",
        "free"
    ]

    if any(phrase in msg_lower for phrase in blacklisted_phrases):
        webhook = await message.channel.create_webhook(name=message.author.name)

        new_msg = msg_lower
        for phrase in blacklisted_phrases:
            if phrase in msg_lower:
                new_msg = new_msg.replace(phrase, "||[REDACTED]||")

        await webhook.send(
            str(new_msg), username=message.author.display_name, avatar_url=message.author.guild_avatar.url if message.author.guild_avatar else message.author.display_avatar.url)

        webhooks = await message.channel.webhooks()
        for webhook in webhooks:
                await webhook.delete()

        await message.delete()
        
    # global alex_msgs_left

    # if message.author.id == alex_id:
    #     if alex_msgs_left > 0:
    #         alex_msgs_left -= 1
    #         await message.reply(f"Messages left today: {alex_msgs_left}")
    #     else:
    #         await message.delete()

@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    if str(payload.emoji) != "🔥":
        return
    message = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
    if len(message.embeds) > 0:
        return

    owner = False
    for reaction in message.reactions:
        if str(reaction.emoji) == "🔥": 
            async for user in reaction.users():
                if user.id == OWNER_ID:
                    owner = True
                    break
                if user.id == bot.user.id:
                    return
            if owner == True:
                break
            if reaction.count != 2:
                return      

    content = await make_quote_embed(message, True)

    hof_msg = await bot.get_channel(HALL_OF_FAME_CHANNEL_ID).send(embeds=content["embeds"], files=content["files"])

    await message.add_reaction("🔥")
    await message.reply(f"Added to hall of fame.\n{hof_msg.jump_url}", mention_author=False)

