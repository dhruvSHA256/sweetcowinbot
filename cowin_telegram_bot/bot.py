#!/usr/bin/env python

import threading
from typing import Tuple
from utils import render_template
from cowin import get_all_slots, CowinException
from user import User
import logging
import os
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.parts import safe_split_text
import time

# import time
from threading import Thread


# import API_TOKEN from secrets.py if run locally else from env var
if os.environ["LOCAL"]:
    from utils.secrets import API_TOKEN
else:
    API_TOKEN = os.environ["API_TOKEN"]

NOTIFY_DELTA = 3  # time interval to notify user in sec

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
PINCODES: set[int]  # store pincodes to notify in memory


@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    """
    function to handle /start

    :param message types.Message:
    """
    await message.answer("http://0x0.st/-BGP.png")
    await message.answer(
        "HI this a  😷 BOT 😷 to notify you about available vaccine sessions, send /help \
        for usage"
    )


@dp.message_handler(commands=["help"])
async def show_help(message: types.Message):
    """
    function to handle /help

    :param message types.Message:
    """
    await message.reply(
        "Usage: send PINCODE and MIN-AGE-LIMIT in format `PINCODE MIN-AGE-LIMIT` to get \
        notification about availibility status in next 10 days",
        parse_mode=types.ParseMode.MARKDOWN,
    )
    await message.answer(
        "For example: `110032 18`", parse_mode=types.ParseMode.MARKDOWN
    )


@dp.message_handler(regexp="^[1-9]{1}[0-9]{5}\\s(45|18)$")
async def reply_pin_current(message: types.Message):
    """
    function to handle `PINCODE AGE`

    :param message types.Message:
    """
    global PINCODES
    pincode, min_age_limit = message.text.split(" ")
    pincode = int(pincode)
    min_age_limit = int(min_age_limit)
    PINCODES.add(pincode)
    print(message.chat.as_json())
    try:
        await message.answer(f"Got Pincode :  {pincode} and age : {min_age_limit}")
        centers = await get_all_slots(pincode)
        answer_list = safe_split_text(
            render_template(centers, pincode, min_age_limit=min_age_limit)
        )
        for answer in answer_list:
            await message.answer(answer, parse_mode=types.ParseMode.MARKDOWN)
    except CowinException:
        await message.answer("Internal Server Error, please try after few mins")


# run notification daemon in a seperate thread,
# [TODO : implement this]
def notify_user():
    global PINCODES
    # Timer(interval=NOTIFY_DELTA, function=notify_user).start()
    while True:
        time.sleep(NOTIFY_DELTA)
        print(PINCODES)


# run tg bot daemon in  a seperate thread,
def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    executor.start_polling(dp, skip_updates=True, loop=loop)


if __name__ == "__main__":
    # populate pincode here
    # pincode where user > 1 and user.notification is true
    PINCODES = {110032}

    bot_thread = Thread(target=run_bot)
    bot_thread.setDaemon(True)

    notification_daemon = Thread(target=notify_user)
    notification_daemon.setDaemon(True)

    bot_thread.start()
    notification_daemon.start()

    bot_thread.join()
    notification_daemon.join()
