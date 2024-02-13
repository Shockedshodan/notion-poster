# -*- coding: utf-8 -*-
import sys
import os

plugindir = os.path.abspath(os.path.dirname(__file__))
plugin_parent_dir = os.path.dirname(plugindir)
sys.path.append(plugin_parent_dir)
sys.path.append(os.path.join(plugin_parent_dir, "lib"))
sys.path.append(os.path.join(plugin_parent_dir, "notionposter_windows"))
sys.path.append(os.path.join(plugin_parent_dir, "notion-journal"))

from notion_journal.notion_poster import NotionJournalPoster
import requests
from requests.exceptions import HTTPError
from flox import Flox, ICON_APP_ERROR



class WindowsPlugin(Flox):
   def __init__(self):
      super().__init__()
      self.notion_poster = NotionJournalPoster(None, self)

   def _query(self, query: str):
         try:
               self.query(query)
         except HTTPError as e:
               self.logger.exception(e)
               self.add_item(
                  title="Error",
                  subtitle="An error occurred while querying Notion",
                  method=self.open_settings_dialog
               )

   def query(self, query: str):
      if len(query.strip()) == 0:
            self.add_item(title="Empty query is not allowed",
                        subtitle="No query provided",
                        icon=ICON_APP_ERROR
                     )
      else:
            self.add_item(title="Create new journal entry",
                        subtitle=query,
                        method=self.create_journay_entry,
                        parameters=[query]
            )

   def create_journay_entry(self, query: str):
      self.notion_poster.create_new_journal_entry_for_user(query)

if __name__ == "__main__":
   windows_notion_poster = WindowsPlugin()
   windows_notion_poster.run()