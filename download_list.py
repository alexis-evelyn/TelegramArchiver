import requests

channel_list: str = "https://archive.org/download/telegram_20210125/telegram.txt"
file_path: str = "working/telegram.txt"

print(f"Downloading {channel_list}!!!")
r = requests.get(channel_list)

if r.status_code == requests.codes.OK:
    print(f"Saving as {file_path}!!!")
    try:
        with open(file_path, mode="w") as f:
            f.writelines(r.text)
            f.close()
            print(f"Saved File {file_path}!!!")
    except IOError as e:
        print(f"Failed To Save {file_path} Due To {e.message}")
else:
    print(f"Failed To Get Valid Response From Channel List: {r.status_code}")
