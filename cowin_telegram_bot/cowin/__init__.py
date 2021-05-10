#!/usr/bin/env python
from typing import Any, Dict

import aiohttp
import datetime
import asyncio


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
}
NUMDAY = 10
COWIN_API = (
    # "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByDistrict"
    # "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByPin?pincode=110001&date=20-05-2021"
    "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByPin"
)


class CowinException(Exception):
    pass


async def fetch(date: str, pincode: int, session: aiohttp.ClientSession):
    """
    call cowin api

    :param date str:
    :param pincode int:
    :param session aiohttp.ClientSession:
    """
    url = f"{COWIN_API}/?pincode={pincode}&date={date}"
    try:
        response = await session.request(
            method="GET",
            url=url,
            headers=HEADERS,
        )

        resp_json = await response.json()

        if response.status == 403:  # forbidden
            print("403 : Too Many Requests")
            raise CowinException

        if "sessions" in resp_json:
            return resp_json
    except aiohttp.ClientConnectorError as e:
        print("Connection Error", str(e))


async def get_slot(date: str, pincode: int, session: aiohttp.ClientSession, centers):
    """
    get centers for given date and pincode

    :param date str:
    :param pincode int:
    :param session aiohttp.ClientSession:
    :param centers [TODO:type]: result will be stored in this dict
    """
    try:
        response = await fetch(date, pincode, session)
        if response["sessions"]:
            for center in response["sessions"]:
                center["date"] = datetime.datetime.strptime(center["date"], "%d-%m-%Y")
                center_dict = {
                    k: center[k]
                    for k in [
                        "available_capacity",
                        "min_age_limit",
                        "date",
                    ]
                }
                if center["name"] in centers:
                    centers[center["name"]].append(center_dict)
                else:
                    centers[center["name"]] = [center_dict]
                pass
    except Exception as err:
        print(f"Exception occured: {err}")
        pass


async def get_all_slots(pincode: int):
    """
    get slots for day+NUMDAY of given pincode

    :param pincode int
    [TODO: Error Handling]
    """
    centers: Dict[str, Any] = {}  # data will be stored in this dict
    dates = [
        (datetime.datetime.today() + datetime.timedelta(days=x)).strftime("%d-%m-%Y")
        for x in range(NUMDAY)
    ]
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(
            *[get_slot(date, pincode, session, centers) for date in dates]
        )
        for center in centers:
            centers[center].sort(key=lambda x: x["date"])
        # print(centers)
        return centers


# loop = asyncio.get_event_loop()
# loop.run_until_complete(get_all_slots(110053))
