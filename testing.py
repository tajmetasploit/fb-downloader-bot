"""


import json
import asyncio
from telegram import Bot
from telegram.error import TelegramError

TOKEN = "8058688084:AAG0LreV_E0vaQPqEW9QC9-TYRCDgp4lyp4"
bot = Bot(token=TOKEN)

async def fetch_users():
    # Load user IDs from your JSON
    with open("/Users/Uzer/fb-downloader-bot/users1.json", "r") as f:
        user_ids = json.load(f)

    users_details = {}

    for user_id in user_ids:
        try:
            user = await bot.get_chat(user_id)  # <-- await here
            users_details[user_id] = {
                "id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                #"is_bot": user.is_bot
            }
        except TelegramError as e:
            print(f"Failed to get info for {user_id}: {e}")

    # Save to JSON
    with open("users_full.json", "w") as f:
        json.dump(users_details, f, indent=4)

    print("Done! Full user info saved in users_full.json")

# Run the async function
asyncio.run(fetch_users())
"""

"""import json

# Load your JSON file
with open("users_full.json", "r", encoding="utf-8") as f:
    users = json.load(f)

# Open a new text file to save readable output
with open("users_readable.txt", "w", encoding="utf-8") as out_file:
    for user_id, info in users.items():
        username = info.get("username") or "No username"
        first_name = info.get("first_name") or ""
        last_name = info.get("last_name") or ""
        
        line = f"ID: {user_id} | Username: {username} | Name: {first_name} {last_name}\n"
        out_file.write(line)

print("Users have been decoded and saved to users_readable.txt")
"""
"""
import json
from telegram import Bot
from telegram.constants import ParseMode

# ===== Load your JSON data =====
with open("users_full.json", "r", encoding="utf-8") as f:
    users_data = json.load(f)

# ===== Telegram bot setup =====
BOT_TOKEN = "8058688084:AAG0LreV_E0vaQPqEW9QC9-TYRCDgp4lyp4"
CHAT_ID = "6384333518"  # can be your chat or a group id

bot = Bot(BOT_TOKEN)

# ===== Prepare message =====
message_lines = ["<b>Users in Bot:</b>"]

# Check if users_data is a dict or a list
if isinstance(users_data, dict):
    iterable = users_data.items()
elif isinstance(users_data, list):
    # convert list to (id, info) tuples for uniformity
    iterable = ((user.get("id"), user) for user in users_data)
else:
    raise ValueError("Invalid JSON format: expected dict or list")

for user_id, info in iterable:
    first_name = info.get("first_name") or ""
    last_name = info.get("last_name") or ""
    full_name = f"{first_name} {last_name}".strip()

    username = info.get("username")
    if username:
        # clickable link
        line = f'<a href="https://t.me/{username}">{full_name}</a>'
    else:
        # fallback: show name + ID
        line = f'{full_name} (ID: {user_id})'

    message_lines.append(line)

message_text = "\n".join(message_lines)

# ===== Send message =====
bot.send_message(chat_id=CHAT_ID, text=message_text, parse_mode=ParseMode.HTML)
print("Message sent successfully!")
"""
"""
import json
import asyncio
from telegram import Bot
from telegram.constants import ParseMode

# Load JSON
with open("users_full.json", "r", encoding="utf-8") as f:
    users_data = json.load(f)

BOT_TOKEN = "8058688084:AAG0LreV_E0vaQPqEW9QC9-TYRCDgp4lyp4"
CHAT_ID = "6384333518"  # your chat or group id

bot = Bot(BOT_TOKEN)

async def send_users():
    message_lines = ["<b>Users in Bot:</b>"]
    for user_id, info in users_data.items():
        first_name = info.get("first_name") or ""
        last_name = info.get("last_name") or ""
        full_name = f"{first_name} {last_name}".strip()

        username = info.get("username")
        if username:
            # clickable via username
            line = f'<a href="https://t.me/{username}">{full_name}</a>'
        else:
            # clickable via Telegram ID
            line = f'<a href="tg://user?id={user_id}">{full_name}</a>'

        message_lines.append(line)

    message_text = "\n".join(message_lines)
    await bot.send_message(chat_id=CHAT_ID, text=message_text, parse_mode=ParseMode.HTML)
    print("Message sent successfully!")

# Run the async function
asyncio.run(send_users())

"""

import json

# Load your existing JSON file
with open("users_full.json", "r", encoding="utf-8") as f:
    users_data = json.load(f)  # likely a dict keyed by user_id

# Open a new file to write line-by-line JSON
with open("users_lines.jsonl", "w", encoding="utf-8") as f:
    for user_id, info in users_data.items():
        # Build user object
        user_obj = {
            "id": user_id,
            "username": info.get("username"),
            "first_name": info.get("first_name"),
            "last_name": info.get("last_name"),
            "language_code": info.get("language_code", "en")  # default "en" if missing
        }

        # Write JSON as a single line
        f.write(json.dumps(user_obj, ensure_ascii=False) + "\n")

print("Converted to line-by-line JSON successfully!")
