from typing import Counter
from datetime import datetime
import aiohttp
import requests
from .consts import INVITE_CODE, OPEN_XPL_API_KEY

service_token = ""
prev_online_xuids = []
prev_online_gamertags = []

async def get_gamertags(xuids) -> dict["gamertag": str, "time_joined": datetime]:
    if len(xuids) == 0:
        return []

    headers = {
        'x-authorization': OPEN_XPL_API_KEY,
    }

    params = {
        "xuids": xuids
    }

    url = f'https://xbl.io/api/v2/account/{",".join(xuids)}'

    r = requests.get(url=url, headers=headers, params=params)
    r = r.json()

    gamertags = []
    global prev_online_gamertags

    if len(xuids) > 1:
        people = r["people"]

        for person in people:
            in_prev = any(person["gamertag"] in player.values() for player in prev_online_gamertags)

            gamertag_dict = {}
            gamertag_dict["gamertag"] = person["gamertag"]

            if in_prev == False:
                gamertag_dict["time_joined"] = datetime.now()
            else:
                gamertag_dict["time_joined"] = [player["time_joined"] for player in prev_online_gamertags if player["gamertag"] == person["gamertag"]][0]
            
            gamertags.append(gamertag_dict)
    else:
        gamertag_dict = {}
        gamertag_dict["gamertag"] = r["profileUsers"][0]["settings"][2]["value"] #response when one xuid is passed is different
        in_prev = any(gamertag_dict["gamertag"] in player.values() for player in prev_online_gamertags)
        if in_prev == False:
            gamertag_dict["time_joined"] = datetime.now()
        else:
            gamertag_dict["time_joined"] = [player["time_joined"] for player in prev_online_gamertags if player["gamertag"] == person["gamertag"]][0]
        gamertags.append(gamertag_dict)

    return gamertags

async def get_club_id():
    url = f"https://pocket.realms.minecraft.net/worlds/v1/link/{INVITE_CODE}"

    headers = {
        "Accept": "*/*",
        "Authorization": "XBL3.0 x=" + service_token,
        "Cache-Control": "no-cache",
        "Charset": "utf-8",
        "Client-Version": "1.20.32",
        "User-Agent": "MCPE/UWP",
        "Accept-Language": "en-GB",
        "Accept-Encoding": "gzip, deflate, br",
        "Host": "pocket.realms.minecraft.net",
        "Connection": "Keep-Alive",
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers=headers) as response:
            r = await response.json()

    club_id = r["clubId"]

    return club_id

async def get_online_xuids():
    club_id = await get_club_id()

    url = f'https://xbl.io/api/v2/clubs/{club_id}'
    params = {
        "clubId": club_id
    }
    headers = {
        "x-authorization": OPEN_XPL_API_KEY
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url, headers=headers, params=params) as response:
                r = await response.json()
    except Exception as e:
        print(f"Error in get_online_xuids: {e}")

    online_xuids = []
    members = r["clubs"][0]["clubPresence"]

    for member in members:
        if member["lastSeenState"] == "InGame":
            online_xuids.append(member["xuid"])

    return online_xuids

def compare(s, t):
    return Counter(s) == Counter(t)

async def get_online_gamertags() -> dict["gamertag": str, "time_joined": datetime]:
    global prev_online_xuids
    global prev_online_gamertags

    online_xuids = await get_online_xuids()

    if compare(online_xuids, prev_online_xuids) == True:
        return prev_online_gamertags
    else:
        prev_online_xuids = online_xuids

    online_gamertags = await get_gamertags(online_xuids)
    prev_online_gamertags = online_gamertags

    return online_gamertags

