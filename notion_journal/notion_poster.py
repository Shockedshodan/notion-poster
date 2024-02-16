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
    from pynotifier import Notification

    Notification(
        title='Notification Title',
        description=message,
        duration=1,  # Duration in seconds
        urgency='low'
    ).send()


class NotionJournalPoster:

    def __init__(self, config_path=None, flow_self = None):
        
        if flow_self is not None:
            self.notion_api_key = flow_self.settings.get("api_key")
            self.person_id = flow_self.settings.get("person_id")
            self.db_id = flow_self.settings.get("db_id")
        else:
            config = self.get_and_read_config(config_path)
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


    def get_and_read_config(config_path=None) -> configparser:
        config_path = config_path or DEFAULT_CONFIG_PATH
        if not Path(config_path).exists():
            print(f"Config file not found at {config_path}")
            sys.exit(1)
        config = configparser.ConfigParser()
        config.read(config_path)
        return config
    
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

    def create_new_journal_entry_for_user(self, text: str):
        url = f"https://api.notion.com/v1/pages"
        # Define the data for the new children
        data = {
            "parent": {"database_id": self.db_id},
            "properties": {
                "Entry": {
                    "title": [
                        {
                            "type": "text",
                            "text": {
                                "content": text
                            }
                        }
                    ]
                },
                "Person": {
                    "people": [
                        {
                            "id": self.person_id
                        }
                    ]
                },
                "Date": {
                    "date": {
                        "start": self.now_local.isoformat(),
                    }
                }
            }
        }
        try:
            response = requests.post(url, headers=self.headers, data=json.dumps(data))
            if self.flow_self is not None:
                # Temporary workaround for flow launcher
                return None
            if response.headers.get('Content-Type') == 'application/json' and response.status_code == 200:
                response_json = json.loads(response.text) 
                return response_json
            else:
                print("Non-JSON Response or Error Status Code")
                return response.text  # Return raw text for inspection
        except json.JSONDecodeError as e:
            print("JSON parsing error:", e)
        except requests.RequestException as e:
            print("Request error:", e)

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


if __name__ == "__main__":
    input_text = ' '.join(sys.argv[1:])
    njp = NotionJournalPoster()
    result = njp.create_new_journal_entry_for_user(input_text)
    created_time = result['created_time']
    notify("Notion journal [" + created_time + "]: " + input_text)
