"""import os
import tempfile
import logging
from threading import Thread

from dotenv import load_dotenv
from flask import Flask
from yt_dlp import YoutubeDL

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not found in environment. Put it in .env")

# Set up basic logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Flask keep-alive app
flask_app = Flask("")

@flask_app.route("/")
def home():
    return "FB Downloader Bot is running!"

def run_web():
    port = int(os.getenv("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run_web, daemon=True)
    t.start()


NORMAL_LIMIT = 50 * 1024 * 1024         # 50 MB
PREMIUM_LIMIT = 2 * 1024 * 1024 * 1024  # 2 GB

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📥 Send me a **public Facebook** video or reel link and I'll download it for you.\n\n"
        "✅ Works with:\n- Facebook Reels\n- Facebook Videos\n- fb.watch short links\n\n"
        "❗ Private videos are not supported."
    )

def is_facebook_url(url: str) -> bool:
    if not url:
        return False
    url = url.strip()
    return any(domain in url for domain in ("facebook.com", "fb.watch"))

async def download_fb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    url = message.text.strip()
    if not is_facebook_url(url):
        await message.reply_text("❌ Please send a valid Facebook video/reel link (facebook.com or fb.watch).")
        return

    await message.reply_text("⏳ Downloading... please wait.")
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_VIDEO)

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            ydl_opts = {
                "outtmpl": os.path.join(tmpdir, "video.%(ext)s"),
                "format": "best",
                "noplaylist": True,
                "quiet": True,
                "no_warnings": True,
            }
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)

            if not os.path.exists(file_path):
                await message.reply_text("❌ Failed to locate downloaded file.")
                return

            file_size = os.path.getsize(file_path)
            user_is_premium = getattr(update.effective_user, "is_premium", False)
            limit = PREMIUM_LIMIT if user_is_premium else NORMAL_LIMIT

            # Log info
            logger.info(f"Downloaded file: {file_path} ({file_size/1024/1024:.2f} MB)")
            logger.info(f"User premium status: {user_is_premium}")

            # Video metadata to show before sending
            duration = info.get("duration")
            duration_str = f"{int(duration//60)}m {int(duration%60)}s" if duration else "unknown"
            resolution = info.get("height") or info.get("format_note") or "unknown"
            title = info.get("title") or "video"

            await message.reply_text(
                f"🎬 Title: {title}\n"
                f"⏱ Duration: {duration_str}\n"
                f"📺 Resolution: {resolution}\n"
                f"📁 Size: {file_size/1024/1024:.2f} MB\n"
            )

            if file_size <= limit:
                with open(file_path, "rb") as f:
                    await message.reply_video(f, caption="✅ Here is your video")
            else:
                download_url = info.get("url") or info.get("webpage_url") or info.get("original_url")
                if download_url:
                    await message.reply_text(
                        "⚠️ The video is too large to send via Telegram.\n\n"
                        "📎 Use the direct download link below in your browser to download the file:\n\n"
                        f"{download_url}"
                    )
                else:
                    await message.reply_text("❌ The video is too large to send and no download link is available.")

    except Exception as e:
        logger.error(f"Error processing video: {e}", exc_info=True)
        await message.reply_text(f"⚠️ Error while processing the link:\n{str(e)}")


if __name__ == "__main__":
    keep_alive()
    bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_fb))

    print("🚀 Bot is running...")
    bot_app.run_polling()
"""

"""import os
import tempfile
import logging
from threading import Thread

from dotenv import load_dotenv
from flask import Flask
from yt_dlp import YoutubeDL

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not found in environment. Put it in .env")

# Set up basic logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Flask keep-alive app
flask_app = Flask("")

@flask_app.route("/")
def home():
    return "Multi-platform Downloader Bot is running!"

def run_web():
    port = int(os.getenv("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run_web, daemon=True)
    t.start()


NORMAL_LIMIT = 50 * 1024 * 1024         # 50 MB
PREMIUM_LIMIT = 2 * 1024 * 1024 * 1024  # 2 GB

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📥 Send me a **public** video or reel link from Facebook, TikTok, or Instagram, and I'll download it for you.\n\n"
        "✅ Supported platforms:\n"
        "- Facebook Videos & Reels\n"
        "- TikTok Videos & Reels\n"
        "- Instagram Videos & Reels\n\n"
        "❗ Private videos are not supported."
    )

def is_supported_url(url: str) -> bool:
    if not url:
        return False
    url = url.strip().lower()
    supported_domains = [
        "facebook.com", "fb.watch",
        "tiktok.com",
        "instagram.com", "instagr.am"
    ]
    return any(domain in url for domain in supported_domains)

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    url = message.text.strip()
    if not is_supported_url(url):
        await message.reply_text(
            "❌ Please send a valid Facebook, TikTok, or Instagram video/reel link."
        )
        return

    await message.reply_text("⏳ Downloading... please wait.")
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_VIDEO)

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            ydl_opts = {
                "outtmpl": os.path.join(tmpdir, "video.%(ext)s"),
                "format": "best",
                "noplaylist": True,
                "quiet": True,
                "no_warnings": True,
            }
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)

            if not os.path.exists(file_path):
                await message.reply_text("❌ Failed to locate downloaded file.")
                return

            file_size = os.path.getsize(file_path)
            user_is_premium = getattr(update.effective_user, "is_premium", False)
            limit = PREMIUM_LIMIT if user_is_premium else NORMAL_LIMIT

            # Log info
            logger.info(f"Downloaded file: {file_path} ({file_size/1024/1024:.2f} MB)")
            logger.info(f"User premium status: {user_is_premium}")

            # Video metadata to show before sending
            duration = info.get("duration")
            duration_str = f"{int(duration//60)}m {int(duration%60)}s" if duration else "unknown"
            resolution = info.get("height") or info.get("format_note") or "unknown"
            title = info.get("title") or "video"

            await message.reply_text(
                f"🎬 Title: {title}\n"
                f"⏱ Duration: {duration_str}\n"
                f"📺 Resolution: {resolution}\n"
                f"📁 Size: {file_size/1024/1024:.2f} MB\n"
            )

            if file_size <= limit:
                with open(file_path, "rb") as f:
                    await message.reply_video(f, caption="✅ Here is your video")
            else:
                download_url = info.get("url") or info.get("webpage_url") or info.get("original_url")
                if download_url:
                    await message.reply_text(
                        "⚠️ The video is too large to send via Telegram.\n\n"
                        "📎 Use the direct download link below in your browser to download the file:\n\n"
                        f"{download_url}"
                    )
                else:
                    await message.reply_text("❌ The video is too large to send and no download link is available.")

    except Exception as e:
        logger.error(f"Error processing video: {e}", exc_info=True)
        await message.reply_text(f"⚠️ Error while processing the link:\n{str(e)}")


if __name__ == "__main__":
    keep_alive()
    bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    print("🚀 Bot is running...")
    bot_app.run_polling()
"""

