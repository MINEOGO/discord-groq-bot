import time
import random
import requests
import json
import re
import sys
import threading
import asyncio
import websockets
from groq import Groq

def load_config():
    try:
        with open("config.miengoo", "r") as f:
            config = json.load(f)
            required_keys = [
                "discord_token", "groq_api_key", "whitelisted_channel_ids",
                "primary_model", "fallback_model", "random_reply_chance",
                "max_history_length", "personality", "personalities"
            ]
            for key in required_keys:
                if key not in config:
                    print(f"❌ Error: Missing key '{key}' in config.miengoo")
                    sys.exit(1)

            active_personality = config["personality"]
            if active_personality not in config["personalities"]:
                print(f"❌ Error: Personality '{active_personality}' not found in the 'personalities' section of config.miengoo.")
                sys.exit(1)

            return config
    except FileNotFoundError:
        print("❌ Error: config.miengoo not found. Please create the configuration file.")
        sys.exit(1)
    except json.JSONDecodeError:
        print("❌ Error: Could not decode config.miengoo. Please ensure it is valid JSON.")
        sys.exit(1)

def get_my_id(headers):
    try:
        res = requests.get("https://discord.com/api/v9/users/@me", headers=headers)
        if res.status_code == 200:
            user_id = res.json()["id"]
            print(f"✅ Successfully fetched user ID: {user_id}")
            return user_id
        else:
            print(f"❌ Error: Failed to fetch user ID. Status: {res.status_code}, Response: {res.text}")
            print("    Please check if your discord_token is valid in config.miengoo.")
            sys.exit(1)
    except Exception as e:
        print(f"❌ An error occurred while fetching user ID: {e}")
        sys.exit(1)

config = load_config()

DISCORD_TOKEN = config["discord_token"]
GROQ_API_KEY = config["groq_api_key"]
WHITELISTED_CHANNEL_IDS = set(config["whitelisted_channel_ids"])
PRIMARY_MODEL = config["primary_model"]
FALLBACK_MODEL = config["fallback_model"]
RANDOM_REPLY_CHANCE = float(config["random_reply_chance"])
MAX_HISTORY_LENGTH = int(config["max_history_length"])
ACTIVE_PERSONALITY = config["personality"]
ACTIVE_SYSTEM_PROMPT = config["personalities"][ACTIVE_PERSONALITY]

HEADERS = {
    "Authorization": DISCORD_TOKEN,
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/536.36",
    "Accept": "application/json"
}

MY_ID = get_my_id(HEADERS)

client = Groq(api_key=GROQ_API_KEY)

channel_to_guild_cache = {}
server_emoji_maps_cache = {}
chat_histories = {}

def gateway_worker():
    async def gateway_main():
        gateway_url = "wss://gateway.discord.gg/?v=10&encoding=json"
        while True:
            try:
                async with websockets.connect(gateway_url) as ws:
                    hello = json.loads(await ws.recv())
                    heartbeat_interval = hello['d']['heartbeat_interval'] / 1000

                    asyncio.create_task(heartbeat(ws, heartbeat_interval))

                    identify_payload = {
                        "op": 2,
                        "d": {
                            "token": DISCORD_TOKEN,
                            "properties": {
                                "os": "Windows",
                                "browser": "Chrome",
                                "device": ""
                            }
                        }
                    }
                    await ws.send(json.dumps(identify_payload))

                    async for message in ws:
                        event = json.loads(message)
                        if event['t'] == "READY":
                            print("    ✅ Gateway connection is READY. Setting custom presence.")
                            presence_payload = {
                                "op": 3,
                                "d": {
                                    "since": None,
                                    "activities": [
                                        {
                                            "name": "Custom Status",
                                            "type": 4,
                                            "state": "go sub to mineogo!!",
                                            "emoji": {
                                                "id": "1378218418884575313",
                                                "name": "mineogo"
                                            }
                                        }
                                    ],
                                    "status": "online",
                                    "afk": False
                                }
                            }
                            await ws.send(json.dumps(presence_payload))
                            break

                    async for message in ws:
                        pass

            except Exception as e:
                print(f"    ⚠️ Gateway connection error: {e}. Reconnecting in 10 seconds...")
                await asyncio.sleep(10)

    async def heartbeat(ws, interval):
        while True:
            await asyncio.sleep(interval)
            heartbeat_payload = {"op": 1, "d": None}
            try:
                await ws.send(json.dumps(heartbeat_payload))
            except websockets.exceptions.ConnectionClosed:
                break

    asyncio.run(gateway_main())

