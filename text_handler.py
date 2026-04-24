import os, requests, subprocess, asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

#==============================================================================================================================
async def text_to_txt(bot: Client, message: Message):
    user_id = str(message.from_user.id)
    editable = await message.reply_text(f"<blockquote><b>Welcome to the Text to .txt Converter!\nSend the **text** for convert into a `.txt` file.</b></blockquote>")
    input_message: Message = await bot.listen(message.chat.id)
    if not input_message.text:
        await message.reply_text("**Send valid text data**")
        return
    text_data = input_message.text.strip()
    await input_message.delete()  # Corrected here
    await editable.edit("**🔄 Send file name or send /d**")
    try:
        input: Message = await bot.listen(editable.chat.id, timeout=20)
        raw_text = input.text
        await input.delete(True)
    except asyncio.TimeoutError:
        raw_text = '/d'
     
    await editable.delete()
    if raw_text == '/d':
        custom_file_name = 'txt_file'
    else:
        custom_file_name = raw_text

    txt_file = os.path.join("downloads", f'{custom_file_name}.txt')
    os.makedirs(os.path.dirname(txt_file), exist_ok=True)  # Ensure the directory exists
    with open(txt_file, 'w') as f:
        f.write(text_data)
        
    await message.reply_document(document=txt_file, caption=f"`{custom_file_name}.txt`\n<blockquote><b>You can now download your content! 📥</b></blockquote>")
    os.remove(txt_file)

#===================================================================================================================================
UPLOAD_FOLDER = '/path/to/upload/folder'

async def handle_txt(bot: Client, message: Message):
    editable = await message.reply_text(f"<blockquote>Welcome to the .txt File Editor!\nSend your `.txt` file containing subjects, links, and topics.</blockquote>")
    input_message: Message = await bot.listen(editable.chat.id)
    if not input_message.document:
        await message.reply_text("**Invalid Input File**")
        return
    file_name = input_message.document.file_name
    uploaded_file_path = os.path.join(UPLOAD_FOLDER, file_name)
    uploaded_file = await input_message.download(uploaded_file_path)
    await input_message.delete(True)
    await editable.delete(True)
    try:
        with open(uploaded_file, 'r', encoding='utf-8') as f:
            content = f.readlines()
    except Exception as e:
        await message.reply_text(f"**Failed Reason:**\n<blockquote>{e}</blockquote>")
        return
    subjects = {}
    current_subject = None
    for line in content:
        line = line.strip()
        if line and ":" in line:
            title, url = line.split(":", 1)
            title, url = title.strip(), url.strip()
            if title in subjects:
                subjects[title]["links"].append(url)
            else:
                subjects[title] = {"links": [url], "topics": []}
            current_subject = title
        elif line.startswith("-") and current_subject:
            subjects[current_subject]["topics"].append(line.strip("- ").strip())
    sorted_subjects = sorted(subjects.items())
    for title, data in sorted_subjects:
        data["topics"].sort()
    try:
        final_file_path = os.path.join(UPLOAD_FOLDER, file_name)
        with open(final_file_path, 'w', encoding='utf-8') as f:
            for title, data in sorted_subjects:
                for link in data["links"]:
                    f.write(f"{title}:{link}\n")
                for topic in data["topics"]:
                    f.write(f"- {topic}\n")
    except Exception as e:
        await message.reply_text(f"**Failed Reason:**\n<blockquote>{e}</blockquote>")
        return
    try:
        await bot.send_document(
            chat_id=message.chat.id,
            document=final_file_path,
            caption="<blockquote><b>Your edited .txt file with subjects, links, and topics sorted alphabetically!</b></blockquote>"
        )
    except Exception as e:
        await message.reply_text(f"**Failed Reason:**\n<blockquote>{e}</blockquote>")
    finally:
        if os.path.exists(uploaded_file_path):
            os.remove(uploaded_file_path)  

#===================================================================================================================================
async def handle_title(bot: Client, message: Message):
    editable = await message.reply_text(f"<blockquote>⚙️ Welcome Parentheses Optimizer\n📂 Send your `.txt` input file with titles and hyperlinks</blockquote>")
    input: Message = await bot.listen(editable.chat.id)
    txt_file = await input.download()
    await input.delete(True)
    await editable.delete()
      
    with open(txt_file, 'r') as f:
        lines = f.readlines()
    
    cleaned_lines = [line.replace('(', ' ').replace(')', ' ').replace('_', ' ').replace('  ', ' ').lstrip() for line in lines]
    cleaned_txt_file = os.path.splitext(txt_file)[0] + '_cleaned.txt'
    with open(cleaned_txt_file, 'w') as f:
        f.write(''.join(cleaned_lines))
      
    await bot.send_document(chat_id=message.chat.id, document=cleaned_txt_file,caption="<blockquote><b>Here is your cleaned txt file.</b></blockquote>")
    os.remove(cleaned_txt_file)

#========================================================================================================================
def register_text_handlers(bot):
    @bot.on_message(filters.command(["t2t"]))
    async def call_text_to_txt(bot: Client, m: Message):
        await text_to_txt(bot, m)

    @bot.on_message(filters.command(["e2t"]))
    async def call_handle_txt(bot: Client, m: Message):
        await handle_txt(bot, m)

    @bot.on_message(filters.command(["remtitle"]))
    async def call_handle_title(bot: Client, message: Message):
        await handle_title(bot, message)