"""import os
import tempfile
import logging
from threading import Thread

from dotenv import load_dotenv
from flask import Flask
from yt_dlp import YoutubeDL

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
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not found in environment. Put it in .env")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

flask_app = Flask("")

@flask_app.route("/")
def home():
    return "د ډاونلوډر بوټ روان دی!"

def run_web():
    port = int(os.getenv("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run_web, daemon=True)
    t.start()

NORMAL_LIMIT = 50 * 1024 * 1024
PREMIUM_LIMIT = 2 * 1024 * 1024 * 1024

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📥 مهرباني وکړئ ما ته د فېسبوک، ټيک ټاک يا انسټاګرام د عامو ویډیو یا ریل لینک واستوئ، زه به یې ستاسو لپاره ښکته کړم.\n\n"
        "✅ ملاتړ شوی پلیټفارمونه:\n"
        "- د فېسبوک ویډیوګانې او ریلونه\n"
        "- د ټيک ټاک ویډیوګانې او ریلونه\n"
        "- د انسټاګرام ویډیوګانې او ریلونه\n\n"
        "❗ شخصي ویډیوګانې ملاتړ نه کیږي."
    )

def is_supported_url(url: str) -> bool:
    if not url:
        return False
    url = url.strip().lower()
    supported_domains = [
        "facebook.com", "fb.watch",
        "tiktok.com",
        "instagram.com", "instagr.am"
    ]
    return any(domain in url for domain in supported_domains)

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    url = message.text.strip()
    if not is_supported_url(url):
        await message.reply_text(
            "❌ مهرباني وکړئ د فېسبوک، ټيک ټاک، يا انسټاګرام د ویډیو یا ریل معتبر لینک واستوئ."
        )
        return

    await message.reply_text("⏳ مهرباني وکړئ انتظار وکړئ، ویډیو ښکته کیږي...")
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_VIDEO)

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            ydl_opts = {
                "outtmpl": os.path.join(tmpdir, "video.%(ext)s"),
                "format": "best",
                "noplaylist": True,
                "quiet": True,
                "no_warnings": True,
            }
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)

            if not os.path.exists(file_path):
                await message.reply_text("❌ ویډیو ښکته کول ناکام شول.")
                return

            file_size = os.path.getsize(file_path)
            user_is_premium = getattr(update.effective_user, "is_premium", False)
            limit = PREMIUM_LIMIT if user_is_premium else NORMAL_LIMIT

            logger.info(f"Downloaded file: {file_path} ({file_size/1024/1024:.2f} MB)")
            logger.info(f"User premium status: {user_is_premium}")

            duration = info.get("duration")
            duration_str = f"{int(duration//60)} دقیقې {int(duration%60)} ثانيې" if duration else "نامعلومه"
            resolution = info.get("height") or info.get("format_note") or "نامعلومه"
            title = info.get("title") or "ویډیو"

            await message.reply_text(
                f"🎬 عنوان: {title}\n"
                f"⏱ موده: {duration_str}\n"
                f"📺 کیفیت: {resolution}\n"
                f"📁 اندازه: {file_size/1024/1024:.2f} MB\n"
            )

            if file_size <= limit:
                with open(file_path, "rb") as f:
                    await message.reply_video(f, caption="✅ دلته ستاسو ویډیو ده")
            else:
                download_url = info.get("url") or info.get("webpage_url") or info.get("original_url")
                if download_url:
                    await message.reply_text(
                        "⚠️ ویډیو ډېره لویه ده چې په ټیلیګرام کې ولیږل شي.\n\n"
                        "📎 مهرباني وکړئ لاندې لینک په براوزر کې خلاص کړئ او ویډیو ښکته کړئ:\n\n"
                        f"{download_url}"
                    )
                else:
                    await message.reply_text("❌ ویډیو ډېره لویه ده او د ښکته کولو لینک نشته.")

    except Exception as e:
        err_str = str(e)
        if "Restricted Video" in err_str or "you must be 18 years old" in err_str.lower():
            await message.reply_text(
                "⚠️ دا ویډیو د عمر محدودیت لري (۱۸+).\n"
                "بدبختانه، دا ویډیو پرته له لاگین یا کوکیز څخه ښکته کول ممکن نه دي."
            )
        else:
            await message.reply_text(f"⚠️ د لینک د پروسس په وخت کې تېروتنه وشوه:\n{err_str}")
        logger.error(f"Error processing video: {e}", exc_info=True)


if __name__ == "__main__":
    keep_alive()
    bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    print("🚀 بوټ روان دی...")
    bot_app.run_polling()
"""
"""import os
import tempfile
import logging
from threading import Thread

from dotenv import load_dotenv
from flask import Flask
from yt_dlp import YoutubeDL

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
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not found in environment. Put it in .env")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

flask_app = Flask("")

@flask_app.route("/")
def home():
    return "د ډاونلوډر بوټ روان دی!"

def run_web():
    port = int(os.getenv("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run_web, daemon=True)
    t.start()

NORMAL_LIMIT = 50 * 1024 * 1024
PREMIUM_LIMIT = 2 * 1024 * 1024 * 1024

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📥 مهرباني وکړئ ما ته د فېسبوک، ټيک ټاک، انسټاګرام يا يوټيوب د عامو ویډیو یا ریل لینک واستوئ، زه به یې ستاسو لپاره ښکته کړم.\n\n"
        "✅ ملاتړ شوی پلیټفارمونه:\n"
        "- د فېسبوک ویډیوګانې او ریلونه\n"
        "- د ټيک ټاک ویډیوګانې او ریلونه\n"
        "- د انسټاګرام ویډیوګانې او ریلونه\n"
        "- د يوټيوب ویډیوګانې\n\n"
        "❗ شخصي ویډیوګانې ملاتړ نه کیږي."
    )

def is_supported_url(url: str) -> bool:
    if not url:
        return False
    url = url.strip().lower()
    supported_domains = [
        "facebook.com", "fb.watch",
        "tiktok.com",
        "instagram.com", "instagr.am",
        "youtube.com", "youtu.be"
    ]
    return any(domain in url for domain in supported_domains)

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    url = message.text.strip()
    if not is_supported_url(url):
        await message.reply_text(
            "❌ مهرباني وکړئ د فېسبوک، ټيک ټاک، انسټاګرام، يا يوټيوب د ویډیو یا ریل معتبر لینک واستوئ."
        )
        return

    await message.reply_text("⏳ مهرباني وکړئ انتظار وکړئ، ویډیو ښکته کیږي...")
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_VIDEO)

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            ydl_opts = {
                "outtmpl": os.path.join(tmpdir, "video.%(ext)s"),
                "format": "best",
                "noplaylist": True,
                "quiet": True,
                "no_warnings": True,
            }
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)

            if not os.path.exists(file_path):
                await message.reply_text("❌ ویډیو ښکته کول ناکام شول.")
                return

            file_size = os.path.getsize(file_path)
            user_is_premium = getattr(update.effective_user, "is_premium", False)
            limit = PREMIUM_LIMIT if user_is_premium else NORMAL_LIMIT

            logger.info(f"Downloaded file: {file_path} ({file_size/1024/1024:.2f} MB)")
            logger.info(f"User premium status: {user_is_premium}")

            duration = info.get("duration")
            duration_str = f"{int(duration//60)} دقیقې {int(duration%60)} ثانيې" if duration else "نامعلومه"
            resolution = info.get("height") or info.get("format_note") or "نامعلومه"
            title = info.get("title") or "ویډیو"

            await message.reply_text(
                f"🎬 عنوان: {title}\n"
                f"⏱ موده: {duration_str}\n"
                f"📺 کیفیت: {resolution}\n"
                f"📁 اندازه: {file_size/1024/1024:.2f} MB\n"
            )

            if file_size <= limit:
                with open(file_path, "rb") as f:
                    await message.reply_video(f, caption="✅ دلته ستاسو ویډیو ده")
            else:
                download_url = info.get("url") or info.get("webpage_url") or info.get("original_url")
                if download_url:
                    await message.reply_text(
                        "⚠️ ویډیو ډېره لویه ده چې په ټیلیګرام کې ولیږل شي.\n\n"
                        "📎 مهرباني وکړئ لاندې لینک په براوزر کې خلاص کړئ او ویډیو ښکته کړئ:\n\n"
                        f"{download_url}"
                    )
                else:
                    await message.reply_text("❌ ویډیو ډېره لویه ده او د ښکته کولو لینک نشته.")

    except Exception as e:
        err_str = str(e)
        if "Restricted Video" in err_str or "you must be 18 years old" in err_str.lower():
            await message.reply_text(
                "⚠️ دا ویډیو د عمر محدودیت لري (۱۸+).\n"
                "بدبختانه، دا ویډیو پرته له لاگین یا کوکیز څخه ښکته کول ممکن نه دي."
            )
        else:
            await message.reply_text(f"⚠️ د لینک د پروسس په وخت کې تېروتنه وشوه:\n{err_str}")
        logger.error(f"Error processing video: {e}", exc_info=True)


if __name__ == "__main__":
    keep_alive()
    bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    print("🚀 بوټ روان دی...")
    bot_app.run_polling()
"""

