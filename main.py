# -*- coding: utf-8 -*-
import sys
import os

plugindir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(plugindir)
sys.path.append(os.path.join(plugindir, "lib"))
sys.path.append(os.path.join(plugindir, "plugin"))

from plugin.notion_poster import NotionJournalPoster

if __name__ == "__main__":
    NotionJournalPoster()