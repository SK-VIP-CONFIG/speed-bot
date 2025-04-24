import logging
import struct
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Update
from telegram.ext.callbackcontext import CallbackContext

import os

# Logging
logging.basicConfig(level=logging.INFO)
TOKEN = "7432795021:AAGkrn3xpzOyLcwAR1QnucqHpbZXtzCiqTg"

# Value Mappings
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

# Float to bytes
def float_to_hex_bytes(value):
    return struct.pack('<f', value)

# Modify file
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

# Start Command
def start(update: Update, context: CallbackContext):
    update.message.reply_text("👋 Send me a .uexp or .dat file and I’ll modify it for you!")

# Handle file uploads
def handle_file(update: Update, context: CallbackContext):
    file = update.message.document
    if not file.file_name.endswith(('.uexp', '.dat')):
        update.message.reply_text("❌ Only .uexp or .dat files are supported!")
        return

    file_path = f"./{file.file_name}"
    file.get_file().download(file_path)
    update.message.reply_text(
    "✅ File received! Now send a value name and new float value.\n\nFormat:\n```"
    "Format\n"
    "KNOCK SPEED: -0.64,\n"
    "STAND BACK SPEED: -143.9\n"
    "STAND RIGHT SPEED: -119.9\n"
    "CROUCH SPEED: -135.25\n"
    "BACK CROUCH SPEED: -103.28\n"
    "RIGHT CROUCH SPEED: -86.05\n"
    "PRONE SPEED: -359.5\n"
    "PRONE BACK/RIGHT: -20.0\n"
    "SPRINT SPEED: 160.5\n```📋 Tap & Hold to Copy",
    parse_mode="Markdown"
)

    # Save file path in context for next step
    context.user_data['file_path'] = file_path

# Handle text for replacement
def handle_text(update: Update, context: CallbackContext):
    if 'file_path' not in context.user_data:
        update.message.reply_text("❗ First send a .uexp or .dat file.")
        return

    try:
        text = update.message.text.strip()
        name, val = text.split(':')
        name = name.strip().upper()
        new_val = float(val.strip())

        if name not in value_mappings:
            update.message.reply_text("⚠️ Invalid key name. Allowed keys:\n" + "\n".join(value_mappings.keys()))
            return

        file_path = context.user_data['file_path']
        success = modify_file(file_path, value_mappings[name], new_val)

        if success:
            update.message.reply_document(open(file_path, 'rb'))
            update.message.reply_text("✅ Modified successfully!")
        else:
            update.message.reply_text("❌ Value not found in file.")
    except Exception as e:
        update.message.reply_text(f"⚠️ Error: {e}")

# Main
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