"""import os
import tempfile
import logging
from threading import Thread

from dotenv import load_dotenv
from flask import Flask
from yt_dlp import YoutubeDL

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
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not found in environment. Put it in .env")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

flask_app = Flask("")

@flask_app.route("/")
def home():
    return "د ډاونلوډر بوټ روان دی!"

def run_web():
    port = int(os.getenv("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run_web, daemon=True)
    t.start()

NORMAL_LIMIT = 50 * 1024 * 1024
PREMIUM_LIMIT = 2 * 1024 * 1024 * 1024

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📥 مهرباني وکړئ ما ته د فېسبوک، ټيک ټاک، انسټاګرام، يوټيوب يا ويکېنټاک ویډیو یا ریل لینک واستوئ، زه به یې ستاسو لپاره ښکته کړم.\n\n"
        "✅ ملاتړ شوی پلیټفارمونه:\n"
        "- د فېسبوک ویډیوګانې او ریلونه\n"
        "- د ټيک ټاک ویډیوګانې او ریلونه\n"
        "- د انسټاګرام ویډیوګانې او ریلونه\n"
        "- د يوټيوب ویډیوګانې\n"
        "- د ويکېنټاک (VK) ویډیوګانې\n\n"
        "❗ شخصي ویډیوګانې ملاتړ نه کیږي."
    )

def is_supported_url(url: str) -> bool:
    if not url:
        return False
    url = url.strip().lower()
    supported_domains = [
        "facebook.com", "fb.watch",
        "tiktok.com",
        "instagram.com", "instagr.am",
        "youtube.com", "youtu.be",
        "vk.com", "vkontakte.ru"
    ]
    return any(domain in url for domain in supported_domains)

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    url = message.text.strip()
    if not is_supported_url(url):
        await message.reply_text(
            "❌ مهرباني وکړئ د فېسبوک، ټيک ټاک، انسټاګرام، يوټيوب يا ويکېنټاک د ویډیو یا ریل معتبر لینک واستوئ."
        )
        return

    await message.reply_text("⏳ مهرباني وکړئ انتظار وکړئ، ویډیو ښکته کیږي...")
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_VIDEO)

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            ydl_opts = {
                "outtmpl": os.path.join(tmpdir, "video.%(ext)s"),
                "format": "best",
                "noplaylist": True,
                "quiet": True,
                "no_warnings": True,
            }
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)

            if not os.path.exists(file_path):
                await message.reply_text("❌ ویډیو ښکته کول ناکام شول.")
                return

            file_size = os.path.getsize(file_path)
            user_is_premium = getattr(update.effective_user, "is_premium", False)
            limit = PREMIUM_LIMIT if user_is_premium else NORMAL_LIMIT

            logger.info(f"Downloaded file: {file_path} ({file_size/1024/1024:.2f} MB)")
            logger.info(f"User premium status: {user_is_premium}")

            duration = info.get("duration")
            duration_str = f"{int(duration//60)} دقیقې {int(duration%60)} ثانيې" if duration else "نامعلومه"
            resolution = info.get("height") or info.get("format_note") or "نامعلومه"
            title = info.get("title") or "ویډیو"

            await message.reply_text(
                f"🎬 عنوان: {title}\n"
                f"⏱ موده: {duration_str}\n"
                f"📺 کیفیت: {resolution}\n"
                f"📁 اندازه: {file_size/1024/1024:.2f} MB\n"
            )

            if file_size <= limit:
                with open(file_path, "rb") as f:
                    await message.reply_video(f, caption="✅ دلته ستاسو ویډیو ده")
            else:
                download_url = info.get("url") or info.get("webpage_url") or info.get("original_url")
                if download_url:
                    await message.reply_text(
                        "⚠️ ویډیو ډېره لویه ده چې په ټیلیګرام کې ولیږل شي.\n\n"
                        "📎 مهرباني وکړئ لاندې لینک په براوزر کې خلاص کړئ او ویډیو ښکته کړئ:\n\n"
                        f"{download_url}"
                    )
                else:
                    await message.reply_text("❌ ویډیو ډېره لویه ده او د ښکته کولو لینک نشته.")

    except Exception as e:
        err_str = str(e)
        if "Restricted Video" in err_str or "you must be 18 years old" in err_str.lower():
            await message.reply_text(
                "⚠️ دا ویډیو د عمر محدودیت لري (۱۸+).\n"
                "بدبختانه، دا ویډیو پرته له لاگین یا کوکیز څخه ښکته کول ممکن نه دي."
            )
        else:
            await message.reply_text(f"⚠️ د لینک د پروسس په وخت کې تېروتنه وشوه:\n{err_str}")
        logger.error(f"Error processing video: {e}", exc_info=True)


if __name__ == "__main__":
    keep_alive()
    bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    print("🚀 بوټ روان دی...")
    bot_app.run_polling()
"""
"""
import os
import tempfile
import logging
from threading import Thread

from dotenv import load_dotenv
from flask import Flask
from yt_dlp import YoutubeDL

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
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN نه دی موندل شوی. لطفاً په .env کې یې واچوئ.")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

flask_app = Flask("")

@flask_app.route("/")
def home():
    return "د ډاونلوډر بوټ روان دی!"

def run_web():
    port = int(os.getenv("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run_web, daemon=True)
    t.start()

NORMAL_LIMIT = 50 * 1024 * 1024
PREMIUM_LIMIT = 2 * 1024 * 1024 * 1024

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📥 مهرباني وکړئ ما ته د فېسبوک، ټيک ټاک، انسټاګرام، VK یا Snapchat د عامو ویډیو یا ریل لینک واستوئ، زه به یې ستاسو لپاره ښکته کړم.\n\n"
        "✅ ملاتړ شوی پلیټفارمونه:\n"
        "- د فېسبوک ویډیوګانې او ریلونه\n"
        "- د ټيک ټاک ویډیوګانې او ریلونه\n"
        "- د انسټاګرام ویډیوګانې او ریلونه\n"
        "- د VK ویډیوګانې\n"
        "- د Snapchat ویډیوګانې\n\n"
        "❗ شخصي ویډیوګانې ملاتړ نه کیږي."
    )

def is_supported_url(url: str) -> bool:
    if not url:
        return False
    url = url.strip().lower()
    supported_domains = [
        "facebook.com", "fb.watch",
        "tiktok.com",
        "instagram.com", "instagr.am",
        "youtube.com", "youtu.be",
        "vk.com", "vkontakte.ru",
        "snapchat.com",
    ]
    return any(domain in url for domain in supported_domains)

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    url = message.text.strip()
    if not is_supported_url(url):
        await message.reply_text(
            "❌ مهرباني وکړئ د فېسبوک، ټيک ټاک، انسټاګرام، VK یا Snapchat د ویډیو یا ریل معتبر لینک واستوئ."
        )
        return

    await message.reply_text("⏳ مهرباني وکړئ انتظار وکړئ، ویډیو ښکته کیږي...")
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_VIDEO)

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            ydl_opts = {
                "outtmpl": os.path.join(tmpdir, "video.%(ext)s"),
                "format": "best",
                "noplaylist": True,
                "quiet": True,
                "no_warnings": True,
            }
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)

            if not os.path.exists(file_path):
                await message.reply_text("❌ ویډیو ښکته کول ناکام شول.")
                return

            file_size = os.path.getsize(file_path)
            user_is_premium = getattr(update.effective_user, "is_premium", False)
            limit = PREMIUM_LIMIT if user_is_premium else NORMAL_LIMIT

            logger.info(f"Downloaded file: {file_path} ({file_size/1024/1024:.2f} MB)")
            logger.info(f"User premium status: {user_is_premium}")

            duration = info.get("duration")
            duration_str = f"{int(duration//60)} دقیقې {int(duration%60)} ثانيې" if duration else "نامعلومه"
            resolution = info.get("height") or info.get("format_note") or "نامعلومه"
            title = info.get("title") or "ویډیو"

            await message.reply_text(
                f"🎬 عنوان: {title}\n"
                f"⏱ موده: {duration_str}\n"
                f"📺 کیفیت: {resolution}\n"
                f"📁 اندازه: {file_size/1024/1024:.2f} MB\n"
            )

            if file_size <= limit:
                with open(file_path, "rb") as f:
                    await message.reply_video(f, caption="✅ دلته ستاسو ویډیو ده")
            else:
                download_url = info.get("url") or info.get("webpage_url") or info.get("original_url")
                if download_url:
                    await message.reply_text(
                        "⚠️ ویډیو ډېره لویه ده چې په ټیلیګرام کې ولیږل شي.\n\n"
                        "📎 مهرباني وکړئ لاندې لینک په براوزر کې خلاص کړئ او ویډیو ښکته کړئ:\n\n"
                        f"{download_url}"
                    )
                else:
                    await message.reply_text("❌ ویډیو ډېره لویه ده او د ښکته کولو لینک نشته.")

    except Exception as e:
        err_str = str(e)
        if "Restricted Video" in err_str or "you must be 18 years old" in err_str.lower():
            await message.reply_text(
                "⚠️ دا ویډیو د عمر محدودیت لري (۱۸+).\n"
                "بدبختانه، دا ویډیو پرته له لاگین یا کوکیز څخه ښکته کول ممکن نه دي."
            )
        else:
            await message.reply_text(f"⚠️ د لینک د پروسس په وخت کې تېروتنه وشوه:\n{err_str}")
        logger.error(f"Error processing video: {e}", exc_info=True)


if __name__ == "__main__":
    keep_alive()
    bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    print("🚀 بوټ روان دی...")
    bot_app.run_polling()
"""

