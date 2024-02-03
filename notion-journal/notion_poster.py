#!/usr/bin/python3
import json
import sys
from pathlib import Path
from pprint import pprint
from datetime import datetime, timezone

import requests

import configparser

"""
This script sends its command line arguments to the Notion API to create a new journal entry
in the user's journal.
For it to work you need to provide the config file notion_poster.ini:

[GENERAL]
api_key=<the API key for the integration>
person_id=<the ID of the user (UUID)>
[JOURNAL]
db_id=<the ID of the journals database page>

"""

DEFAULT_CONFIG_PATH = Path.home() / "notion_poster.ini"


def notify(message):
    from notifier import Notifier
    notifier = Notifier()
    notifier.title = "Notion Journal Poster"
    notifier.message = message

    notifier.send()


class NotionJournalPoster:

    def __init__(self, config_path=None):
        config_path = config_path or DEFAULT_CONFIG_PATH

        if not Path(config_path).exists():
            print(f"Config file not found at {config_path}")
            sys.exit(1)
        config = configparser.ConfigParser()
        config.read(config_path)

        self.notion_api_key = config['GENERAL']['api_key']
        self.person_id = config['GENERAL']['person_id']
        self.db_id = config['JOURNAL']['db_id']

        # Get the current date and time in UTC
        now_utc = datetime.now(timezone.utc)
        self.now_local = now_utc.astimezone()
        self.today_date_iso = now_utc.date().isoformat()

        # Define the headers for the API request
        self.headers = {
            "Authorization": f"Bearer {self.notion_api_key}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }

    def get_todays_page_id_for_user(self) -> [str | None]:
        url = f"https://api.notion.com/v1/databases/{self.db_id}/query"
        filter = {
            "and": [
                {
                    "property": "Date",
                    "date": {
                        "equals": self.today_date_iso
                    }
                },
                {
                    "property": "Person",
                    "people": {
                        "contains": self.person_id,
                    }
                }
            ]
        }
        data = {
            "filter": filter
        }
        response = requests.post(url, headers=self.headers, data=json.dumps(data))
        pprint(response.json())
        resp_dict = response.json()
        if resp_dict['results']:
            return resp_dict['results'][0]['id']
        return None

    def create_new_todays_page_for_user(self):
        url = f"https://api.notion.com/v1/pages"
        # Define the data for the new children
        data = {
            "parent": {"database_id": self.db_id},
            "properties": {
                "Person": {
                    "people": [
                        {
                            "id": self.person_id
                        }
                    ]
                },
                "Date": {
                    "date": {
                        "start": self.today_date_iso
                    }
                }
            }
        }
        response = requests.post(url, headers=self.headers, data=json.dumps(data))
        pprint(response.json())
        return response.json()['id']

    def add_child_text_block_to_block(self, block_id: str, text: str, with_timestamp=False):
        url = f"https://api.notion.com/v1/blocks/{block_id}/children"
        # Define the data for the new children
        data = {
            "children": [
                {
                    "object": "block",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": " " + text if with_timestamp else text
                                }
                            }
                        ]
                    }
                },
            ]
        }
        if with_timestamp:
            data['children'][0]['paragraph']['rich_text'].insert(
                0,
                {'mention': {'date': {'end': None,
                                      'start': self.now_local.isoformat(),
                                      'time_zone': None},
                             'type': 'date'},
                 'plain_text': self.now_local.isoformat(),
                 'type': 'mention'}
            )

        response = requests.patch(url, headers=self.headers, data=json.dumps(data))
        pprint(response.json())
        return response.json()

    def get_page_children(self, page_id: str):
        url = f"https://api.notion.com/v1/blocks/{page_id}/children"
        response = requests.get(url, headers=self.headers)
        pprint(response.json())

    def post_journal_update(self, input_text):
        todays_page_id = (self.get_todays_page_id_for_user() or self.create_new_todays_page_for_user())
        return self.add_child_text_block_to_block(todays_page_id, input_text, with_timestamp=True)


if __name__ == "__main__":
    input_text = ' '.join(sys.argv[1:])
    njp = NotionJournalPoster()
    result = njp.post_journal_update(input_text)
    created_time = result['results'][0]['created_time']
    notify("Created new journal entry in Notion: " + created_time)
