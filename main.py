import logging
import struct
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Update
from telegram.ext.callbackcontext import CallbackContext

import os

# Logging
logging.basicConfig(level=logging.INFO)
TOKEN = "7432795021:AAGMOoMf9GtHwmk8DHTS03ydH1MEAKeqx1k"  # 🔁 यहाँ अपना Telegram Bot Token डालो

# Value Mappings (original values for replacing)
value_mappings = {
    "KNOCK SPEED": -0.64,
    "STAND BACK SPEED": -143.9,
    "STAND RIGHT SPEED": -119.9,
    "CROUCH SPEED": -135.25,
    "BACK CROUCH SPEED": -103.28,
    "RIGHT CROUCH SPEED": -86.05,
    "PRONE SPEED": -359.5,
    "PRONE BACK/RIGHT": -20.0,
    "SPRINT SPEED": 160.5
}

# Float to hex bytes
def float_to_hex_bytes(value):
    return struct.pack('<f', value)

# Modify float value in file
def modify_file(file_path, search_value, new_value):
    with open(file_path, 'rb') as f:
        data = f.read()
    search = float_to_hex_bytes(search_value)
    replace = float_to_hex_bytes(new_value)

    if search in data:
        data = data.replace(search, replace, 1)
        with open(file_path, 'wb') as f:
            f.write(data)
        return True
    return False

# /start command
def start(update: Update, context: CallbackContext):
    update.message.reply_text("👋 𝐒𝐞𝐧𝐝 𝐌𝐞 𝐚 .𝐮𝐞𝐱𝐩 𝐨𝐫 .𝐝𝐚𝐭 𝐅𝐢𝐥𝐞 𝐀𝐧𝐝 𝐈’𝐥𝐥 𝐌𝐨𝐝𝐢𝐟𝐲 𝐈𝐭 𝐅𝐨𝐫 𝐘𝐨𝐮 !")

# File upload handler
def handle_file(update: Update, context: CallbackContext):
    file = update.message.document
    if not file.file_name.endswith(('.uexp', '.dat')):
        update.message.reply_text("❌ Only .uexp or .dat files are supported!")
        return

    file_path = f"./{file.file_name}"
    file.get_file().download(file_path)
    context.user_data['file_path'] = file_path

    update.message.reply_text(
        "✅ 𝐅𝐢𝐥𝐞 𝐑𝐞𝐜𝐞𝐢𝐯𝐞𝐝 ! 𝐍𝐨𝐰 𝐒𝐞𝐧𝐝 𝐍𝐞𝐰 𝐕𝐚𝐥𝐮𝐞𝐬 𝐈𝐧 𝐓𝐡𝐢𝐬 𝐅𝐨𝐫𝐦𝐚𝐭:\n\n"
        "📑 𝐂𝐨𝐩𝐲 𝐓𝐡𝐞 𝐅𝐨𝐫𝐦𝐚𝐭 𝐆𝐢𝐯𝐞𝐧 𝐁𝐞𝐥𝐨𝐰, 𝐄𝐝𝐢𝐭 𝐈𝐭𝐬 𝐕𝐚𝐥𝐮𝐞𝐬 𝐀𝐧𝐝 𝐒𝐞𝐧𝐝 𝐈𝐭.\n"
        "```Format:\n"
        "KNOCK SPEED: -0.64\n"
        "STAND BACK SPEED: -143.9\n"
        "STAND RIGHT SPEED: -119.9\n"
        "CROUCH SPEED: -135.25\n"
        "BACK CROUCH SPEED: -103.28\n"
        "RIGHT CROUCH SPEED: -86.05\n"
        "PRONE SPEED: -359.5\n"
        "PRONE BACK/RIGHT: -20.0\n"
        "SPRINT SPEED: 160.5\n```",
        parse_mode="Markdown"
    )

# Text message handler (multi-line value edit)
def handle_text(update: Update, context: CallbackContext):
    if 'file_path' not in context.user_data:
        update.message.reply_text("❗ 𝐅𝐢𝐫𝐬𝐭 𝐒𝐞𝐧𝐝 𝐚 .𝐮𝐞𝐱𝐩 𝐎𝐫 .𝐝𝐚𝐭 𝐅𝐢𝐥𝐞.")
        return

    try:
        text = update.message.text.strip()
        lines = text.split('\n')
        file_path = context.user_data['file_path']

        results = []
        for line in lines:
            if ':' not in line:
                continue
            name, val = line.split(':', 1)
            name = name.strip().upper()
            try:
                new_val = float(val.strip())
            except ValueError:
                results.append(f"❌ {name}: Invalid number.")
                continue

            if name not in value_mappings:
                results.append(f"❌ {name}: Not a valid key.")
                continue

            old_val = value_mappings[name]
            success = modify_file(file_path, old_val, new_val)

            if success:
                results.append(f"✅ {name}: Modified.")
            else:
                results.append(f"⚠️ {name}: Value not found.")

        update.message.reply_text('\n'.join(results))
        update.message.reply_document(open(file_path, 'rb'))
    except Exception as e:
        update.message.reply_text(f"⚠️ Error: {e}")

# Main function
def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.document, handle_file))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()


