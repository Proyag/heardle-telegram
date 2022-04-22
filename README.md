# Heardle-telegram
Like [Heardle](https://www.heardle.app), but with a customised list of songs and [for now] in the form of a telegram bot instead of a web UI.

## Setup

### Install dependencies
```bash
conda create -n heardle-telegram python=3.10
sudo apt install ffmpeg
pip install -r requirements.txt
```

### Configure `ytmusicapi` headers
Then set up ytmusicapi headers according to https://ytmusicapi.readthedocs.io/en/latest/setup.html.
#### Step 1: Get header info
* Go to https://music.youtube.com and ensure you are logged in
* Find an authenticated POST request. The simplest way is to filter by /browse using the search bar of the developer tools. If you don’t see the request, try scrolling down a bit or clicking on the library button in the top bar.
<details><summary>Firefox </summary>

* Verify that the request looks like this: **Status** 200, **Method** POST, **Domain** music.youtube.com, **File** `browse?...`
* Copy the request headers (right click > copy > copy request headers)
</details>

<details>
<summary>Chromium (Chrome/Edge/Brave)</summary>

* Verify that the request looks like this: **Status** 200, **Type** xhr, **Name** `browse?...`
* Click on the Name of any matching request. In the “Headers” tab, scroll to the section “Request headers” and copy everything starting from “accept: */*” to the end of the section
</details>

#### Step 2: Create file with these credentials
```python
from ytmusicapi import YTMusic
YTMusic.setup(filepath="headers_auth.json")
```
Then paste what you got in the previous step, and press `Ctrl+D`.

### Configure Telegram Bot API
Next, create a JSON file called `telegram_config.json` like this:
```json
{
    "api_token": "Fill in your Bot API Token",
    "subscribers": []
}
```
with your telegram API token for this bot in `api_token` and a list of chat IDs for subscribers who will get new game notifications in `subscribers`.

## Run
Run a game with

```bash
python heardle-telegram.py
```

### Options:
`--no-notify`: Don't send notifications to subscribed telegram chats. (Useful while testing)
`--log-file LOG_FILE`: File to write logs (in addition to console)
`--cache CACHE`: File to use as library of songs