def get_emoji_map(guild_id):
    if not guild_id: return {}
    if guild_id in server_emoji_maps_cache: return server_emoji_maps_cache[guild_id]

    print(f"    - Fetching emoji map for server {guild_id}...")
    res = requests.get(f"https://discord.com/api/v10/guilds/{guild_id}/emojis", headers=HEADERS)
    if res.status_code == 200:
        emoji_map = {f":{e['name']}:": f"<:{e['name']}:{e['id']}>" for e in res.json() if not e.get('animated')}
        server_emoji_maps_cache[guild_id] = emoji_map
        return emoji_map
    return {}

def convert_emoji_placeholders(text, channel_id):
    guild_id = get_guild_id_from_channel(channel_id)
    if not guild_id: return text

    emoji_map = get_emoji_map(guild_id)
    if not emoji_map: return text

    def replacer(match):
        emoji_key = f":{match.group(1)}:"
        return emoji_map.get(emoji_key, match.group(0))

    return re.sub(r':(\w+):?', replacer, text)

def resolve_mentions(content, message_object):
    resolved_content = content
    for mention in message_object.get('mentions', []):
        resolved_content = resolved_content.replace(f'<@{mention["id"]}>', f'@{mention["username"]}')
    return resolved_content

def get_dms():
    res = requests.get("https://discord.com/api/v10/users/@me/channels", headers=HEADERS)
    if res.status_code == 200: return res.json()
    return []

def get_messages(channel_id, after=None, limit=20):
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages?limit={limit}"
    if after: url += f"&after={after}"
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200: return res.json()
    return []

def get_message(channel_id, message_id):
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages/{message_id}"
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200: return res.json()
    return None

def get_guild_id_from_channel(channel_id):
    if channel_id in channel_to_guild_cache: return channel_to_guild_cache[channel_id]
    res = requests.get(f"https://discord.com/api/v10/channels/{channel_id}", headers=HEADERS)
    if res.status_code == 200:
        guild_id = res.json().get("guild_id")
        channel_to_guild_cache[channel_id] = guild_id
        return guild_id
    return None

def send_typing(channel_id):
    requests.post(f"https://discord.com/api/v10/channels/{channel_id}/typing", headers=HEADERS)

def reply_message(channel_id, content, message_id):
    send_typing(channel_id)
    time.sleep(random.uniform(1.5, 3.5))
    payload = {"content": content, "message_reference": {"message_id": message_id}}
    requests.post(f"https://discord.com/api/v10/channels/{channel_id}/messages", headers=HEADERS, json=payload)

def groq_reply(message_content, channel_id, history, model_name, image_url=None):
    guild_id = get_guild_id_from_channel(channel_id)
    emoji_map = get_emoji_map(guild_id)
    available_emojis_for_prompt = " ".join(emoji_map.keys())

    system_prompt = ACTIVE_SYSTEM_PROMPT

    if available_emojis_for_prompt:
        system_prompt += f" The custom emojis available for you to use are: {available_emojis_for_prompt}."

    messages_payload = [{"role": "system", "content": system_prompt}]
    messages_payload.extend(history)

    user_content = [{"type": "text", "text": message_content}]
    if image_url:
        user_content.append({"type": "image_url", "image_url": {"url": image_url}})

    messages_payload.append({"role": "user", "content": user_content})

    try:
        completion = client.chat.completions.create(
            model=model_name, messages=messages_payload,
            temperature=1.3, max_completion_tokens=150, top_p=1, stream=False
        )
        if completion.choices and completion.choices[0].message:
            return completion.choices[0].message.content
    except Exception as e:
        print(f"    ❌ Error calling Groq API with model {model_name}: {e}")
    return ""

print("✅ Selfbot started...")
print(f"✅ Loaded personality: {ACTIVE_PERSONALITY}")

gateway_thread = threading.Thread(target=gateway_worker, daemon=True)
gateway_thread.start()
print("🔹 Gateway connection initiated to maintain custom presence...")

