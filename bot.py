from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import *
from users_db import get_user
from bans_db import is_banned, ban, unban
from watermark import watermark_video
import os

app = Client("wm_bot", API_ID, API_HASH, BOT_TOKEN)

buttons = InlineKeyboardMarkup([
    [InlineKeyboardButton("✏️ Rename", callback_data="rename"),
     InlineKeyboardButton("🔁 Default", callback_data="default")],
    [InlineKeyboardButton("🖼 Thumbnail", callback_data="thumb"),
     InlineKeyboardButton("📏 Scale", callback_data="scale")],
    [InlineKeyboardButton("📍 Position", callback_data="position")],
    [InlineKeyboardButton("▶️ Start Watermark", callback_data="process")]
])

@app.on_message(filters.private)
async def ban_check(_, m):
    if is_banned(m.from_user.id):
        await m.stop_propagation()

@app.on_message(filters.private & (filters.video | filters.document))
async def handle_video(_, m):
    media = m.video or m.document
    if m.document and not (media.mime_type or "").startswith("video/"):
        return await m.reply("❌ Only video files supported")

    if media.file_size > MAX_FILE_SIZE:
        return await m.reply("❌ Max file size is 2GB")

    u = get_user(m.from_user.id)
    u["last"] = m
    await m.reply("👇 Options choose karo", reply_markup=buttons)

@app.on_callback_query(filters.regex("^rename$"))
async def rename(_, cq):
    u = get_user(cq.from_user.id)
    u["awaiting"] = "rename"
    await cq.message.reply("✏️ New file name bhejo (without .mp4)")
    await cq.answer()

@app.on_callback_query(filters.regex("^default$"))
async def default(_, cq):
    get_user(cq.from_user.id)["rename"] = None
    await cq.message.reply("🔁 Default filename set")
    await cq.answer()

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

@app.on_message(filters.text & filters.private)
async def text_input(_, m):
    u = get_user(m.from_user.id)
    if u.get("awaiting") == "rename":
        u["rename"] = m.text.strip()
        u["awaiting"] = None
        await m.reply("✅ Rename saved")

@app.on_callback_query(filters.regex("^position$"))
async def position(_, cq):
    u = get_user(cq.from_user.id)
    u["position"] = DEFAULT_POSITION
    await cq.message.reply("📍 Position set (bottom-center)")
    await cq.answer()

@app.on_callback_query(filters.regex("^scale$"))
async def scale(_, cq):
    u = get_user(cq.from_user.id)
    u["scale"] = DEFAULT_SCALE
    await cq.message.reply("📏 Scale set (20%)")
    await cq.answer()

@app.on_callback_query(filters.regex("^process$"))
async def process(_, cq):
    u = get_user(cq.from_user.id)
    m = u.get("last")
    if not m:
        return

    status = await cq.message.reply("⏳ Watermarking...")
    inp = await m.download()
    out = (u["rename"] or "watermarked") + ".mp4"

    watermark_video(inp, out, DEFAULT_TEXT, "logo.png", u["scale"], u["position"])

    await cq.message.reply_video(
        out,
        thumb=u["thumb"],
        supports_streaming=True,
        caption="✅ Watermark added"
    )

    await status.delete()
    os.remove(inp)
    os.remove(out)

@app.on_message(filters.command("ban") & filters.user(OWNER_ID))
async def ban_user(_, m):
    ban(int(m.text.split()[1]))
    await m.reply("🚫 User banned")

@app.on_message(filters.command("unban") & filters.user(OWNER_ID))
async def unban_user(_, m):
    unban(int(m.text.split()[1]))
    await m.reply("✅ User unbanned")

app.run()