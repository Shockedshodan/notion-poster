# -*- coding: utf-8 -*-
import sys
import os

plugindir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(plugindir)
sys.path.append(os.path.join(plugindir, "lib"))
sys.path.append(os.path.join(plugindir, "plugin"))

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
                        method=self.notion_poster.create_new_journal_entry_for_user,
                        parameters=[query]
            )


if __name__ == "__main__":
   windows_notion_poster = WindowsPlugin()
   windows_notion_poster.run()