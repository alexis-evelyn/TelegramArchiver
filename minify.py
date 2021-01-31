#!/usr/bin/python3

import os
import json
import compress_json

from typing import List, TextIO

input_dir: str = "json"
output_dir: str = "mini-json"
log_file: str = "failed-minification.txt"

files: List[str] = os.listdir(input_dir)

if not os.path.exists(output_dir):
    os.mkdir(output_dir)

for file in files:
    print(f"Minifying and Compressing {file}")

    try:
        json_file_path: str = os.path.join(input_dir, file)
        mini_file_path: str = os.path.join(output_dir, f"{file}.lzma")

        input_file: TextIO = open(file=json_file_path, mode="r")
        input_contents_list: List[str] = input_file.readlines()
        input_contents: str = "\n".join(input_contents_list)

        input_dict: dict = json.loads(input_contents)

        compress_json.dump(input_dict, mini_file_path)
    except Exception as e:  # JSONDecodeError
        print(f"Failed To Minify {file}!!! Reason: {e}!!! Logging To {log_file}")

        with open(file=log_file, mode="a+") as f:
            f.writelines(f"{file}; {e}\n")
            f.close()