"""import os
import tempfile
import logging
from threading import Thread
import json

from dotenv import load_dotenv
from flask import Flask
from yt_dlp import YoutubeDL

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
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not found in environment. Put it in .env")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

flask_app = Flask("")

@flask_app.route("/")
def home():
    return "د ډاونلوډر بوټ روان دی!"

def run_web():
    port = int(os.getenv("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run_web, daemon=True)
    t.start()

NORMAL_LIMIT = 50 * 1024 * 1024
PREMIUM_LIMIT = 2 * 1024 * 1024 * 1024

USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                data = json.load(f)
                return set(data)
        except Exception as e:
            logger.error(f"Failed to load users from {USERS_FILE}: {e}")
    return set()

def save_users(user_ids_set):
    try:
        with open(USERS_FILE, "w") as f:
            json.dump(list(user_ids_set), f)
    except Exception as e:
        logger.error(f"Failed to save users to {USERS_FILE}: {e}")

# Load existing users on start
user_ids = load_users()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📥 مهرباني وکړئ ما ته د فېسبوک، ټيک ټاک، انسټاګرام، VK او یوتیوب د عامو ویډیو یا ریل لینک واستوئ، زه به یې ستاسو لپاره ښکته کړم.\n\n"
        "✅ ملاتړ شوی پلیټفارمونه:\n"
        "- د فېسبوک ویډیوګانې او ریلونه\n"
        "- د ټيک ټاک ویډیوګانې او ریلونه\n"
        "- د انسټاګرام ویډیوګانې او ریلونه\n"
        "- د VK ویډیوګانې\n"
        "- د یوتیوب ویډیوګانې\n\n"
        "❗ شخصي ویډیوګانې ملاتړ نه کیږي."
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    count = len(user_ids)
    await update.message.reply_text(f"📊 ستاسو د بوټ کارونکي: {count} ځانګړي کارونکي دي.")

def is_supported_url(url: str) -> bool:
    if not url:
        return False
    url = url.strip().lower()
    supported_domains = [
        "facebook.com", "fb.watch",
        "tiktok.com",
        "instagram.com", "instagr.am",
        "vk.com",
        "youtube.com", "youtu.be"
    ]
    return any(domain in url for domain in supported_domains)

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_ids:
        user_ids.add(user_id)
        save_users(user_ids)  # Save on new user added

    message = update.message
    if not message or not message.text:
        return

    url = message.text.strip()
    if not is_supported_url(url):
        await message.reply_text(
            "❌ مهرباني وکړئ د فېسبوک، ټيک ټاک، انسټاګرام، VK یا یوتیوب د ویډیو یا ریل معتبر لینک واستوئ."
        )
        return

    await message.reply_text("⏳ مهرباني وکړئ انتظار وکړئ، ویډیو ښکته کیږي...")
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_VIDEO)

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            ydl_opts = {
                "outtmpl": os.path.join(tmpdir, "video.%(ext)s"),
                "format": "best",
                "noplaylist": True,
                "quiet": True,
                "no_warnings": True,
            }
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)

            if not os.path.exists(file_path):
                await message.reply_text("❌ ویډیو ښکته کول ناکام شول.")
                return

            file_size = os.path.getsize(file_path)
            user_is_premium = getattr(update.effective_user, "is_premium", False)
            limit = PREMIUM_LIMIT if user_is_premium else NORMAL_LIMIT

            logger.info(f"Downloaded file: {file_path} ({file_size/1024/1024:.2f} MB)")
            logger.info(f"User premium status: {user_is_premium}")

            duration = info.get("duration")
            duration_str = f"{int(duration//60)} دقیقې {int(duration%60)} ثانيې" if duration else "نامعلومه"
            resolution = info.get("height") or info.get("format_note") or "نامعلومه"
            title = info.get("title") or "ویډیو"

            await message.reply_text(
                f"🎬 عنوان: {title}\n"
                f"⏱ موده: {duration_str}\n"
                f"📺 کیفیت: {resolution}\n"
                f"📁 اندازه: {file_size/1024/1024:.2f} MB\n"
            )

            if file_size <= limit:
                with open(file_path, "rb") as f:
                    await message.reply_video(f, caption="✅ دلته ستاسو ویډیو ده")
            else:
                download_url = info.get("url") or info.get("webpage_url") or info.get("original_url")
                if download_url:
                    await message.reply_text(
                        "⚠️ ویډیو ډېره لویه ده چې په ټیلیګرام کې ولیږل شي.\n\n"
                        "📎 مهرباني وکړئ لاندې لینک په براوزر کې خلاص کړئ او ویډیو ښکته کړئ:\n\n"
                        f"{download_url}"
                    )
                else:
                    await message.reply_text("❌ ویډیو ډېره لویه ده او د ښکته کولو لینک نشته.")

    except Exception as e:
        err_str = str(e)
        if "Restricted Video" in err_str or "you must be 18 years old" in err_str.lower():
            await message.reply_text(
                "⚠️ دا ویډیو د عمر محدودیت لري (۱۸+).\n"
                "بدبختانه، دا ویډیو پرته له لاگین یا کوکیز څخه ښکته کول ممکن نه دي."
            )
        else:
            await message.reply_text(f"⚠️ د لینک د پروسس په وخت کې تېروتنه وشوه:\n{err_str}")
        logger.error(f"Error processing video: {e}", exc_info=True)


if __name__ == "__main__":
    keep_alive()
    bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("stats", stats))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    print("🚀 بوټ روان دی...")
    bot_app.run_polling()
"""
"""
import os
import tempfile
import logging
from threading import Thread

from dotenv import load_dotenv
from flask import Flask
from yt_dlp import YoutubeDL

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
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not found in environment. Put it in .env")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

flask_app = Flask("")

@flask_app.route("/")
def home():
    return "د ډاونلوډر بوټ روان دی!"

def run_web():
    port = int(os.getenv("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run_web, daemon=True)
    t.start()

USERS_FILE = "users.txt"

def add_user(user_id: int):
    users = set()
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            for line in f:
                users.add(line.strip())
    if str(user_id) not in users:
        users.add(str(user_id))
        with open(USERS_FILE, "w") as f:
            for uid in users:
                f.write(f"{uid}\n")

def get_user_count() -> int:
    if not os.path.exists(USERS_FILE):
        return 0
    with open(USERS_FILE, "r") as f:
        return len(f.readlines())

NORMAL_LIMIT = 50 * 1024 * 1024
PREMIUM_LIMIT = 2 * 1024 * 1024 * 1024

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    add_user(user_id)
    user_count = get_user_count()

    await update.message.reply_text(
        "📥 مهرباني وکړئ راته د فیسبوک، ټیک ټاک، انسټاګرام، یوټیوب، وی‌کې یا سنپ‌چټ څخه د عامه ویډیو یا ریل لینک واستوئ.\n\n"
        "✅ ملاتړ شوې ویب‌پاڼې:\n"
        "- د فیسبوک ویډیوګانې او ریل\n"
        "- د ټیک ټاک ویډیوګانې او ریل\n"
        "- د انسټاګرام ویډیوګانې او ریل\n"
        "- د یوټیوب ویډیوګانې\n"
        "- د وی‌کې ویډیوګانې\n"
        "- د سنپ‌چټ ویډیوګانې\n\n"
        "❗ خصوصي ویډیوګانې نه ملاتړ کیږي.\n\n"
        f"👥 زموږ بوټ اوس {user_count} کاروونکي لري."
    )

def is_supported_url(url: str) -> bool:
    if not url:
        return False
    url = url.strip().lower()
    supported_domains = [
        "facebook.com", "fb.watch",
        "tiktok.com",
        "instagram.com", "instagr.am",
        "youtube.com", "youtu.be",
        "vk.com", "ok.ru",
        "snapchat.com"
    ]
    return any(domain in url for domain in supported_domains)

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    url = message.text.strip()
    if not is_supported_url(url):
        await message.reply_text(
            "❌ مهرباني وکړئ د ملاتړ شویو وېب‌پاڼو څخه د ویډیو یا ریل لینک واستوئ."
        )
        return

    await message.reply_text("⏳ مهرباني وکړئ انتظار وکړئ، ویډیو ښکته کیږي...")
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_VIDEO)

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            ydl_opts = {
                "outtmpl": os.path.join(tmpdir, "video.%(ext)s"),
                "format": "best",
                "noplaylist": True,
                "quiet": True,
                "no_warnings": True,
            }
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)

            if not os.path.exists(file_path):
                await message.reply_text("❌ ویډیو ښکته کول ناکام شول.")
                return

            file_size = os.path.getsize(file_path)
            user_is_premium = getattr(update.effective_user, "is_premium", False)
            limit = PREMIUM_LIMIT if user_is_premium else NORMAL_LIMIT

            logger.info(f"Downloaded file: {file_path} ({file_size/1024/1024:.2f} MB)")
            logger.info(f"User premium status: {user_is_premium}")

            duration = info.get("duration")
            duration_str = f"{int(duration//60)} دقیقې {int(duration%60)} ثانيې" if duration else "نامعلومه"
            resolution = info.get("height") or info.get("format_note") or "نامعلومه"
            title = info.get("title") or "ویډیو"

            await message.reply_text(
                f"🎬 عنوان: {title}\n"
                f"⏱ موده: {duration_str}\n"
                f"📺 کیفیت: {resolution}\n"
                f"📁 اندازه: {file_size/1024/1024:.2f} MB\n"
            )

            if file_size <= limit:
                with open(file_path, "rb") as f:
                    await message.reply_video(f, caption="✅ دلته ستاسو ویډیو ده")
            else:
                download_url = info.get("url") or info.get("webpage_url") or info.get("original_url")
                if download_url:
                    await message.reply_text(
                        "⚠️ ویډیو ډېره لویه ده چې په ټیلیګرام کې ولیږل شي.\n\n"
                        "📎 مهرباني وکړئ لاندې لینک په براوزر کې خلاص کړئ او ویډیو ښکته کړئ:\n\n"
                        f"{download_url}"
                    )
                else:
                    await message.reply_text("❌ ویډیو ډېره لویه ده او د ښکته کولو لینک نشته.")

    except Exception as e:
        err_str = str(e)
        if "Restricted Video" in err_str or "you must be 18 years old" in err_str.lower():
            await message.reply_text(
                "⚠️ دا ویډیو د عمر محدودیت لري (۱۸+).\n"
                "بدبختانه، دا ویډیو پرته له لاگین یا کوکیز څخه ښکته کول ممکن نه دي."
            )
        else:
            await message.reply_text(f"⚠️ د لینک د پروسس په وخت کې تېروتنه وشوه:\n{err_str}")
        logger.error(f"Error processing video: {e}", exc_info=True)


if __name__ == "__main__":
    keep_alive()
    bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    print("🚀 بوټ روان دی...")
    bot_app.run_polling()
"""

