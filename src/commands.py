import json
import os
import random
from discord.ext import tasks
from datetime import datetime, time

import requests
from minecraft import minecraft, minecraft_auth
import discord
from client import bot
import operator
import numpy as np
import matplotlib.pyplot as plt
from consts import OWNER_ID, LOG_CHANNEL_ID, OPENAI_KEY, TENOR_API_KEY, MEALS_CHANNEL_ID
from sympy import lambdify, sqrt
from sympy.parsing.sympy_parser import (parse_expr, standard_transformations,
                                         implicit_multiplication_application,
                                         implicit_application)
from openai import OpenAI


running = False
player_list = discord.Message

@bot.tree.command(
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

    minecraft.service_token = minecraft_auth.get_service_token()
    await update_list.start()


prev_gamertags = []

@tasks.loop(minutes=1)
async def update_list():
    global player_list
    global prev_gamertags
    
    gamertags = await minecraft.get_online_gamertags()
    gamertags.sort(key=operator.itemgetter('gamertag'))

    join_leave_logs_id = LOG_CHANNEL_ID
    join_leaves = bot.get_channel(join_leave_logs_id)

    just_gamertags = []
    for player in gamertags:
        just_gamertags.append(player["gamertag"])
        
    if just_gamertags != prev_gamertags:
        log = discord.Embed()

        joined_players = set(just_gamertags) - set(prev_gamertags)
        left_players = set(prev_gamertags) - set(just_gamertags)

        if joined_players:
            log.description = f"{' & '.join([f'**{player}**' for player in joined_players])} joined the realm!"
            log.color = discord.Color.green()
            await join_leaves.send(embed=log) 

        if left_players:
            log.description = f"{' & '.join([f'**{player}**' for player in left_players])} left the realm!"
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
        if "🔴no-players-online" != player_list.channel.name:
            await player_list.channel.edit(name="🔴no-players-online")
        return

    r.title = "**Current Online Players:**"
    r.color = discord.Color.green() 

    for player in gamertags:
        time_now = datetime.now()
        time_joined = player["time_joined"]

        time_since_join = time_now - time_joined
        seconds_since_join = time_since_join.total_seconds()

        if seconds_since_join < 60:
            r.description += f"• **{player['gamertag']}** for < 1min\n"
        elif seconds_since_join < 3600:
            r.description += f"• **{player['gamertag']}** for {int(seconds_since_join // 60)}min\n"
        else:
            hours = int(seconds_since_join // 3600)
            minutes = int((seconds_since_join % 3600) // 60)
            if minutes == 0:
                r.description += f"• **{player['gamertag']}** for {hours}hr\n"
            else:
                r.description += f"• **{player['gamertag']}** for {hours}hr {minutes}min\n"
        

    r.set_footer(text=f"as of {datetime.today().strftime('%I:%M %p')}")
    await player_list.edit(embed=r)

    if f"🟢{len(gamertags)}-players-online" != player_list.channel.name:
        if len(gamertags) == 1:
            await player_list.channel.edit(name=f"🟢{len(gamertags)}-player-online")
        else:
            await player_list.channel.edit(name=f"🟢{len(gamertags)}-players-online")
    

@bot.tree.command(
    name = "test", 
    description = "yep",
)
async def self(
    interaction: discord.Interaction,
    user: discord.User,
    msg: str
):
    owner = await bot.fetch_user(OWNER_ID)

    await owner.send(f"{interaction.user}: {msg} \nto {user}")
    await user.send(msg)
    
    await interaction.response.send_message("done", ephemeral=True)


@bot.tree.command(
    name="graph",
    description="Graph a function. Use 'sqrt(x)' for square root, 'log(x)' for log, etc."
)
@discord.app_commands.describe(
    function="exclude \"y=\"/\"f(x)=\", give just the expression. Example: \"sin(x)\", or \"x+3\"."
)
async def self(
    interaction: discord.Interaction,
    function: str,
    ymin: int = -10,
    ymax: int = 10,
    xmin: int = -10,
    xmax: int = 10,
    points_on_whole_nums: bool = False,
    show_grid: bool = True
):
    modified_function = function.replace("^", "**")

    transformations = standard_transformations + (implicit_multiplication_application,) + (implicit_application,)

    try:
        expr = parse_expr(modified_function, transformations=transformations)
        f = lambdify('x', expr, modules=['numpy', {'sqrt': np.sqrt, 
                                                   'log': np.log10, 
                                                   'sin': np.sin, 
                                                   'cos': np.cos, 
                                                   'tan': np.tan}])
        x = np.linspace(xmin, xmax, 100)
        y = f(x)
        plt.plot(x, y, color='c')
    except Exception as e:
        await interaction.response.send_message(f"Error evaluating the function.")
        return

    plt.axis([xmin, xmax, ymin, ymax])
    if show_grid:
        plt.grid(True, which='both', linestyle='-', linewidth=0.5)
    plt.xticks(np.arange(xmin, xmax+1, (xmax-xmin)/10))
    plt.yticks(np.arange(ymin, ymax+1, (ymax-ymin)/10))
    plt.axhline(0, color='k')
    plt.axvline(0, color='k')
    plt.xlabel('x')
    plt.ylabel('y', rotation=0, labelpad=10)
    plt.title(f"$f(x)={function}$")

    if points_on_whole_nums:
        for i in range(xmin, xmax+1):
            if f(i) % 1 == 0:
                plt.plot(i, f(i), "ko", markersize=5)

    plt.gca().set_aspect('equal', adjustable='box')

    plt.savefig("graph.png")
    file = discord.File("graph.png")
    await interaction.response.send_message(file=file)
    os.remove("graph.png")
    plt.clf()

client = OpenAI(api_key=OPENAI_KEY)

@bot.tree.command(
    name="ask",
    description="ask stuff"
)
async def ask(
    interaction: discord.Interaction, 
    prompt: str
):
    await interaction.response.defer(thinking=True)

    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-3.5-turbo",
        )

        await interaction.edit_original_response(content=chat_completion.choices[0].message.content)
    
    except Exception as e:
        await interaction.edit_original_response(content="Error: " + str(e))

tz = datetime.now().astimezone().tzinfo
morning = time(hour=7, minute=5, second=0, microsecond=0, tzinfo=tz)

@bot.tree.command(
    name="random_quote",
    description="oh yeah"
)
async def quote(
    interaction: discord.Interaction
):
    r = requests.get("https://zenquotes.io/api/random")
    if r.status_code == 200:
        r = r.json()
        await interaction.response.send_message(f'{r[0]["q"]} — {r[0]["a"]}')
    else:
        await interaction.response.send_message("Error")
        await interaction.response.send_message(f"Error: {r.status_code}")

@bot.tree.command(
    name="purge",
    description="purge messages"
)
async def purge(
    interaction: discord.Interaction,
    amount: int
):
    if interaction.user.id == OWNER_ID:
        await interaction.channel.purge(limit=amount)
    else:
        await interaction.response.send_message("only big willy can do that.", ephemeral=True)

@tasks.loop(time=morning)
async def good_morning():
    meals_channel = bot.get_channel(MEALS_CHANNEL_ID)

    lmt = 10
    search_term = f"goodmorning {datetime.today().strftime('%A').lower()}"
    r = requests.get("https://tenor.googleapis.com/v2/search?q=%s&key=%s&limit=%s" % (search_term, TENOR_API_KEY, lmt))
    if r.status_code == 200:
        i = random.randint(0, lmt-1)
        r = r.json()
        gif_url = r["results"][i]["media_formats"]["mediumgif"]["url"]
        await meals_channel.send(gif_url)
    else:
        await meals_channel.send(f"Error: {r.status_code}")

    r = requests.get("https://zenquotes.io/api/random")
    if r.status_code == 200:
        r = r.json()
        await meals_channel.send(f'{r[0]["q"]} — {r[0]["a"]}')
    else:
        await meals_channel.send("Error")
        await meals_channel.send(f"Error: {r.status_code}")
