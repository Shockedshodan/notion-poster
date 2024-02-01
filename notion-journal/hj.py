import json
import sys
from pprint import pprint
from datetime import datetime, timezone

import requests

import configparser

"""
This script sends its command line arguments to the Notion API to create a new journal entry
in the user's journal.
For it to work you need to provide the config file with three variables:
db_id   -  the ID of the journals database" page
person_id - the ID of the user (UUID)
notion_api_key - the API key for the integration
"""


class NotionJournalPoster:

    def __init__(self, config_path=None):
        config = configparser.ConfigParser()
        config.read(config_path or "~/.notion_journal_poster.ini")

        self.db_id = config['JOURNAL_CREDS']['db_id']
        self.person_id = config['JOURNAL_CREDS']['person_id']
        self.notion_api_key = config['JOURNAL_CREDS']['notion_api_key']

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
                                    "content": text
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

    def get_page_children(self, page_id: str):
        url = f"https://api.notion.com/v1/blocks/{page_id}/children"
        response = requests.get(url, headers=self.headers)
        pprint(response.json())

    def post_journal_update(self, text):
        todays_page_id = (self.get_todays_page_id_for_user() or self.create_new_todays_page_for_user())
        self.add_child_text_block_to_block(todays_page_id, input_text, with_timestamp=True)


if __name__ == "__main__":
    input_text = ' '.join(sys.argv[1:])
    njp = NotionJournalPoster()
    njp.post_journal_update(input_text)
