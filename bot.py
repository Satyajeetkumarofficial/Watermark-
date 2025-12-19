import os
import time
import subprocess
from datetime import datetime

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ✅ IMPORT CONFIG
from config import (
    API_ID, API_HASH, BOT_TOKEN,
    OWNER_ID, LOG_CHANNEL,
    MAX_FILE_SIZE,
    DEFAULT_TEXT, DEFAULT_SCALE, DEFAULT_POSITION
)

print("🚀 bot.py loaded", flush=True)

# =========================
# BASIC CONFIG CHECK
# =========================
if not API_ID or not API_HASH or not BOT_TOKEN:
    print("❌ config.py values missing", flush=True)
    while True:
        time.sleep(10)

print("✅ config.py loaded successfully", flush=True)

# =========================
# BOT INIT
# =========================
app = Client(
    "watermark_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# =========================
# MEMORY DB
# =========================
USERS = {}
STATS = {"users": set(), "processed": 0}

def get_user(uid):
    STATS["users"].add(uid)
    if uid not in USERS:
        USERS[uid] = {
            "rename": None,
            "thumb": None,
            "scale": DEFAULT_SCALE,
            "position": DEFAULT_POSITION,
            "awaiting": None,
            "last_msg": None
        }
    return USERS[uid]

# =========================
# BUTTONS
# =========================
buttons = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("✏️ Rename", callback_data="rename"),
        InlineKeyboardButton("🔁 Default", callback_data="default")
    ],
    [
        InlineKeyboardButton("▶️ Start Watermark", callback_data="process")
    ]
])

# =========================
# /start
# =========================
@app.on_message(filters.command("start") & filters.private)
async def start(_, m):
    await m.reply(
        "👋 **Watermark Bot Online**\n\n"
        "🎥 Ek video bhejo\n"
        "✏️ Rename (optional)\n"
        "▶️ Start Watermark dabao"
    )

# =========================
# VIDEO RECEIVE
# =========================
@app.on_message(filters.private & (filters.video | filters.document))
async def receive_video(_, m):
    media = m.video or m.document

    if m.document and not (media.mime_type or "").startswith("video/"):
        return await m.reply("❌ Sirf video files allowed")

    if media.file_size > MAX_FILE_SIZE:
        return await m.reply("❌ Max file size 2GB")

    u = get_user(m.from_user.id)
    u["last_msg"] = m

    await m.reply(
        "👇 Option choose karo",
        reply_markup=buttons
    )

# =========================
# RENAME
# =========================
@app.on_callback_query(filters.regex("^rename$"))
async def rename(_, cq):
    u = get_user(cq.from_user.id)
    u["awaiting"] = "rename"
    await cq.message.reply("✏️ New filename bhejo (without .mp4)")
    await cq.answer()

@app.on_message(filters.text & filters.private)
async def save_text(_, m):
    u = get_user(m.from_user.id)
    if u.get("awaiting") == "rename":
        u["rename"] = m.text.strip()
        u["awaiting"] = None
        await m.reply("✅ Rename saved")

# =========================
# DEFAULT NAME
# =========================
@app.on_callback_query(filters.regex("^default$"))
async def default(_, cq):
    get_user(cq.from_user.id)["rename"] = None
    await cq.message.reply("🔁 Default name set")
    await cq.answer()

# =========================
# PROCESS WATERMARK
# =========================
@app.on_callback_query(filters.regex("^process$"))
async def process(_, cq):
    u = get_user(cq.from_user.id)
    m = u.get("last_msg")

    if not m:
        return await cq.message.reply("❌ Pehle video bhejo")

    status = await cq.message.reply("⏳ Watermark ho raha hai...")

    inp = await m.download()
    out = (u["rename"] or "watermarked") + ".mp4"

    cmd = [
        "ffmpeg", "-y",
        "-i", inp,
        "-vf",
        f"drawtext=text='{DEFAULT_TEXT}':"
        f"fontcolor=white@0.85:"
        f"fontsize=24:"
        f"x=(w-text_w)/2:y=h-text_h-20",
        "-c:v", "libx264",
        "-preset", "fast",
        "-c:a", "copy",
        "-movflags", "+faststart",
        out
    ]

    subprocess.run(cmd, check=True)

    STATS["processed"] += 1

    await cq.message.reply_video(
        out,
        supports_streaming=True,
        caption="✅ Watermark added"
    )

    # LOG CHANNEL
    try:
        await app.send_message(
            LOG_CHANNEL,
            f"🎬 New Video\n"
            f"👤 User: {cq.from_user.id}\n"
            f"📁 File: {out}\n"
            f"⏰ {datetime.now()}"
        )
    except:
        pass

    await status.delete()
    os.remove(inp)
    os.remove(out)

print("🤖 Bot starting...", flush=True)
app.run()
