# Heardle-telegram
Like [Heardle](https://www.heardle.app), but with a customised list of songs and [for now] in the form of a telegram bot instead of a web UI.

## Setup
```bash
conda create -n heardle-telegram python=3.9
pip install -r requirements.txt
```
Then set up ytmusicapi headers according to https://ytmusicapi.readthedocs.io/en/latest/setup.html.

<details>
<summary>Firefox </summary>

* Verify that the request looks like this: **Status** 200, **Method** POST, **Domain** music.youtube.com, **File** `browse?...`
* Copy the request headers (right click > copy > copy request headers)
</details>

<details>
<summary>Chromium (Chrome/Edge/Brave)</summary>

* Verify that the request looks like this: **Status** 200, **Type** xhr, **Name** `browse?...`
* Click on the Name of any matching request. In the “Headers” tab, scroll to the section “Request headers” and copy everything starting from “accept: */*” to the end of the section
</details>

## Run
Run a game with

```bash
python heardle-telegram.py
```