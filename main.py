import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# 📌 Load bot token from environment variables
TOKEN = os.getenv("8287974267:AAGKrOdr5zmMostvnA7XWXXR5r5G3Zp82ug")

# 📝 Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# 🌐 Temp Mail API (Example: mail.tm API)
BASE_URL = "https://api.mail.tm"

# 🔹 Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📧 Welcome to Temp Mail Bot!\n"
        "Use /getmail to get a temporary email address."
    )

# 🔹 Get temp mail
async def getmail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Request a new account from mail.tm
        domain_res = requests.get(f"{BASE_URL}/domains").json()
        domain = domain_res["hydra:member"][0]["domain"]
        email = f"user{os.urandom(4).hex()}@{domain}"
        password = os.urandom(6).hex()

        account_data = {"address": email, "password": password}
        requests.post(f"{BASE_URL}/accounts", json=account_data)

        await update.message.reply_text(
            f"✅ Your temporary email:\n📧 {email}\n\n"
            f"⚠️ Save your password if you want to check inbox:\n🔑 {password}"
        )
    except Exception as e:
        await update.message.reply_text("⚠️ Error getting temp mail. Please try again later.")

# Bot setup
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("getmail", getmail))

    print("🚀 Bot is running...")
    app.run_polling()       