"""import os
import tempfile
import logging
from threading import Thread

from dotenv import load_dotenv
from flask import Flask
from yt_dlp import YoutubeDL

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
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not found in environment. Put it in .env")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

flask_app = Flask("")

@flask_app.route("/")
def home():
    return "د ډاونلوډر بوټ روان دی!"

def run_web():
    port = int(os.getenv("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run_web, daemon=True)
    t.start()

NORMAL_LIMIT = 50 * 1024 * 1024
PREMIUM_LIMIT = 2 * 1024 * 1024 * 1024

# Keep track of unique users in-memory (will reset on restart)
user_ids = set()

MAX_LENGTH = 4096  # Telegram max message length


async def send_long_message(message_obj, text):
    for i in range(0, len(text), MAX_LENGTH):
        await message_obj.reply_text(text[i:i+MAX_LENGTH])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_ids.add(update.effective_user.id)

    user_count = len(user_ids)
    await update.message.reply_text(
        "📥 مهرباني وکړئ ما ته د فېسبوک، ټيک ټاک يا انسټاګرام د عامو ویډیو یا ریل لینک واستوئ، زه به یې ستاسو لپاره ښکته کړم.\n\n"
        "✅ ملاتړ شوی پلیټفارمونه:\n"
        "- د فېسبوک ویډیوګانې او ریلونه\n"
        "- د ټيک ټاک ویډیوګانې او ریلونه\n"
        "- د انسټاګرام ویډیوګانې او ریلونه\n"
        "- د VK ویډیوګانې\n"
        "- د Snapchat ویډیوګانې\n\n"
        "❗ خصوصي ویډیوګانې نه ملاتړ کیږي.\n\n"
        f"🧑‍💻 اوس مهال کارونکي: {user_count} کسان"
    )


def is_supported_url(url: str) -> bool:
    if not url:
        return False
    url = url.strip().lower()
    supported_domains = [
        "facebook.com", "fb.watch",
        "tiktok.com",
        "instagram.com", "instagr.am",
        "vk.com",
        "snapchat.com"
    ]
    return any(domain in url for domain in supported_domains)


async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    user_ids.add(update.effective_user.id)  # track user usage

    url = message.text.strip()
    if not is_supported_url(url):
        await message.reply_text(
            "❌ مهرباني وکړئ د فېسبوک، ټيک ټاک، انسټاګرام، VK يا Snapchat د ویډیو یا ریل معتبر لینک واستوئ."
        )
        return

    await message.reply_text("⏳ مهرباني وکړئ انتظار وکړئ، ویډیو ښکته کیږي...")
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_VIDEO)

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            ydl_opts = {
                "outtmpl": os.path.join(tmpdir, "video.%(ext)s"),
                "format": "best",
                "noplaylist": True,
                "quiet": True,
                "no_warnings": True,
            }
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)

            if not os.path.exists(file_path):
                await message.reply_text("❌ ویډیو ښکته کول ناکام شول.")
                return

            file_size = os.path.getsize(file_path)
            user_is_premium = getattr(update.effective_user, "is_premium", False)
            limit = PREMIUM_LIMIT if user_is_premium else NORMAL_LIMIT

            logger.info(f"Downloaded file: {file_path} ({file_size/1024/1024:.2f} MB)")
            logger.info(f"User premium status: {user_is_premium}")

            duration = info.get("duration")
            duration_str = f"{int(duration//60)} دقیقې {int(duration%60)} ثانيې" if duration else "نامعلومه"
            resolution = info.get("height") or info.get("format_note") or "نامعلومه"
            title = info.get("title") or "ویډیو"

            info_text = (
                f"🎬 عنوان: {title}\n"
                f"⏱ موده: {duration_str}\n"
                f"📺 کیفیت: {resolution}\n"
                f"📁 اندازه: {file_size/1024/1024:.2f} MB\n"
            )
            await send_long_message(message, info_text)

            if file_size <= limit:
                with open(file_path, "rb") as f:
                    await message.reply_video(f, caption="✅ دلته ستاسو ویډیو ده")
            else:
                download_url = info.get("url") or info.get("webpage_url") or info.get("original_url")
                if download_url:
                    await send_long_message(
                        message,
                        "⚠️ ویډیو ډېره لویه ده چې په ټیلیګرام کې ولیږل شي.\n\n"
                        "📎 مهرباني وکړئ لاندې لینک په براوزر کې خلاص کړئ او ویډیو ښکته کړئ:\n\n"
                        f"{download_url}"
                    )
                else:
                    await message.reply_text("❌ ویډیو ډېره لویه ده او د ښکته کولو لینک نشته.")

    except Exception as e:
        err_str = str(e)
        if "Restricted Video" in err_str or "you must be 18 years old" in err_str.lower():
            await message.reply_text(
                "⚠️ دا ویډیو د عمر محدودیت لري (۱۸+).\n"
                "بدبختانه، دا ویډیو پرته له لاگین یا کوکیز څخه ښکته کول ممکن نه دي."
            )
        else:
            await message.reply_text(f"⚠️ د لینک د پروسس په وخت کې تېروتنه وشوه:\n{err_str}")
        logger.error(f"Error processing video: {e}", exc_info=True)


if __name__ == "__main__":
    keep_alive()
    bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    print("🚀 بوټ روان دی...")
    bot_app.run_polling()
"""
"""
import os
import tempfile
import logging
import json
from threading import Thread

from dotenv import load_dotenv
from flask import Flask
from yt_dlp import YoutubeDL

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
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not found in environment. Put it in .env")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

flask_app = Flask("")

USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                return set(json.load(f))
        except Exception as e:
            logger.error(f"Failed to load users from file: {e}")
            return set()
    return set()

def save_users(user_ids):
    try:
        with open(USERS_FILE, "w") as f:
            json.dump(list(user_ids), f)
    except Exception as e:
        logger.error(f"Failed to save users to file: {e}")

# Load users on startup
user_ids = load_users()

@flask_app.route("/")
def home():
    return "د ډاونلوډر بوټ روان دی!"

def run_web():
    port = int(os.getenv("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run_web, daemon=True)
    t.start()

NORMAL_LIMIT = 50 * 1024 * 1024
PREMIUM_LIMIT = 2 * 1024 * 1024 * 1024

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global user_ids

    user_id = update.effective_user.id
    if user_id not in user_ids:
        user_ids.add(user_id)
        save_users(user_ids)

    users_count = len(user_ids)

    await update.message.reply_text(
        "📥 مهرباني وکړئ ما ته د فېسبوک، ټيک ټاک يا انسټاګرام د عامو ویډیو یا ریل لینک واستوئ، زه به یې ستاسو لپاره ښکته کړم.\n\n"
        "✅ ملاتړ شوی پلیټفارمونه:\n"
        "- د فېسبوک ویډیوګانې او ریلونه\n"
        "- د ټيک ټاک ویډیوګانې او ریلونه\n"
        "- د انسټاګرام ویډیوګانې او ریلونه\n\n"
        "❗ خصوصي ویډیوګانې نه ملاتړ کیږي.\n\n"
        f"👥 فعاله کاروونکي: {users_count} "
    )

def is_supported_url(url: str) -> bool:
    if not url:
        return False
    url = url.strip().lower()
    supported_domains = [
        "facebook.com", "fb.watch",
        "tiktok.com",
        "instagram.com", "instagr.am",
        "vk.com",
        "youtube.com", "youtu.be",
        "snapchat.com"
    ]
    return any(domain in url for domain in supported_domains)

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    url = message.text.strip()
    if not is_supported_url(url):
        await message.reply_text(
            "❌ مهرباني وکړئ د فېسبوک، ټيک ټاک، انسټاګرام، VK، YouTube، يا Snapchat د ویډیو یا ریل معتبر لینک واستوئ."
        )
        return

    await message.reply_text("⏳ مهرباني وکړئ انتظار وکړئ، ویډیو ښکته کیږي...")
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_VIDEO)

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            ydl_opts = {
                "outtmpl": os.path.join(tmpdir, "video.%(ext)s"),
                "format": "best",
                "noplaylist": True,
                "quiet": True,
                "no_warnings": True,
            }
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)

            if not os.path.exists(file_path):
                await message.reply_text("❌ ویډیو ښکته کول ناکام شول.")
                return

            file_size = os.path.getsize(file_path)
            user_is_premium = getattr(update.effective_user, "is_premium", False)
            limit = PREMIUM_LIMIT if user_is_premium else NORMAL_LIMIT

            logger.info(f"Downloaded file: {file_path} ({file_size/1024/1024:.2f} MB)")
            logger.info(f"User premium status: {user_is_premium}")

            duration = info.get("duration")
            duration_str = f"{int(duration//60)} دقیقې {int(duration%60)} ثانيې" if duration else "نامعلومه"
            resolution = info.get("height") or info.get("format_note") or "نامعلومه"
            title = info.get("title") or "ویډیو"

            await message.reply_text(
                f"🎬 عنوان: {title}\n"
                f"⏱ موده: {duration_str}\n"
                f"📺 کیفیت: {resolution}\n"
                f"📁 اندازه: {file_size/1024/1024:.2f} MB\n"
            )

            if file_size <= limit:
                with open(file_path, "rb") as f:
                    await message.reply_video(f, caption="✅ دلته ستاسو ویډیو ده")
            else:
                download_url = info.get("url") or info.get("webpage_url") or info.get("original_url")
                if download_url:
                    await message.reply_text(
                        "⚠️ ویډیو ډېره لویه ده چې په ټیلیګرام کې ولیږل شي.\n\n"
                        "📎 مهرباني وکړئ لاندې لینک په براوزر کې خلاص کړئ او ویډیو ښکته کړئ:\n\n"
                        f"{download_url}"
                    )
                else:
                    await message.reply_text("❌ ویډیو ډېره لویه ده او د ښکته کولو لینک نشته.")

    except Exception as e:
        err_str = str(e)
        if "Restricted Video" in err_str or "you must be 18 years old" in err_str.lower():
            await message.reply_text(
                "⚠️ دا ویډیو د عمر محدودیت لري (۱۸+).\n"
                "بدبختانه، دا ویډیو پرته له لاگین یا کوکیز څخه ښکته کول ممکن نه دي."
            )
        else:
            await message.reply_text(f"⚠️ د لینک د پروسس په وخت کې تېروتنه وشوه:\n{err_str}")
        logger.error(f"Error processing video: {e}", exc_info=True)


if __name__ == "__main__":
    keep_alive()
    bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    print("🚀 بوټ روان دی...")
    bot_app.run_polling()
"""
"""
import os
import json
import tempfile
import logging
from threading import Thread

from dotenv import load_dotenv
from flask import Flask
from yt_dlp import YoutubeDL

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
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not found in environment. Put it in .env")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

flask_app = Flask("")

USERS_JSON_FILE = "users.json"
MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100 MB max upload via bot

def load_users():
    if not os.path.exists(USERS_JSON_FILE):
        return set()
    with open(USERS_JSON_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            return set(data)
        except Exception:
            return set()

def save_users(users_set):
    with open(USERS_JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(list(users_set), f, ensure_ascii=False, indent=2)

users = load_users()

@flask_app.route("/")
def home():
    return "د ډاونلوډر بوټ روان دی!"

def run_web():
    port = int(os.getenv("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run_web, daemon=True)
    t.start()

SUPPORTED_DOMAINS = [
    "facebook.com", "fb.watch",
    "tiktok.com",
    "instagram.com", "instagr.am",
    "vk.com",
    "snapchat.com", "snap.com"
]

def is_supported_url(url: str) -> bool:
    if not url:
        return False
    url = url.strip().lower()
    return any(domain in url for domain in SUPPORTED_DOMAINS + ["youtube.com", "youtu.be"])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Add user ID to tracking set
    user_id = update.effective_user.id
    if user_id not in users:
        users.add(user_id)
        save_users(users)

    user_count = len(users)

    await update.message.reply_text(
        f"📥 مهرباني وکړئ ما ته د فېسبوک، ټيک ټاک، انسټاګرام، ويکي، سنپچېټ، یا یوټیوب د عامو ویډیو یا ریل لینک واستوئ، زه به یې ستاسو لپاره ښکته کړم.\n\n"
        "✅ ملاتړ شوی پلیټفارمونه:\n"
        "- د فېسبوک ویډیوګانې او ریلونه\n"
        "- د ټيک ټاک ویډیوګانې او ریلونه\n"
        "- د انسټاګرام ویډیوګانې او ریلونه\n"
        "- د ويکي ویډیوګانې\n"
        "- د سنپچېټ ویډیوګانې\n"
        "- د یوټیوب ویډیوګانې\n\n"
        "❗ خصوصي ویډیوګانې نه ملاتړ کیږي.\n\n"
        f"👥 اوس مهال کاروونکي: {user_count}"
    )

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    url = message.text.strip()
    if not is_supported_url(url):
        await message.reply_text(
            "❌ مهرباني وکړئ د فېسبوک، ټيک ټاک، انسټاګرام، ويکي، سنپچېټ، یا یوټیوب د ویډیو یا ریل معتبر لینک واستوئ."
        )
        return

    # Track user if new
    user_id = update.effective_user.id
    if user_id not in users:
        users.add(user_id)
        save_users(users)

    await message.reply_text("⏳ مهرباني وکړئ انتظار وکړئ، ویډیو ښکته کیږي...")
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_VIDEO)

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            ydl_opts = {
                "outtmpl": os.path.join(tmpdir, "video.%(ext)s"),
                "format": "best",
                "noplaylist": True,
                "quiet": True,
                "no_warnings": True,
                # Cookies or headers can be added here if needed for age restricted content
            }
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)

            if not os.path.exists(file_path):
                await message.reply_text("❌ ویډیو ښکته کول ناکام شول.")
                return

            file_size = os.path.getsize(file_path)

            duration = info.get("duration")
            duration_str = f"{int(duration//60)} دقیقې {int(duration%60)} ثانيې" if duration else "نامعلومه"
            resolution = info.get("height") or info.get("format_note") or "نامعلومه"
            title = info.get("title") or "ویډیو"

            await message.reply_text(
                f"🎬 عنوان: {title}\n"
                f"⏱ موده: {duration_str}\n"
                f"📺 کیفیت: {resolution}\n"
                f"📁 اندازه: {file_size/1024/1024:.2f} MB\n"
            )

            if file_size <= MAX_UPLOAD_SIZE:
                try:
                    with open(file_path, "rb") as f:
                        await message.reply_video(f, caption="✅ دلته ستاسو ویډیو ده")
                except Exception as e:
                    logger.error(f"Error uploading video: {e}", exc_info=True)
                    await message.reply_text(
                        "⚠️ ویډیو اپلوډ کولو کې ستونزه وشوه، لطفاً په براوزر کې لاندې لینک خلاص کړئ:\n"
                        f"{info.get('url') or info.get('webpage_url') or url}"
                    )
            else:
                # Too large for Telegram upload, send direct link
                await message.reply_text(
                    "⚠️ ویډیو ډېره لویه ده چې دلته ولیږل شي.\n"
                    "لطفاً په براوزر کې لاندې لینک خلاص کړئ او ښکته یې کړئ:\n"
                    f"{info.get('url') or info.get('webpage_url') or url}"
                )

    except Exception as e:
        err_str = str(e)
        if "Restricted Video" in err_str or "you must be 18 years old" in err_str.lower():
            await message.reply_text(
                "⚠️ دا ویډیو د عمر محدودیت لري (۱۸+).\n"
                "بدبختانه، دا ویډیو پرته له لاگین یا کوکیز څخه ښکته کول ممکن نه دي."
            )
        else:
            logger.error(f"Error processing video: {e}", exc_info=True)
            await message.reply_text(f"⚠️ د لینک د پروسس په وخت کې تېروتنه وشوه:\n{err_str}")

if __name__ == "__main__":
    keep_alive()
    bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    print("🚀 بوټ روان دی...")
    bot_app.run_polling()
"""

