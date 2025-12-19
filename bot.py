from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import *
from users_db import get_user, stats
from bans_db import is_banned, ban, unban
from watermark import watermark_video
import os
from datetime import datetime

app = Client(
    "watermark_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

buttons = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("✏️ Rename", callback_data="rename"),
        InlineKeyboardButton("🔁 Default", callback_data="default")
    ],
    [
        InlineKeyboardButton("🖼 Thumbnail", callback_data="thumb"),
        InlineKeyboardButton("📏 Scale", callback_data="scale")
    ],
    [
        InlineKeyboardButton("📍 Position", callback_data="position")
    ],
    [
        InlineKeyboardButton("▶️ Start Watermark", callback_data="process")
    ]
])

# 🔒 BAN CHECK
@app.on_message(filters.private)
async def ban_check(_, m):
    if is_banned(m.from_user.id):
        await m.stop_propagation()

# 📊 STATS
@app.on_message(filters.command("stats") & filters.user(OWNER_ID))
async def stats_cmd(_, m):
    await m.reply(
        f"📊 BOT STATS\n\n"
        f"👥 Users: {len(stats['users'])}\n"
        f"🎬 Videos: {stats['processed']}"
    )

# 🎥 VIDEO RECEIVE
@app.on_message(filters.private & (filters.video | filters.document))
async def receive_video(_, m):

    media = m.video or m.document

    if m.document and not (media.mime_type or "").startswith("video/"):
        return await m.reply("❌ Sirf video files allowed")

    if media.file_size > MAX_FILE_SIZE:
        return await m.reply("❌ Maximum file size 2GB")

    u = get_user(m.from_user.id)
    u["last_video_msg"] = m

    await m.reply(
        "👇 Options select karo, phir ▶️ Start Watermark dabao",
        reply_markup=buttons
    )

# ✏️ RENAME
@app.on_callback_query(filters.regex("^rename$"))
async def rename(_, cq):
    u = get_user(cq.from_user.id)
    u["awaiting"] = "rename"
    await cq.message.reply("✏️ New filename bhejo (without .mp4)")
    await cq.answer()

@app.on_message(filters.text & filters.private)
async def text_input(_, m):
    u = get_user(m.from_user.id)

    if u.get("awaiting") == "rename":
        u["rename"] = m.text.strip()
        u["awaiting"] = None
        await m.reply("✅ Rename saved")

# 🔁 DEFAULT
@app.on_callback_query(filters.regex("^default$"))
async def default(_, cq):
    get_user(cq.from_user.id)["rename"] = None
    await cq.message.reply("🔁 Default filename set")
    await cq.answer()

# 🖼 THUMB
@app.on_callback_query(filters.regex("^thumb$"))
async def thumb(_, cq):
    u = get_user(cq.from_user.id)
    u["awaiting"] = "thumb"
    await cq.message.reply("🖼 Thumbnail photo bhejo")
    await cq.answer()

@app.on_message(filters.photo & filters.private)
async def save_thumb(_, m):
    u = get_user(m.from_user.id)
    if u.get("awaiting") == "thumb":
        u["thumb"] = await m.download()
        u["awaiting"] = None
        await m.reply("✅ Thumbnail saved")

# 📏 SCALE
@app.on_callback_query(filters.regex("^scale$"))
async def scale(_, cq):
    get_user(cq.from_user.id)["scale"] = DEFAULT_SCALE
    await cq.message.reply("📏 Scale set")
    await cq.answer()

# 📍 POSITION
@app.on_callback_query(filters.regex("^position$"))
async def position(_, cq):
    get_user(cq.from_user.id)["position"] = DEFAULT_POSITION
    await cq.message.reply("📍 Position set")
    await cq.answer()

# ▶️ PROCESS
@app.on_callback_query(filters.regex("^process$"))
async def process(_, cq):

    u = get_user(cq.from_user.id)
    msg = u.get("last_video_msg")

    if not msg:
        return await cq.message.reply("❌ Pehle video upload karo")

    status = await cq.message.reply("⏳ Video processing...")

    inp = await msg.download()
    out = (u["rename"] or "watermarked") + ".mp4"

    watermark_video(
        inp,
        out,
        DEFAULT_TEXT,
        "logo.png",
        u["scale"],
        u["position"]
    )

    stats["processed"] += 1

    await cq.message.reply_video(
        out,
        thumb=u.get("thumb"),
        supports_streaming=True,
        caption="✅ Watermark added"
    )

    # 📢 LOG CHANNEL
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

# 🚫 BAN / UNBAN
@app.on_message(filters.command("ban") & filters.user(OWNER_ID))
async def ban_user(_, m):
    ban(int(m.text.split()[1]))
    await m.reply("🚫 User banned")

@app.on_message(filters.command("unban") & filters.user(OWNER_ID))
async def unban_user(_, m):
    unban(int(m.text.split()[1]))
    await m.reply("✅ User unbanned")

app.run()
