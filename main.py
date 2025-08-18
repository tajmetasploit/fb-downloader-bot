

# main.py
from functools import partial
import asyncio
import yt_dlp
import datetime
import os
import json
import tempfile
import logging
from threading import Thread
from telegram.error import Forbidden
from dotenv import load_dotenv
from flask import Flask
from yt_dlp import YoutubeDL
from telegram import error
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError
#from telegram import Unauthorized
from telegram.constants import ParseMode
from telegram.error import TelegramError
import os
import json
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

load_dotenv()
#MAX_TELEGRAM_FILESIZE = 50 * 1024 * 1024  # 50 MB    2 * 1024 * 1024 * 1024  # 2 GB 
MAX_TELEGRAM_FILESIZE = 2 * 1024 * 1024 * 1024  # 2 GB 

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not found in environment. Put it in .env")
"""
import asyncio
import requests
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

URL = "https://vpnifyapp.com/connectioncheck"

async def keep_vpn_alive():
    while True:
        try:
            r = requests.get(URL, timeout=10)  # timeout in case VPN is down
            if r.status_code == 200:
                print("VPN alive ✅")
            else:
                print(f"VPN check failed, status: {r.status_code} ⚠️")
                await asyncio.sleep(60)  # sleep 1 minute if failed
        except requests.RequestException as e:
            print(f"VPN not reachable ❌: {e}")
            await asyncio.sleep(60)  # sleep 1 minute if exception occurs
        await asyncio.sleep(300)  # 5 minutes between checks

"""
# ---------- Logging ----------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ---------- Flask keep-alive (Replit / uptime) ----------
flask_app = Flask("")

@flask_app.route("/")
def home():
    return "د ډاونلوډر بوټ روان دی!"

def run_web():
    port = int(os.getenv("PORT", 8000))
    flask_app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run_web, daemon=True)
    t.start()

# ---------- Persistence (users) ----------
USERS_FILE = "users.jsonl"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load existing users
def load_users():
    users = {}
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    user = json.loads(line)
                    users[str(user["id"])] = user
    return users

# Save all users
def save_all_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        for user_data in users.values():
            json.dump(user_data, f, ensure_ascii=False)
            f.write("\n")

MY_TELEGRAM_ID = 6384333518

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ----------------- GLOBAL USERS -----------------
users = {}

# ----------------- LOAD/ SAVE USERS -----------------
def load_users():
    global users
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    user = json.loads(line)
                    users[str(user["id"])] = user
    logger.info(f"Loaded {len(users)} users")

def save_all_users():
    global users
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        for user_data in users.values():
            json.dump(user_data, f, ensure_ascii=False)
            f.write("\n")
    logger.info(f"Saved {len(users)} users to {USERS_FILE}")

