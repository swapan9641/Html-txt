import os, zipfile, tempfile, shutil, asyncio
from pyrogram import Client, filters
from pyrogram.types.messages_and_media import message
from pyrogram.types import Message
from pyrogram.errors.exceptions.bad_request_400 import StickerEmojiInvalid

async def unzip_handler(client: Client, message: Message):
    reply = message.reply_to_message
    if not reply or not reply.document:
        return await message.reply_text("**Reply to a .zip file with `/unzip` or `/unzip password`**")
        
    file_name = reply.document.file_name or "archive.zip"
    if not file_name.lower().endswith(".zip"):
        return await message.reply_text("**Reply `/unzip` or `/unzip password` only .zip file**")       

    # optional password
    parts = message.text.split(maxsplit=1)
    password = parts[1].strip() if len(parts) > 1 else None
    pwd_bytes = password.encode() if password else None

    file_name = file_name.replace('_', ' ').replace('.zip', '').replace('.Zip', '')
    await message.reply_text(f"<blockquote><b>🗜️ Archive : {file_name}</b></blockquote>")
    status = await message.reply_text("📥 **Downloading archive...**")
    temp_dir = tempfile.mkdtemp(prefix="unzip_")
    zip_path = os.path.join(temp_dir, file_name)

    try:
        await client.download_media(reply.document.file_id, zip_path)
    except Exception as e:
        await status.edit(f"__**Failed Reason in Download:**__\n<blockquote><b>{e}</b></blockquote>")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return

    await status.edit("🗜️ **Extracting archive...**")
    extract_dir = os.path.join(temp_dir, "extracted")
    os.makedirs(extract_dir, exist_ok=True)

    try:
        with zipfile.ZipFile(zip_path) as zf:
            first_file = zf.infolist()[0]
            try:
                with zf.open(first_file, pwd=None) as f:
                    f.read(1)    # try reading a byte
                needs_password = False
            except RuntimeError:
                needs_password = True

            if needs_password and not password:
                await status.edit("🔒 **This archive is password-protected.**\n**🖊️ Reply to the ZIP with:** `/unzip password`")
                shutil.rmtree(temp_dir, ignore_errors=True)
                return

            pwd_bytes = password.encode("utf-8") if password else None 
            try:
                zf.extractall(path=extract_dir, pwd=pwd_bytes)
            except RuntimeError as e:
                await status.edit(f"__**Failed Reason in Extraction:**__\n<blockquote><b>01. May be Password Wrong\n02. {e}</b></blockquote>")
                shutil.rmtree(temp_dir, ignore_errors=True)
                return
    except zipfile.BadZipFile:
        await status.edit(f"__**Failed Reason:**__\n<blockquote><b>Corrupted .zip file</b></blockquote>")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return
    except Exception as e:
        await status.edit(f"__**Failed Reason in Extraction:**__\n<blockquote><b>{e}</b></blockquote>")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return

    # Build top-level listing
    entries = sorted(os.listdir(extract_dir))
    if not entries:
        await status.edit(f"__**Failed Reason:**__\n<blockquote><b>Empty .zip file</b></blockquote>")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return

    list_lines = ["<blockquote><b>🔎 फ़ाइल/फ़ोल्डर सूची:</b></blockquote>"]
    for e in entries:
        e_path = os.path.join(extract_dir, e)
        if os.path.isdir(e_path):
            list_lines.append(f"📁 **{e}**")
        else:
            list_lines.append(f"📄 **{e}**")
    await status.edit("\n".join(list_lines))

    # Send top-level files (not in any folder)
    root_files = [e for e in entries if os.path.isfile(os.path.join(extract_dir, e))]
    if root_files:
        await message.reply_text("📄 **Root files:**")
        for fname in root_files:
            fpath = os.path.join(extract_dir, fname)
            try:
                await message.reply_document(fpath, caption=f"📄 **{fname}**\n<blockquote><b>🗜️ Archive : {file_name}</b></blockquote>")
            except Exception as e:
                await message.reply_text(f"__**Failed Reason in Send File: {fname}**__\n<blockquote><>b{e}</b></blockquote>")
            await asyncio.sleep(4)

    # For each top-level folder, send folder name and its files (recursively)
    top_dirs = [e for e in entries if os.path.isdir(os.path.join(extract_dir, e))]
    for d in top_dirs:
        folder_path = os.path.join(extract_dir, d)
        await message.reply_text(f"<blockquote><b>📁 Folder: {d}</b></blockquote>")
        # walk the folder recursively and send files with relative paths
        for root, _, files in os.walk(folder_path):
            # compute relative path inside the folder
            rel_root = os.path.relpath(root, folder_path)
            for fname in files:
                abs_path = os.path.join(root, fname)
                rel_path_display = fname if rel_root == "." else os.path.join(rel_root, fname)
                caption = f"📄 **{rel_path_display}**\n<blockquote><b>🗜️ Archive: {file_name}\n📁 Folder: {d}</b></blockquote>\n"
                try:
                    await message.reply_document(abs_path, caption=caption)
                except Exception as e:
                    await message.reply_text(f"__**Failed Reason in Send File: {caption}**__\n<blockquote><>b{e}</b></blockquote>")
                await asyncio.sleep(4)

    shutil.rmtree(temp_dir, ignore_errors=True)
    await message.reply_text(f"**⋅ ─ UPLOADING ✩ COMPLETED ─ ⋅**")

#==============================================================================================================
def register_unzip_handlers(bot):
    @bot.on_message(filters.command(["unzip"]))
    async def call_unzip_handler(client: Client, message: Message):
        await unzip_handler(client, message)
