#!/usr/bin/python3
import json
import sys
from pathlib import Path
from pprint import pprint
from datetime import datetime, timezone
from flowlauncher import FlowLauncher

import requests

import configparser




def notify(message):
    from pynotifier import Notification

    Notification(
        title='Notification Title',
        description=message,
        duration=1,  # Duration in seconds
        urgency='low'
    ).send()


class NotionJournalPoster(FlowLauncher):

    def __init__(self):
        self.api_key = self.settings.get('api_key')
        self.person_id = self.settings.get('person_id')
        self.db_id = self.settings.get('db_id')
        
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


    def query(self, query: str):
        output = []
        if len(query.strip()) == 0:
            output.append({
                "Title": "No query provided",
                "IcoPath": "Images/notion.png",
            })
        else: 
            output.append({
                "Title": "Create new journal entry",
                "SubTitle": query,
                "IcoPath": "Images/notion.png",
                "JsonRPCAction": {
                    "method": "create_new_journal_entry_for_user",
                    "parameters": [query],
                    "dontHideAfterAction": False
                }
            })

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
        response = requests.post(
            url, headers=self.headers, data=json.dumps(data))
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
                        'start': self.now_local.isoformat(),
                    }
                }
            }
        }
        response = requests.post(
            url, headers=self.headers, data=json.dumps(data))
        pprint(response.json())
        return response.json()

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

        response = requests.patch(
            url, headers=self.headers, data=json.dumps(data))
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