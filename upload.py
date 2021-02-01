#!/usr/bin/python3

import configparser
import os
import dropbox

from typing import List, BinaryIO
from dropbox.exceptions import ApiError
from dropbox.files import ListFolderResult

log_file: str = "failed-upload.txt"
output_dir: str = "Telegram"
input_dir: str = "mini-json"
files: List[str] = os.listdir(input_dir)

config = configparser.ConfigParser()
config.read('login.ini')


def add_files_to_list(entries, files_list: List[str]):
    for entry in entries:
        file: str = str(entry.path_lower).rsplit(f"{output_dir.lower()}/")[1]
        files_list.append(file)


access_token: str = config['dropbox']['access_token']
dbx = dropbox.Dropbox(access_token)

print("Dropbox User: {user}".format(user=dbx.users_get_current_account().name.display_name))

# for entry in dbx.files_list_folder(path='').entries:
#     print(entry.name)

try:
    dbx.files_list_folder(f"/{output_dir}")
except ApiError:
    print(f"Creating Folder {output_dir}")
    dbx.files_create_folder_v2(f"/{output_dir}")

existing_files: List[str] = []
existing_files_result: ListFolderResult = dbx.files_list_folder(f"/{output_dir}")

add_files_to_list(entries=existing_files_result.entries, files_list=existing_files)

has_more_files: bool = existing_files_result.has_more
more_files: ListFolderResult
while has_more_files:
    more_files = dbx.files_list_folder_continue(cursor=existing_files_result.cursor)
    add_files_to_list(entries=more_files.entries, files_list=existing_files)
    has_more_files: bool = more_files.has_more

for file in files:
    input_file_path: str = os.path.join(input_dir, file)
    input_file: BinaryIO = open(file=input_file_path, mode="rb")

    if file.lower() in existing_files:
        print(f"Skipping {file}")
        continue

    print(f"Uploading {file} to Dropbox")
    try:
        dbx.files_upload(input_file.read(), f'/{output_dir}/{file}')
    except ApiError as e:
        print(f"Failed to Upload {file}!!! Reason: {e}!!! Logging To {log_file}")

        with open(file=log_file, mode="a+") as f:
            f.writelines(f"{file}; {e}\n")
            f.close()
