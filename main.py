#!/usr/bin/python3

from telethon import TelegramClient, events, sync

import pandas as pd
import configparser

# Get API Login Auth
config = configparser.ConfigParser()
config.read('login.ini')

# API Login Auth
api_id = config['auth']['id']
api_hash = config['auth']['key']
channel_name: str = config['archive']['channel']

client = TelegramClient('python-archiver', api_id, api_hash)
client.start()

# The_DonaId, CoronaChanNews, CoronaChanNews2
messages = client.get_messages(channel_name, limit=int(config['archive']['limit']))
# messages[0].download_media()

print(f"{messages.total} Total Messages")

# TODO: Verify How To Not Crash On Too Small Number Of Messages
channel: pd.DataFrame = pd.DataFrame()
for x in range(0, messages.total):
    try:
        message_dict: dict = messages[x].to_dict()
        channel = channel.append(message_dict, ignore_index=True)
    except:
        print(f"Failed {x}/{messages.total}!!!")

# print(channel)
print(channel.message)
# print(f"{messages.total} Total Messages")

channel.to_csv(f"{channel_name}.csv")
