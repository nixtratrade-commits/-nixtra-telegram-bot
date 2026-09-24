import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Nixtra Bot is running!")

    def log_message(self, format, *args):
        return


def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["📊 سیگنال رایگان", "💎 عضویت VIP"],
        ["📚 آموزش", "💬 پشتیبانی"]
    ]

    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "به Nixtra خوش اومدی 👋\n\n"
        "اینجا می‌تونی به سیگنال‌ها، آموزش‌ها و بخش VIP دسترسی داشته باشی.\n\n"
        "یکی از گزینه‌های زیر رو انتخاب کن 👇",
        reply_markup=markup
    )


def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN is not set")

    threading.Thread(target=run_web_server, daemon=True).start()

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()


if __name__ == "__main__":
    main()
