import configparser
from pathlib import Path

import requests

DEFAULT_CONFIG_PATH = Path.home() / "notion_poster.ini"

config = configparser.ConfigParser()
config.read(DEFAULT_CONFIG_PATH)
notion_api_key = config['GENERAL']['api_key']

headers = {
    "Authorization": f"Bearer {notion_api_key}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

response = requests.get('https://api.notion.com/v1/users', headers=headers)

users = response.json().get('results', [])

# print table header
print("| User ID | Username |")
print("| --- | --- |")

# print each row
for user in users:
    print(f"|{user['name']}|`{user['id']}`| ")
