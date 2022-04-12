# Heardle-telegram
Like [Heardle](https://www.heardle.app), but with a customised list of songs and [for now] in the form of a telegram bot instead of a web UI.

## Setup
```bash
conda create -n heardle-telegram python=3.10
sudo apt install ffmpeg
pip install -r requirements.txt
```
Then set up ytmusicapi headers according to https://ytmusicapi.readthedocs.io/en/latest/setup.html.
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

## Run
Run a game with

```bash
python heardle-telegram.py
```