# Mienoog Self-Bot

A highly customizable Discord self-bot designed to mimic a chaotic, low-effort, and witty Gen Z personality. This bot uses the Groq API for incredibly fast AI-powered responses and is packed with features to feel more like a real person and less like a generic AI assistant.

This project is open-sourced for educational purposes. Please be aware of the risks associated with running a self-bot.

## 🚨 EXTREMELY IMPORTANT: DISCLAIMER 🚨

> **Running a self-bot is a direct violation of Discord's Terms of Service and Automaton/API Guidelines.** Your account could be flagged and **permanently terminated** without warning. The developers of this script are not responsible for any action taken against your account.
>
> **USE THIS SCRIPT AT YOUR OWN RISK.** It is strongly recommended to run this on an alternative account that you do not mind losing.

## Features

-   **Interactive Setup:** No need to edit files! The bot asks for your configuration on the first run.
-   **Advanced AI Personality:** Core personality is defined in a single, easy-to-edit system prompt for advanced customization.
-   **Context-Aware Replies:** Knows who is talking (`username: message`) and resolves user mentions from IDs to readable names (`@username`).
-   **Selective Triggers:** Doesn't spam the chat. Only replies when pinged, mentioned by keyword, replied to, or on a random chance.
-   **Conversational Memory:** Remembers the last 10 messages in each channel to maintain context.
-   **Smart Model Fallback:** Tries a primary model first, then a secondary one if the first fails, ensuring a response is always sent.
-   **Intelligent Emoji Handling:** The AI generates emoji names (`:pog:`) and the script automatically translates them into the full format (`<:pog:12345>`) for the server.
-   **Custom Status:** Sets your Discord status to "Online" with a custom activity when the script starts.
-   **Safe Startup:** Performs a "silent" initial scan of all channels to prevent replying to old messages.

## Setup and Running

### 1. Information to Prepare

When you run the script, it will ask you for the following information. It's best to have these ready beforehand.

-   `DISCORD_TOKEN`: **(HIGHLY SENSITIVE)** Your Discord account token.
    -   **How to get it:** Open Discord in your browser, press `Ctrl+Shift+I` to open Developer Tools, go to the "Network" tab, type `/api` in the filter, click on any request, find "Request Headers", and copy the entire `authorization` value.
    -   **NEVER SHARE THIS TOKEN.**

-   `GROQ_API_KEY`: Your API key for the Groq service.
    -   **How to get it:** Go to [GroqCloud](https://console.groq.com/keys), sign up, and create a new API key.

-   `MY_ID`: Your personal Discord User ID.
    -   **How to get it:** In Discord, go to `Settings > Advanced` and enable `Developer Mode`. Then, right-click your own profile picture anywhere and select `Copy User ID`.

-   `WHITELISTED_CHANNEL_IDS`: The list of server channel IDs where you want the bot to be active.
    -   **How to get them:** With Developer Mode enabled, right-click on a channel name and select `Copy Channel ID`.
    -   When the script asks for these, you can enter multiple IDs separated by commas (e.g., `12345,67890`).

### 2. Run the Bot

**IMPORTANT:** For the custom status to work correctly, you must **close all other Discord clients** (the desktop app, the mobile app, the web version in your browser). If another client is open, it will constantly override the status set by the script.

Open your terminal or command prompt and paste the following command. This will clone the repository, install the necessary libraries, and run the script all in one go.

```bash
git clone https://github.com/MINEOGO/discord-groq-bot.git && pip install groq requests && cd discord-groq-bot && python3 bocchi_therock_is_peak.py
```

The script will then guide you through the setup process, asking for each piece of information you prepared. Once you've entered everything, it will start its initial scan and come online.

---

## Advanced Customization (Optional)

For advanced users who want to change the bot's core behavior, the entire personality of the AI is controlled by the `system_prompt` variable inside the `groq_reply` function in `bocchi_therock_is_peak.py`. You can edit this file to make the bot more aggressive, more friendly, or give it a completely different persona.

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
