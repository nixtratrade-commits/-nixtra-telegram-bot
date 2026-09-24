import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["📊 سیگنال رایگان", "💎 عضویت VIP"],
        ["📚 آموزش", "💬 پشتیبانی"]
    ]

    markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    await update.message.reply_text(
        "به Nixtra خوش اومدی 👋\n\n"
        "اینجا می‌تونی به سیگنال‌ها، آموزش‌ها و بخش VIP دسترسی داشته باشی.\n\n"
        "یکی از گزینه‌های زیر رو انتخاب کن 👇",
        reply_markup=markup
    )

def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN is not set")

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()
