#!/usr/bin/python3

import json
import asyncio
import configparser
import urllib.parse

from typing import Union, TextIO, List

from telethon import TelegramClient, errors
from telethon.client.messages import _IDsIter, _MessagesIter
from telethon.tl.types import Chat, Message

config = configparser.ConfigParser()
config.read('login.ini')

# API Login Auth
api_id: int = int(config['auth']['id'])
api_hash: str = config['auth']['key']
# channel_name: str = config['archive']['channel']

client = TelegramClient('python-archiver', api_id, api_hash)
client.start()


async def download_channel(channel: str) -> dict:
    try:
        async with client.takeout(contacts=True, users=True, chats=True, megagroups=True, channels=True, files=False) as takeout:
            chat: Chat = await client.get_entity(channel)
            messages: Union[_MessagesIter, _IDsIter] = takeout.iter_messages(chat, wait_time=0)

            print(f"Downloading Channel: {channel}")
            # print(f"{messages.total} Total Messages")

            messages_dict: dict[Message] = {}
            async for message in messages:
                # print(message.id, message.text)
                messages_dict[message.id] = message.to_dict()

            return messages_dict
    except errors.TakeoutInitDelayError as e:
        print('Must wait ', e.seconds, ' before takeout')


async def save_channel(channel: str):
    print(f"Validating Channel: {channel}")
    results: dict = await download_channel(channel)

    print(f"Saving Channel: {channel}")
    save: TextIO = open(file=f"working/messages/{channel}.json", mode="w")
    save.writelines(json.dumps(obj=results, indent=4, sort_keys=True, default=str))
    save.close()


async def download_channels():
    channel_list_path: str = "working/telegram.txt"
    channel_list_file: TextIO = open(file=channel_list_path, mode="r")
    channel_list: List[str] = channel_list_file.readlines()

    for line in channel_list:
        clean: str = line.lstrip("https://t.me/").strip()
        clean: str = urllib.parse.unquote_plus(string=clean)

        if clean == "":
            continue

        try:
            await save_channel(channel=clean)
        except ValueError as e:
            message: str = e.args[0]
            ignore: bool = False

            if "Cannot find any entity corresponding to" in message:
                ignore: bool = True
            elif "No user has" in message and "as username" in message:
                ignore: bool = True

            if not ignore:
                print(e)
                break



print("Starting Download!!!")
loop = asyncio.get_event_loop()
loop.run_until_complete(download_channels())
# loop.run_until_complete(download_channel("magalife"))
print("Finished!!!")
