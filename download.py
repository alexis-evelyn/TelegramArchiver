#!/usr/bin/python3

import configparser
import os
import dropbox

from typing import List, BinaryIO
from dropbox.exceptions import ApiError
from dropbox.files import ListFolderResult

log_file: str = "failed-download.txt"
output_dir: str = "mini-json-dropbox"
input_dir: str = "Telegram"

config = configparser.ConfigParser()
config.read('login.ini')


def add_files_to_list(entries, files_list: List[str]):
    for entry in entries:
        file: str = str(entry.path_lower).rsplit(f"{input_dir.lower()}/")[1]
        files_list.append(file)


if not os.path.exists(output_dir):
    os.mkdir(output_dir)

access_token: str = config['dropbox']['access_token']
dbx = dropbox.Dropbox(access_token)

print("Dropbox User: {user}".format(user=dbx.users_get_current_account().name.display_name))

existing_files: List[str] = []
existing_files_result: ListFolderResult = dbx.files_list_folder(f"/{input_dir}")

add_files_to_list(entries=existing_files_result.entries, files_list=existing_files)

has_more_files: bool = existing_files_result.has_more
more_files: ListFolderResult
while has_more_files:
    more_files = dbx.files_list_folder_continue(cursor=existing_files_result.cursor)
    add_files_to_list(entries=more_files.entries, files_list=existing_files)
    has_more_files: bool = more_files.has_more

for file in existing_files:
    output_file_path: str = os.path.join(output_dir, file)

    if os.path.exists(file):
        print(f"Skipping {file}")
        continue

    print(f"Downloading {file} From Dropbox")
    try:
        dbx.files_download_to_file(path=f'/{input_dir}/{file}', download_path=f'{output_dir}/{file}')
    except ApiError as e:
        print(f"Failed to Download {file}!!! Reason: {e}!!! Logging To {log_file}")

        with open(file=log_file, mode="a+") as f:
            f.writelines(f"{file}; {e}\n")
            f.close()