# ----------------- SAVE/UPDATE SINGLE USER -----------------
async def save_user(user, bot=None):
    global users   # must come first inside the function

    user_id = str(user.id)
    is_new = user_id not in users

    users[user_id] = {
        "id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "language_code": getattr(user, "language_code", None),
    }

    save_all_users()   # no argument if using global
    logger.info(f"Saved/updated user {user_id}")

    if is_new and bot:
        try:
            text = (

                f"🆕 <b>New User Joined</b>\n"
                f"🔑 ID: <a href='tg://user?id={user.id}'>{user.id}</a>\n"
                f"📛 Username: @{user.username if user.username else 'N/A'}\n"
                f"👤 Name: {user.first_name} {user.last_name or ''}\n"
                f"🌐 Language: {getattr(user, 'language_code', 'N/A')}"

            )

            await bot.send_message(
                chat_id=MY_TELEGRAM_ID,
                text=text,
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Failed to notify about new user {user_id}: {e}")

# ---------- Settings ----------
MAX_UPLOAD_SIZE = 100 * 1024 * 1024   # 100 MB: upload threshold for Telegram
TELEGRAM_MSG_LIMIT = 4000            # use <4096 for safety

SUPPORTED_DOMAINS = [
    "facebook.com", "fb.watch",
    "tiktok.com",
    "instagram.com", "instagr.am",
    "vk.com", "vkontakte.ru",
    "snapchat.com", "scnd.co",
    "youtube.com", "youtu.be"
]

# ---------- Helper functions ----------

def is_supported_url(url: str) -> bool:
    if not url:
        return False
    url = url.strip().lower()
    return any(domain in url for domain in SUPPORTED_DOMAINS)

async def send_text_or_file(chat_id: int, text: str, context: ContextTypes.DEFAULT_TYPE, filename_hint: str = "message.txt"):
    """
    If text is short, send as plain message.
    If text is long (> TELEGRAM_MSG_LIMIT), save as text file and send as document to avoid 'Message is too long'.
    """
    safe_text = text or ""
    if len(safe_text) <= TELEGRAM_MSG_LIMIT:
        await context.bot.send_message(chat_id=chat_id, text=safe_text)
        return

    # send as .txt file
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as tf:
            tf.write(safe_text)
            tmp_name = tf.name

        with open(tmp_name, "rb") as doc:
            await context.bot.send_document(chat_id=chat_id, document=doc, filename=filename_hint)
    except Exception as e:
        logger.error("Failed to send long text as file: %s", e, exc_info=True)
        # fallback: send truncated text
        await context.bot.send_message(chat_id=chat_id, text=safe_text[:TELEGRAM_MSG_LIMIT] + "\n\n...[message truncated]")
    finally:
        try:
            if os.path.exists(tmp_name):
                os.remove(tmp_name)
        except Exception:
            pass

# ---------- Bot handlers ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Telegram bot handlers
    user = update.effective_user
    await save_user(user, bot=context.bot)


    #save_user(user, bot=context.bot)  # pass the bot instance
    #await save_user(update.effective_user, bot=context.bot)

    #save_user(update.effective_user)  # save new user automatically
    user_count = len(users)
    
    start_text = (
        "📥 مهرباني وکړئ د فیسبوک، ټیک ټاک، انسټاګرام، وی کی، سنپ‌چټ او یا یوټیوب د ویډیو یا ریل لینک واستوئ؛ زه به یې ستاسو لپاره ښکته کړم.\n\n"
        "✅ تاسی کولای شی چی د لاندی لیکل شوی پلیټفارمونو لینک واستوئ:\n"
        "- د فیسبوک ویډیوګانې او ریل\n"
        "- د ټیک ټاک ویډیوګانې او ریل\n"
        "- د انسټاګرام ویډیوګانې او ریل\n"
        "- د VK ویډیوګانې\n"
        "- د سنپ‌چټ ویډیوګانې\n"
        "- د یوټیوب ویډیوګانې\n\n"
        "❗ خصوصي ویډیوګانې نه ښکته کوی .\n\n"
        f"👥 اوس مهال {user_count} کارونکي دا بوټ کاروي."
    )
    await send_text_or_file(update.effective_chat.id, start_text, context, filename_hint="start_info.txt")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Optional: show user count via /stats
    await send_text_or_file(update.effective_chat.id, f"👥 Unique users: {len(users)}", context, filename_hint="stats.txt")


MAX_UPLOAD_SIZE = 2 * 1024 * 1024 * 1024  # 2 GB

PLATFORM_NAMES = {
    "facebook.com": "Facebook",
    "fb.watch": "Facebook",
    "tiktok.com": "TikTok",
    "instagram.com": "Instagram",
    "vk.com": "VK",
    "snapchat.com": "Snapchat",
    "youtube.com": "YouTube",
    "youtu.be": "YouTube",
}

def get_platform_name(url: str) -> str:
    for key, name in PLATFORM_NAMES.items():
        if key in url:
            return name
    return "Unknown"
from telegram.error import Forbidden

async def send_text_or_file(chat_id, text, context, filename_hint=None):
    """
    Send a message safely. If user blocked the bot -> just skip.
    """
    try:
        await context.bot.send_message(chat_id=chat_id, text=text)
    except Forbidden:
        # User blocked the bot
        print(f"⚠️ Cannot send message to {chat_id}: user blocked the bot.")
        return
    except Exception as e:
        # Other errors (network issues, invalid chat, etc.)
        print(f"⚠️ Failed to send message to {chat_id}: {e}")


#ADMIN_ID = 6384333518  # Your Telegram ID


async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = update.message
    if not message or not message.text:
        return

    url = message.text.strip()
    if not is_supported_url(url):
        await send_text_or_file(
            update.effective_chat.id,
            "❌ مهرباني وکړئ د لاندی لیکل شویو سوشل میدیا بلتفارم لینک (Facebook, TikTok, Instagram, VK, Snapchat, YouTube) لینک واستوئ.",
            context,
            filename_hint="error.txt",
        )
        return

    platform = get_platform_name(url)
    user = update.effective_user
    # Save or update user in users dict
    save_user(user)

    """  # Add user to persistent set if new
    user_id = update.effective_user.id
    if user_id not in users:
        users.add(user_id)
        save_user(update.effective_user)  """# pass the actual Telegram user object


    await send_text_or_file(update.effective_chat.id, "⏳ مهرباني وکړئ لږ صبر وکړئ — ویډیو ښکته کېږي...", context, filename_hint="downloading.txt")
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_VIDEO)

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            ydl_opts = {
                "outtmpl": os.path.join(tmpdir, "video.%(ext)s"),
                "format": "best",
                "noplaylist": True,
                "quiet": True,
                "no_warnings": True,
                "http_headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                                  "(KHTML, like Gecko) Chrome/115.0 Safari/537.36",
                },

            }

            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)

            if not os.path.exists(file_path):
                await send_text_or_file(update.effective_chat.id, "❌ ویډیو ډاونلوډ نشوه.", context, filename_hint="error.txt")
                return                      

            # Silent logging of downloaded URL
            with open("downloads.txt", "a", encoding="utf-8") as f:
                f.write(f"{datetime.datetime.now().isoformat()} — {url}\n")

            file_size = os.path.getsize(file_path)
            duration = info.get("duration")
            duration_str = f"{int(duration//60)} دقیقې {int(duration%60)} ثانیې" if duration else "نامعلومه"
            resolution = info.get("height") or info.get("format_note") or "نامعلومه"
            title = info.get("title") or "ویډیو"

            info_text = (
                f"🎬 سرلیک: {title}\n"
                f"⏱ موده: {duration_str}\n"
                f"📺 کیفیت: {resolution}\n"
                f"📁 اندازه: {file_size/1024/1024:.2f} MB\n"
            )

            # send info
            await send_text_or_file(update.effective_chat.id, info_text, context, filename_hint="video_info.txt")

            # 🔹 Send video to user first
            #sent_message = None
            if file_size <= MAX_UPLOAD_SIZE:
                try:
                    with open(file_path, "rb") as vidf:
                        #await message.reply_video(vidf, caption="✅ ستاسو ویډیو")
                        await message.reply_video(vidf, caption="✅ ستاسو ویډیو")
                except Exception as e:
                    logger.error("Upload to user failed: %s", e, exc_info=True)
                    direct = info.get("url") or info.get("webpage_url") or url
                    await send_text_or_file(
                        update.effective_chat.id,
                        "⚠️ د ویډیو اپلوډولو کې ستونزه راغله. لطفاً دا لینک په براوزر کې خلاص کړئ:\n\n" + direct,
                        context,
                        filename_hint="download_link.txt",
                    )
            else:
                # Too big -> send direct link
                direct = info.get("url") or info.get("webpage_url") or url
                await send_text_or_file(
                    update.effective_chat.id,
                    "⚠️ ویډیو ډېره لویه ده دلته نه لیږل کیژی.\n\n"
                    "📎 مهرباني وکړئ لاندې لینک په براوزر کې خلاص کړئ او ویډیو ښکته کړئ:\n\n"
                    + direct,
                    context,
                    filename_hint="download_link.txt",
                )

            # Send to channel silently with clickable user and platform
            try:
                with open(file_path, "rb") as vidf:
                    user_link = f"[{update.effective_user.full_name}](tg://user?id={user.id})"
                    channel_caption = (
                        f"Requested by {user_link}\n"
                        f"🎬 {title}\n"
                        f"⏱ {duration_str}\n"
                        f"📺 {resolution}\n"
                        f"📁 {file_size/1024/1024:.2f} MB\n"
                        f"🌐 {platform}"
                    )
                    await context.bot.send_video(
                        chat_id="@chgddffff",  # replace with your channel username or ID
                        video=vidf,
                        caption=channel_caption,
                        parse_mode="Markdown"
                    )
            except Exception as e:
                logger.error("Failed to send video to channel: %s", e, exc_info=True)

    except Exception as e:
        err_str = str(e)
        logger.error("Error processing url: %s", err_str, exc_info=True)
        if "Restricted Video" in err_str or "you must be 18 years old" in err_str.lower():
            await send_text_or_file(
                update.effective_chat.id,
                "⚠️ دا ویډیو د عمر محدودیت لري (۱۸+). د لاگین یا کوکیز پرته ډاونلوډ ممکن نه دی.",
                context,
                filename_hint="error.txt",
            )
        else:
            await send_text_or_file(
                update.effective_chat.id,
                f"⚠️ د لینک د پروسس پر مهال تېروتنه وشوه:\n{err_str}",
                context,
                filename_hint="error.txt"
            )