# main.py
import os
import json
import tempfile
import logging
from threading import Thread

from dotenv import load_dotenv
from flask import Flask
from yt_dlp import YoutubeDL

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
MAX_TELEGRAM_FILESIZE = 50 * 1024 * 1024  # 50 MB
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not found in environment. Put it in .env")

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
    port = int(os.getenv("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run_web, daemon=True)
    t.start()

# ---------- Persistence (users) ----------
USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return set(data)
        except Exception as e:
            logger.error("Failed to load users.json: %s", e)
            return set()
    return set()

def save_users(users_set):
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(list(users_set), f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error("Failed to save users.json: %s", e)

users = load_users()

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
    user_id = update.effective_user.id
    if user_id not in users:
        users.add(user_id)
        save_users(users)

    user_count = len(users)

    start_text = (
        "📥 مهرباني وکړئ راته د فیسبوک، ټیک ټاک، انسټاګرام، وی‌کې، سنپ‌چټ یا یوټیوب د عامه ویډیو یا ریل لینک واستوئ؛ زه به یې ستاسو لپاره ښکته کړم.\n\n"
        "✅ ملاتړ شوي پلیټفارمونه:\n"
        "- د فیسبوک ویډیوګانې او ریل\n"
        "- د ټیک ټاک ویډیوګانې او ریل\n"
        "- د انسټاګرام ویډیوګانې او ریل\n"
        "- د VK ویډیوګانې\n"
        "- د Snapchat ویډیوګانې\n"
        "- د YouTube ویډیوګانې\n\n"
        "❗ خصوصي ویډیوګانې نه ملاتړ کیږي.\n\n"
        f"👥 اوس مهال {user_count} کارونکي دا بوټ کاروي."
    )
    await send_text_or_file(update.effective_chat.id, start_text, context, filename_hint="start_info.txt")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Optional: show user count via /stats
    await send_text_or_file(update.effective_chat.id, f"👥 Unique users: {len(users)}", context, filename_hint="stats.txt")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    url = message.text.strip()
    if not is_supported_url(url):
        await send_text_or_file(
            update.effective_chat.id,
            "❌ مهرباني وکړئ د ملاتړ شوي لینک (Facebook, TikTok, Instagram, VK, Snapchat, YouTube) لینک واستوئ.",
            context,
            filename_hint="error.txt",
        )
        return

    # Add user to persistent set if new
    user_id = update.effective_user.id
    if user_id not in users:
        users.add(user_id)
        save_users(users)

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
                # Optional: pass headers or cookie file if you need to download restricted content
                "http_headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                                  "(KHTML, like Gecko) Chrome/115.0 Safari/537.36",
                },
                # "cookiefile": "cookies.txt",  # uncomment/use if you have cookies
            }

            with YoutubeDL(ydl_opts) as ydl:
                # extract_info downloads the file because download=True
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)

            if not os.path.exists(file_path):
                await send_text_or_file(update.effective_chat.id, "❌ ویډیو ډاونلوډ نشوه.", context, filename_hint="error.txt")
                return

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

            # send info (uses file if too long)
            await send_text_or_file(update.effective_chat.id, info_text, context, filename_hint="video_info.txt")

            # If the file is sufficiently small, try to upload; otherwise send direct link
            if file_size <= MAX_UPLOAD_SIZE:
                try:
                    with open(file_path, "rb") as vidf:
                        await message.reply_video(vidf, caption="✅ ستاسو ویډیو")
                except Exception as e:
                    # If upload fails (network, timeout), fallback to sending direct link and log error
                    logger.error("Upload failed: %s", e, exc_info=True)
                    direct = info.get("url") or info.get("webpage_url") or url
                    await send_text_or_file(
                        update.effective_chat.id,
                        "⚠️ د ویډیو اپلوډولو کې ستونزه راغله. لطفاً دا لینک په براوزر کې خلاص کړئ:\n\n" + direct,
                        context,
                        filename_hint="download_link.txt",
                    )
            else:
                # Too big to upload reliably -> send direct link
                direct = info.get("url") or info.get("webpage_url") or url
                await send_text_or_file(
                    update.effective_chat.id,
                    "⚠️ ویډیو ډېره لویه ده چې دلته ولیږل شي.\n\n"
                    "📎 مهرباني وکړئ لاندې لینک په براوزر کې خلاص کړئ او ویډیو ښکته کړئ:\n\n"
                    + direct,
                    context,
                    filename_hint="download_link.txt",
                )

    except Exception as e:
        # Special-case common yt-dlp messages (age-restricted)
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
            # For very long errors, send as .txt file
            await send_text_or_file(
                update.effective_chat.id,
                f"⚠️ د لینک د پروسس پر مهال تېروتنه وشوه:\n{err_str}",
                context,
                filename_hint="error.txt",
            )

TOTAL_DOWNLOADS_FILE = "total_downloads.txt"

def load_total_downloads():
    if os.path.exists(TOTAL_DOWNLOADS_FILE):
        try:
            with open(TOTAL_DOWNLOADS_FILE, "r", encoding="utf-8") as f:
                return int(f.read().strip())
        except Exception:
            return 0
    return 0

def save_total_downloads(count):
    try:
        with open(TOTAL_DOWNLOADS_FILE, "w", encoding="utf-8") as f:
            f.write(str(count))
    except Exception as e:
        logger.error("Failed to save total downloads: %s", e)

total_downloads = load_total_downloads()

# Inside your download_video handler, after a successful video send (before or after sending video), add:

# if upload success:
total_downloads += 1
save_total_downloads(total_downloads)

async def total(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_text_or_file(
        update.effective_chat.id,
        f"📥 ټوله ښکته شوې ویډیوګانې: {total_downloads}",
        context,
        filename_hint="total_downloads.txt",
    )


# ---------- Run bot ----------
if __name__ == "__main__":
    keep_alive()
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))  # optional
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    app.add_handler(CommandHandler("total", total))


    print("🚀 Bot is running...")
    app.run_polling()
