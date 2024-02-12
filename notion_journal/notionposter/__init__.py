# -*- coding: utf-8 -*-
# Copyright (c) 2024 Vadim Bulavintsev

from __future__ import annotations

import subprocess

import albert

md_iid = '2.0'
md_version = "0.1"
md_name = "Notion Poster"
md_description = "Post to Notion"
md_license = "MIT"
md_url = "https://github.com/albertlauncher/python/tree/master/command"
md_authors = ["@ichorid"]


class Plugin(albert.PluginInstance, albert.TriggerQueryHandler):
    def __init__(self):
        albert.TriggerQueryHandler.__init__(self,
                                            id=md_id,
                                            name=md_name,
                                            description=md_description,
                                            synopsis='Message to post to Notion',
                                            defaultTrigger='np ')
        albert.PluginInstance.__init__(self, extensions=[self])

    def handleTriggerQuery(self, query):
        stripped = query.string.strip()

        if stripped:
            query.add(albert.StandardItem(
                id=md_id,
                text=stripped,
                subtext="Journal: " + stripped,
                inputActionText=query.trigger + stripped,
                actions=[
                    albert.Action("post", "Post",
                                  lambda r=stripped: albert.runDetachedProcess(["notion_poster", stripped]))
                ]
            ))
