#!/usr/bin/python3

import os
import json
import compress_json

from typing import List, TextIO

input_dir: str = "mini-json"
output_dir: str = "decompressed-json"
log_file: str = "failed-decompression.txt"

files: List[str] = os.listdir(input_dir)

if not os.path.exists(output_dir):
    os.mkdir(output_dir)

for file in files:
    print(f"Decompressing {file}")

    try:
        mini_json_file_path: str = os.path.join(input_dir, file)
        decompressed_file_path: str = os.path.join(output_dir, f"{file[:-5]}")

        input_dict: dict = compress_json.load(mini_json_file_path)

        compress_json.dump(input_dict, decompressed_file_path)
    except Exception as e:  # JSONDecodeError
        print(f"Failed To Decompress {file}!!! Reason: {e}!!! Logging To {log_file}")

        with open(file=log_file, mode="a+") as f:
            f.writelines(f"{file}; {e}\n")
            f.close()
