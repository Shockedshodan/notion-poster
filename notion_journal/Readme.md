# Notion journalling utility

This is a utility for posting messages to a journal in Notion.

## Ways to run

To keep your focus on the task at hand and avoid switching to console,
we recommend setting up a launcher for your platform, e.g. "Alfred" for MacOS, 
"Albert" on Ubuntu, and assign it to a hotkey combination.

Here are some ways to run it.

### Console command

You may put it into a local directory that is in your `PATH`, e.g. 
```bash
ln -s ~/hiro-org-tools/notion-journal/notion_poster.py ~/.local/bin/`
```
and run directly as


```bash
pip3 install -r requirements.txt
notion_poster.py My first journal entry! Yay!
```

### Albert launcher
`notion_poster` directory contains a Python plugin for [Albert launcher](https://github.com/albertlauncher/albert)

To install the plugin, copy/link the plugin folder to Alber `plugins` folder, typically 
```bash
ln -s notioposter ~/.local/share/albert/python/
```
then enable the plugin in Albert settings and assign a handler trigger to it.

The plugin will just try to run `notion_poster.py` from the command line.


## Configuration

The utility expects to find its config to in the `notion_poster.ini` in
the user's home directory.
```ini
[GENERAL]
api_key=<the API key for the integration>
person_id=<the ID of the user (UUID)>
[JOURNAL]
db_id=<the ID of the journals database page>
```

## How it works
The utility expects the Notion journal to be a flat database of messages,
each message as a separate row. Messages are put into the `Entry` column 
(special `title` field in Notion)

When run, the utility:
* connects to Notion with the provided `api_key` 
* posts the given text as a new entry into database `db_id` marked as `person_id`
* tries to send a desktop notification to the user

## Important notes

* Currently, Notion API does not support user-specific API tokens. 
  The API token is created for a "connection", so the authorship of the entry is by "integration".
* After you added a "connection" and got its API token, you still need to adjust the
  database object permissions to permit the integration to access it.
* For the "connection" to work, you also need to permit it to "read user information".
* Currently, Notion does not allow querying user information by human-readable names.
  Also, it is impossible to look up one's UUID through Notion interface. 
  So, one has to obtain their UUID for `person_id` by other means (e.g. through the API or by [browser dev tools](https://dev.to/victoriaslocum/how-to-find-non-admin-notion-user-ids-5277))
