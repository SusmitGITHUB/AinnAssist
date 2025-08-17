import os
import requests
import re 
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters
)

# === Load environment variables ===
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL")

# === Split long messages to avoid Telegram's 4096-character limit ===
async def send_long_message(update: Update, text: str, max_length=4096):
    if len(text) <= max_length:
        await update.message.reply_text(text)
        return
    parts = []
    current_part = ""
    for line in text.split("\n"):
        if len(current_part) + len(line) + 1 <= max_length:
            current_part += line + "\n"
        else:
            parts.append(current_part.strip())
            current_part = line + "\n"
    if current_part:
        parts.append(current_part.strip())
    for part in parts:
        await update.message.reply_text(part)

# === /start Command ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! Send your legal question as text.")

# === Handle Text Message ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text
    try:
        # Directly send question to API without translation
        res = requests.post(API_URL, json={"question": question})
        res.raise_for_status()
        response_data = res.json()
        answer = response_data.get("answer", "❌ Sorry, couldn't find an answer.")
        confidence = response_data.get("confidence", 5.0)

        await send_long_message(update, f"📜 Answer:\n{answer}\n\n⭐ Confidence: {confidence}/5")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

# === Main function to run the bot ===
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