VIDEO_LINKS_FILE = "downloads.txt"  # file where links are saved

def get_total_downloads():
    # If file doesn't exist → return 0 without creating it
    if not os.path.exists(VIDEO_LINKS_FILE):
        return 0
    try:
        with open(VIDEO_LINKS_FILE, "r", encoding="utf-8") as f:
            return sum(1 for _ in f if _.strip())
    except Exception as e:
        logger.error("Failed to read video links file: %s", e)
        return 0

# Command handler to show total downloads
async def total(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total_downloads = get_total_downloads()
    await send_text_or_file(
        update.effective_chat.id,
        f"📥 ټوله ښکته شوې ویډیوګانې: {total_downloads}",
        context,
        filename_hint="downloads.txt",
    )

# ---------- Run bot ----------
if __name__ == "__main__":
    load_users()

    keep_alive()  # your existing keep-alive function
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # ----- Handlers -----
    # Save new users automatically when they send /start
    async def start_wrapper(update, context):
        #await save_user(update.effective_user)  # save/update user
        #save_user(update.effective_user)  # save/update user
        await start(update, context)  # call your original start handler
    app.add_handler(CommandHandler("start", start_wrapper))
    app.add_handler(CommandHandler("stats", stats))  # optional
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    app.add_handler(CommandHandler("total", total))
    app.add_handler(CommandHandler("start", start))

    # Optionally, save any user who sends a message (text, media, etc.)
    async def save_any_user(update, context):
        save_user(update.effective_user)  # save/update user
    app.add_handler(MessageHandler(filters.ALL, save_any_user))

    print("🚀 Bot is running...")
    app.run_polling()
"""
# ----- Start VPN task and bot together -----
    async def run_bot():
        asyncio.create_task(keep_vpn_alive())
        await app.run_polling()

    asyncio.run(run_bot())
"""