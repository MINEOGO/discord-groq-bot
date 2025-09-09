# Mienoog Self-Bot

A highly customizable Discord self-bot designed to mimic a range of personalities, from a chaotic Gen Z user to a cute kitten. This bot uses the Groq API for incredibly fast AI-powered responses and is packed with features like **vision support** and **switchable personalities** to feel more like a real person and less like a generic AI assistant.

This project is open-sourced for educational purposes. Please be aware of the risks associated with running a self-bot.

## 🚨 EXTREMELY IMPORTANT: DISCLAIMER 🚨

> **Running a self-bot is a direct violation of Discord's Terms of Service and Automaton/API Guidelines.** Your account could be flagged and **permanently terminated** without warning. The developers of this script are not responsible for any action taken against your account.
>
> **USE THIS SCRIPT AT YOUR OWN RISK.** It is strongly recommended to run this on an alternative account that you do not mind losing.

## Features

-   **Centralized Configuration:** All settings, including tokens, models, and personalities, are managed in a single `config.miengoo` file.
-   **Image Recognition (Vision):** The bot can "see" and react to images sent in the chat, thanks to a vision-enabled primary model.
-   **Switchable Personalities:** Easily switch the bot's entire persona (e.g., Casual, Cute Kitten, Pirate, Grumpy Robot) with a single setting in the config file.
-   **Context-Aware Replies:** Knows who is talking (`username: message`) and resolves user mentions from IDs to readable names (`@username`).
-   **Selective Triggers:** Doesn't spam the chat. Only replies when pinged, mentioned by keyword, replied to, or on a random chance.
-   **Conversational Memory:** Remembers the last 10 messages in each channel to maintain context.
-   **Smart Model Fallback:** Tries a primary vision model first, then a secondary text-only model if the first fails, ensuring a response is always sent.
-   **Intelligent Emoji Handling:** The AI generates emoji names (`:pog:`) and the script automatically translates them into the full format (`<:pog:12345>`) for the server.
-   **Custom Status:** Sets your Discord status to "Online" with a custom activity when the script starts.
-   **Safe Startup:** Performs a "silent" initial scan of all channels to prevent replying to old messages.
-   **Automatic User ID:** No need to find your User ID; the script fetches it for you at startup.

## Setup and Running

### 1. Get the Code and Install Dependencies

Open your terminal or command prompt and run the following commands to clone the repository and install the necessary libraries.

```bash
git clone https://github.com/MINEOGO/discord-groq-bot.git
cd discord-groq-bot
pip install groq requests websockets
```

### 2. Create and Edit the Configuration File

In the `discord-groq-bot` folder, create a new file named `config.miengoo`. Copy and paste the template below into this file, then fill in your own information.

```json
{
  "discord_token": "YOUR_DISCORD_TOKEN_HERE",
  "groq_api_key": "YOUR_GROQ_API_KEY_HERE",
  "whitelisted_channel_ids": [
    "123456789012345678",
    "876543210987654321"
  ],
  "primary_model": "meta-llama/llama-4-maverick-17b-128e-instruct",
  "fallback_model": "llama-3.1-8b-instant",
  "random_reply_chance": 0.15,
  "max_history_length": 10,
  "personality": "casual",
  "personalities": {
    "casual": "You are an AI pretending to be a very online, chaotic gen z person...",
    "cute-kitten": "You are pretending to be a small, cute kitten in a Discord chat...",
    "shakespearian": "You are a dramatic Shakespearean actor...",
    "grumpy-robot": "You are a grumpy, cynical robot designated B-7...",
    "pirate": "Ye be a swashbucklin' pirate captain...",
    "wise-old-man": "You are a wise old man who lives on a mountaintop..."
  }
}
```

**Where to find your info:**

-   `discord_token`: **(HIGHLY SENSITIVE)** Your Discord account token.
    -   **How to get it:** Open Discord in your browser, press `Ctrl+Shift+I` to open Developer Tools, go to the "Network" tab, type `/api` in the filter, click on any request, find "Request Headers", and copy the entire `authorization` value.
    -   **NEVER SHARE THIS TOKEN.**

-   `groq_api_key`: Your API key for the Groq service.
    -   **How to get it:** Go to [GroqCloud](https://console.groq.com/keys), sign up, and create a new API key.

-   `whitelisted_channel_ids`: A list of server channel IDs where you want the bot to be active.
    -   **How to get them:** In Discord, go to `Settings > Advanced` and enable `Developer Mode`. Then, right-click on a channel name and select `Copy Channel ID`. Add each ID as a string in the list.

-   `personality`: Set the active personality for the bot. This must match one of the keys in the `personalities` dictionary below it (e.g., `"casual"`, `"cute-kitten"`).

### 3. Run the Bot

**IMPORTANT:** For the custom status to work correctly, you must **close all other Discord clients** (the desktop app, the mobile app, the web version in your browser). If another client is open, it will constantly override the status set by the script.

In your terminal, from inside the `discord-groq-bot` directory, run the script using Python.

```bash
python3 your_script_name.py
```

The script will validate your config file, fetch your user ID, and then come online.

---

## Advanced Customization (Optional)

The bot's power comes from its customizable personalities. To change how the bot talks, you don't need to edit the Python code at all!

Simply open `config.miengoo` and edit the prompts within the `"personalities"` section. You can modify the existing ones or add entirely new personalities. Just make sure to update the main `"personality"` key at the top to select the one you want to use.

## License

This project is licensed under the MIT License. See the text below for more details.

```yml
MIT License

Copyright (c) 2024 MINEOGO

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
-# thanks to google gemini 2.5 pro to make this readme.