last_seen = {}
known_dm_channels = set()

print("✅ Performing initial scan of all channels to prevent replying to old messages...")
all_channels_on_startup = WHITELISTED_CHANNEL_IDS.copy()
for dm in get_dms():
    all_channels_on_startup.add(dm["id"])
    known_dm_channels.add(dm["id"])

for channel_id in all_channels_on_startup:
    print(f"    - Scanning channel {channel_id}...")
    latest_messages = get_messages(channel_id, limit=1)
    last_seen[channel_id] = latest_messages[0]['id'] if latest_messages else '0'

print("✅ Initial scan complete. Now listening for new messages.")

while True:
    try:
        for dm in get_dms():
            if dm["id"] not in known_dm_channels:
                print(f"🔹 New DM channel detected: {dm['id']}. Performing initial scan...")
                known_dm_channels.add(dm["id"])
                latest_messages = get_messages(dm['id'], limit=1)
                last_seen[dm['id']] = latest_messages[0]['id'] if latest_messages else '0'

        channels_to_check = known_dm_channels.union(WHITELISTED_CHANNEL_IDS)

        for channel_id in channels_to_check:
            after = last_seen.get(channel_id, '0')
            messages = get_messages(channel_id, after=after)
            if not messages: continue

            for msg in reversed(messages):
                if msg["author"]["id"] == MY_ID: continue

                content = msg.get("content", "").strip()
                if not content and not msg.get('attachments'): continue

                content_lower = content.lower()
                author_name = msg["author"].get("username", "Unknown")

                should_reply = False
                if any(mention['id'] == MY_ID for mention in msg.get('mentions', [])): should_reply = True
                elif "mienoog" in content_lower: should_reply = True
                elif msg.get('message_reference'):
                    ref = msg['message_reference']
                    if 'message_id' in ref:
                        original_msg = get_message(ref['channel_id'], ref['message_id'])
                        if original_msg and original_msg['author']['id'] == MY_ID: should_reply = True
                        else: continue
                elif random.random() < RANDOM_REPLY_CHANCE: should_reply = True

                if should_reply:
                    current_history = chat_histories.get(channel_id, [])

                    resolved_content = resolve_mentions(content, msg)
                    final_content_for_ai = f"{author_name}: {resolved_content}"

                    image_url = None
                    if msg.get('attachments'):
                        attachment = msg['attachments'][0]
                        if 'content_type' in attachment and attachment['content_type'].startswith('image/'):
                            image_url = attachment['url']
                            print(f"    🖼️ Image detected: {image_url}")

                    print(f"    ✉ New message from {author_name}: {content}")
                    print(f"    🤖 Content sent to AI: {final_content_for_ai}")

                    raw_reply_text = groq_reply(final_content_for_ai, channel_id, current_history, model_name=PRIMARY_MODEL, image_url=image_url)

                    if not raw_reply_text or not raw_reply_text.strip():
                        print("    ⚠️ Primary model failed. Falling back...")
                        raw_reply_text = groq_reply(final_content_for_ai, channel_id, current_history, model_name=FALLBACK_MODEL, image_url=None)

                    if not raw_reply_text or not raw_reply_text.strip():
                        print("    ⚠️ All models failed. Using hardcoded fallback.")
                        fallback_replies = ["nah", "wht", "huh?", "idk", "...", "bruh", "lol what", "anyways"]
                        raw_reply_text = random.choice(fallback_replies)

                    final_reply_text = convert_emoji_placeholders(raw_reply_text, channel_id)

                    print(f"    💬 Replying: {final_reply_text}")
                    reply_message(channel_id, final_reply_text, msg["id"])

                    current_history.append({"role": "user", "content": final_content_for_ai})
                    current_history.append({"role": "assistant", "content": final_reply_text})
                    if len(current_history) > MAX_HISTORY_LENGTH:
                        current_history = current_history[-MAX_HISTORY_LENGTH:]
                    chat_histories[channel_id] = current_history

            if messages:
                last_seen[channel_id] = messages[0]["id"]

        time.sleep(5)
    except Exception as e:
        print(f"⚠ Error in main loop: {e}")
        time.sleep(10)
