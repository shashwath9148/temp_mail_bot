import logging
import random
import string
import requests
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# 🔐 Your Bot Token (from environment or fallback for local testing)
TOKEN = "8287974267:AAGKrOdr5zmMostvnA7XWXXR5r5G3Zp82ug"

# 📋 Logging Config
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# 🎲 Random email generator
def generate_email():
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    domain = random.choice(["1secmail.com", "1secmail.net", "1secmail.org"])
    return f"{username}@{domain}"

# 📬 Check inbox
def check_inbox(email):
    try:
        username, domain = email.split('@')
        url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={username}&domain={domain}"
        return requests.get(url, timeout=5).json()
    except:
        return []

# 📩 Read a specific message
def read_message(email, message_id):
    try:
        username, domain = email.split('@')
        url = f"https://www.1secmail.com/api/v1/?action=readMessage&login={username}&domain={domain}&id={message_id}"
        return requests.get(url, timeout=5).json()
    except:
        return None

# 🚀 /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📧 Welcome to Temp Mail Bot!\n\n"
        "Commands:\n"
        "/getmail - Get a new temporary email\n"
        "/inbox - Check your inbox\n"
        "/read <id> - Read a specific message"
    )

# 📧 /getmail command
async def get_mail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = generate_email()
    context.user_data["email"] = email
    await update.message.reply_text(f"✅ Your temporary email:\n`{email}`", parse_mode="Markdown")

# 📬 /inbox command
async def inbox(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "email" not in context.user_data:
        await update.message.reply_text("❗ First, get a temp email using /getmail")
        return

    email = context.user_data["email"]
    messages = check_inbox(email)

    if not messages:
        await update.message.reply_text("📭 Inbox is empty. Wait for messages...")
        return

    reply = f"📩 Inbox for `{email}`:\n\n"
    for msg in messages:
        reply += f"From: `{msg['from']}`\nSubject: `{msg['subject']}`\nID: `{msg['id']}`\n\n"
    await update.message.reply_text(reply, parse_mode="Markdown")

# 📥 /read command
async def read(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "email" not in context.user_data:
        await update.message.reply_text("❗ First, get a temp email using /getmail")
        return

    if not context.args:
        await update.message.reply_text("❗ Usage: /read <message_id>")
        return

    email = context.user_data["email"]
    message_id = context.args[0]
    msg = read_message(email, message_id)

    if not msg:
        await update.message.reply_text("⚠️ Could not retrieve message. Try again later.")
        return

    reply = (
        f"📨 From: `{msg['from']}`\n"
        f"📌 Subject: `{msg['subject']}`\n"
        f"📅 Date: `{msg['date']}`\n"
        f"💬 Body:\n{msg['textBody']}"
    )
    await update.message.reply_text(reply, parse_mode="Markdown")

# 🧠 Run Bot
if __name__ == "__main__":
    if not TOKEN:
        raise ValueError("❌ BOT_TOKEN is missing. Set it in .env or environment variables.")
    
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("getmail", get_mail))
    app.add_handler(CommandHandler("inbox", inbox))
    app.add_handler(CommandHandler("read", read))

    print("✅ Temp Mail Bot is running...")
    app.run_polling()