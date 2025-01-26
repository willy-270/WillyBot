from typing import List, Dict, Any, Counter
from datetime import datetime
import aiohttp
import requests
from .consts import INVITE_CODE, OPEN_XPL_API_KEY

service_token = ""
prev_online_xuids = []
prev_online_gamertags = []

async def get_gamertags(xuids: List[str], prev_online_gamertags: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not xuids:
        return []

    print(f"Getting gamertags for {xuids}")

    headers = {'x-authorization': OPEN_XPL_API_KEY}
    url = f'https://xbl.io/api/v2/account/{",".join(xuids)}'

    response = requests.get(url=url, headers=headers)
    response_data = response.json()

    gamertags = []

    if len(xuids) > 1:
        people = response_data.get("people", [])

        for person in people:
            gamertag_dict = {"gamertag": person["gamertag"]}
            # Check if this person was already online
            previous_entry = next(
                (player for player in prev_online_gamertags if player["gamertag"] == person["gamertag"]), None
            )

            gamertag_dict["time_joined"] = previous_entry["time_joined"] if previous_entry else datetime.now()
            gamertags.append(gamertag_dict)

    else:
        # Handling for a single XUID
        profile_users = response_data.get("profileUsers", [])
        if profile_users:
            gamertag = profile_users[0]["settings"][2]["value"]  # Assuming correct index
            gamertag_dict = {"gamertag": gamertag}

            previous_entry = next(
                (player for player in prev_online_gamertags if player["gamertag"] == gamertag), None
            )

            gamertag_dict["time_joined"] = previous_entry["time_joined"] if previous_entry else datetime.now()
            gamertags.append(gamertag_dict)

    return gamertags

async def get_club_id() -> str:
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

    return r.get("clubId", "")

async def get_online_xuids() -> List[str]:
    club_id = await get_club_id()
    url = f'https://xbl.io/api/v2/clubs/3379895950550166'

    headers = {"x-authorization": OPEN_XPL_API_KEY}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url, headers=headers) as response:
                r = await response.json()
    except Exception as e:
        print(f"Error in get_online_xuids: {e}")
        print(r.text)
        return []

    online_xuids = []
    members = r.get("clubs", [{}])[0].get("clubPresence", [])

    for member in members:
        if member.get("lastSeenState") == "InGame":
            online_xuids.append(member["xuid"])

    return online_xuids

def compare(s: List[Any], t: List[Any]) -> bool:
    return Counter(s) == Counter(t)

async def get_online_gamertags() -> List[Dict[str, Any]]:
    global prev_online_xuids, prev_online_gamertags

    online_xuids = await get_online_xuids()

    if compare(online_xuids, prev_online_xuids):
        return prev_online_gamertags

    prev_online_xuids = online_xuids
    online_gamertags = await get_gamertags(online_xuids, prev_online_gamertags)
    prev_online_gamertags = online_gamertags

    return online_gamertags