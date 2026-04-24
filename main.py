import os, re, sys, json, pytz, asyncio, requests, subprocess, random
from pyromod import listen
from pyrogram import Client, filters
from pyrogram.errors.exceptions.bad_request_400 import StickerEmojiInvalid
from pyrogram.types.messages_and_media import message
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, InputMediaPhoto
# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
from html_handler import register_html_handlers
from text_handler import register_text_handlers
from unzip_handler import register_unzip_handlers
from vars import API_ID, API_HASH, BOT_TOKEN, CREDIT
# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,

# Initialize the bot
bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,

@bot.on_message(filters.command("start"))
async def start(bot, m: Message):
    user_id = m.chat.id
    user = await bot.get_me()
    caption = (
        f"𝐇𝐞𝐥𝐥𝐨 𝐃𝐞𝐚𝐫 👋!\n\n"
        f"➠ 𝐈 𝐚𝐦 𝐚 𝐓𝐞𝐱𝐭 𝐇𝐭𝐦𝐥 𝐁𝐨𝐭\n\n"
        f"➠ Can Edit Your Text File and Convert in Html!\n\n"
        f"➠ 𝐌𝐚𝐝𝐞 𝐁𝐲 : {CREDIT} 🦁"
    )
    await bot.send_photo(
        chat_id=m.chat.id,
        photo="https://envs.sh/GVI.jpg",
        caption=caption
    )
    
# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,

@bot.on_message(filters.command(["id"]))
async def id_command(client, message: Message):
    chat_id = message.chat.id
    text = f"<blockquote expandable><b>The ID of this chat id is:</b></blockquote>\n`{chat_id}`"
    await message.reply_text(text)

# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,

@bot.on_message(filters.private & filters.command(["info"]))
async def info(bot: Client, update: Message):
    text = (
        f"╭────────────────╮\n"
        f"│✨ **Your Telegram Info**✨ \n"
        f"├────────────────\n"
        f"├🔹**Name :** `{update.from_user.first_name} {update.from_user.last_name if update.from_user.last_name else 'None'}`\n"
        f"├🔹**User ID :** {('@' + update.from_user.username) if update.from_user.username else 'None'}\n"
        f"├🔹**TG ID :** `{update.from_user.id}`\n"
        f"├🔹**Profile :** {update.from_user.mention}\n"
        f"╰────────────────╯"
    )    
    await update.reply_text(        
        text=text,
        disable_web_page_preview=True
    )

# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_message(filters.command(["stop"]))
async def restart_handler(_, m):
    await m.reply_text("𝐁𝐨𝐭 𝐢𝐬 𝐑𝐞𝐬𝐭𝐚𝐫𝐭𝐢𝐧𝐠...", True)
    os.execl(sys.executable, sys.executable, *sys.argv)

#=================================================================

register_text_handlers(bot)
register_html_handlers(bot)
register_unzip_handlers(bot)

#==================================================================

def reset_and_set_commands():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setMyCommands"

    # General users ke liye commands
    general_commands = [
        {"command": "start", "description": "✅ Check Alive the Bot"},
        {"command": "stop", "description": "♻️ Restart Your Bot"},
        {"command": "id", "description": "🆔 Get Your ID"},
        {"command": "info", "description": "ℹ️ Check Your Information"},
        {"command": "t2h", "description": "🌐 .txt → .html Converter"},
        {"command": "t2t", "description": "📟 Text → .txt Generator"},
        {"command": "e2t", "description": "🔠 txt alphabetical rearrange"},
        {"command": "remtitle", "description": "✂️ Parentheses Optimizer"},
        {"command": "unzip", "description": "🗜️ Zip Extractor"},
    ]

    # General users ke liye set commands (scope default)
    requests.post(url, json={
        "commands": general_commands,
        "scope": {"type": "default"},
        "language_code": "en"
    })

if __name__ == "__main__":
    reset_and_set_commands()

bot.run()
