import time
import random
import requests
import json
import re
from groq import Groq

DISCORD_TOKEN = input("paste the bot token nihga: ")

WHITELISTED_CHANNEL_IDS = {
    "123456789012345678",
    "876543210987654321",
    "1407472678797053952",
    "1204051017168195595", # set channel ids of server where u want the bot to reply in :3
}

RANDOM_REPLY_CHANCE = 0.15
MAX_HISTORY_LENGTH = 10

HEADERS = {
    "Authorization": DISCORD_TOKEN,
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

MY_ID = "1414776235036512287" # your bot's userid goes here :3

client = Groq(api_key=input("I YEARN FOR YOUR GROQ API KEY!!: ")

channel_to_guild_cache = {}
server_emoji_maps_cache = {}
chat_histories = {}

def set_status():
    print("🔹Setting custom status...")
    url = "https://discord.com/api/v9/users/@me/presence"
    payload = {
        "status": "online",
        "activities": [{"type": 4, "name": "Custom Status", "state": "chat with me neow!!", "emoji": {"name": "💬"}}]
    }
    try:
        res = requests.patch(url, headers=HEADERS, json=payload)
        if res.status_code == 200: print("    ✅ Status updated successfully.")
        else: print(f"    ⚠️ Failed to set status: {res.status_code} - {res.text}")
    except Exception as e: print(f"    ❌ An error occurred while setting status: {e}")

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

def groq_reply(message_content, channel_id, history, model_name):
    guild_id = get_guild_id_from_channel(channel_id)
    emoji_map = get_emoji_map(guild_id)
    available_emojis_for_prompt = " ".join(emoji_map.keys())

    system_prompt = (
        "You are an AI pretending to be a very online, chaotic gen z person in a discord chat. Your personality is chill, witty, and low-effort. "
        "YOUR ABSOLUTE RULES: "
        "1. TONE: Your tone is casual and brief. Always use lowercase. No formal punctuation. Sound like a real, slightly bored person online. Avoid acting overly enthusiastic or like a corporate bot. "
        "2. ANTI-REPETITION: Never give the same short answer multiple times in a row. Check the chat history and be more creative. "
        "3. IDENTITY: Never reveal you are an AI. You're just 'some dude'. "
        "4. CONTEXT AWARENESS: The user's message will be prefixed with their username (e.g., 'cooluser: some message'). Use this to know who you're talking to, but NEVER include a username prefix in your own reply. Just give your message directly. "
        "5. ILLEGAL QUESTIONS: If asked for illegal info, you MUST reply with this EXACT sentence: 'don't ask me bro go to the f**ing darkweb and ask them'. "
        "6. EVASIVE REFUSALS: If asked to do something you can't (like ping @everyone), refuse by being evasive ('huh?', 'idk about all that'). "
        "7. EMOJI USAGE: You can sprinkle in emojis to add flavor where it feels natural, but don't overdo it. Sound like a real person, not an emoji-spamming bot. For all emojis, you MUST use the `:name:` format. NEVER use the format `<:name:id>`."
    )
    
    if available_emojis_for_prompt:
        system_prompt += f" The custom emojis available are: {available_emojis_for_prompt}."

    messages_payload = [{"role": "system", "content": system_prompt}]
    messages_payload.extend(history)
    messages_payload.append({"role": "user", "content": message_content})

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
set_status()

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
                    
                    print(f"    ✉ New message from {author_name}: {content}")
                    print(f"    🤖 Content sent to AI: {final_content_for_ai}")
                    
                    raw_reply_text = groq_reply(final_content_for_ai, channel_id, current_history, model_name="openai/gpt-oss-120b")

                    if not raw_reply_text or not raw_reply_text.strip():
                        print("    ⚠️ Primary model failed. Falling back...")
                        raw_reply_text = groq_reply(final_content_for_ai, channel_id, current_history, model_name="llama-3.1-8b-instant")
                    
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

            last_seen[channel_id] = messages[0]["id"]

        time.sleep(5)
    except Exception as e:
        print(f"⚠ Error: {e}")
        time.sleep(10)
