#!/usr/bin/python3

import json
import asyncio
import configparser
import os
import re
import urllib.parse

from typing import Union, TextIO, List, Optional

from telethon import TelegramClient, errors
from telethon.client.messages import _IDsIter, _MessagesIter
from telethon.errors import ChannelPrivateError
from telethon.tl.types import Chat, Message

config = configparser.ConfigParser()
config.read('login.ini')

# API Login Auth
api_id: int = int(config['auth']['id'])
api_hash: str = config['auth']['key']
# channel_name: str = config['archive']['channel']

client = TelegramClient('python-archiver', api_id, api_hash)
client.start()


def file_exists(path: str, file: Optional[str] = None) -> bool:
    try:
        files: List[str] = os.listdir(path=path)
        files: List[str] = [x.lower() for x in files]

        if file is not None and file.lower() in files:
            return True
        elif file is None:
            return True
        return False
    except FileNotFoundError:
        return False


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
        clean: str = urllib.parse.unquote_plus(string=line)

        # Strip Off Domain Name
        clean: str = clean.lstrip("https://t.me/").strip()

        # If Join Chat Instead Of Typical Invite Link, Strip Down To Group Name
        if "joinchat/" in clean:
            clean: str = clean.lstrip("joinchat/").strip()

        # Why Is Robots.txt in Here? Remove It!
        if "robots.txt" in clean:
            clean: str = clean.rstrip("robots.txt").strip()

        # Why Is Favicon.ico in Here? Remove It!
        if "favicon.ico" in clean:
            clean: str = clean.rstrip("favicon.ico").strip()

        # Remove At Symbol
        if "@" in clean:
            clean: str = re.sub(r"[@]", r"", clean)

        # Remove Query Parameters
        if "?" in clean or "&" in clean:
            clean: str = re.sub(r"(.*)([?].*)", r"\1", clean)
            clean: str = re.sub(r"(.*)([&].*)", r"\1", clean)

        # Remove Non-ASCII Characters (As Telegram Doesn't Accept Them At All)
        if re.match(r"[^\x00-\x7F]+", clean):
            # print(f"Before: {clean}")
            clean: str = re.sub(r"[^\x00-\x7F]+", r"", clean)
            # print(f"After: {clean}")

        # Make Sure No Whitespace At Ends Of Channels
        clean: str = clean.strip()

        # Verify String Is Not Empty
        if clean == "":
            continue

        # Test Case Insensitive File Match (Case Insensitivity Does Not Work For Path Variable)
        # Note, I Have A Case Sensitive File System, And Group Names Are Not Case Sensitive AFAICT
        # I Also Want To Keep The Original Casing Of The Groups In The File Names
        # print(file_exists(path="working", file="joinchat.txt"))
        # print(file_exists(path="working", file="joinCHat.txt"))

        # Verify File Was Not Already Downloaded (e.g. different casing, stripped parameters, etc...)
        if file_exists(path="working/messages", file=f"{clean}.json"):
            print(f"File {clean}.json Already Exists!!! Skipping...")
            continue

        try:
            await save_channel(channel=clean)
        except ChannelPrivateError as e:
            # telethon.errors.rpcerrorlist.ChannelPrivateError
            print(f"{clean} Is A Private Channel!!! Logging!!!")
            with open(file="working/private-channels.txt", mode="a+") as private:
                private.writelines(f"{clean}\n")
                private.close()
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
