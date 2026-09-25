import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters


TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = os.environ.get("ADMIN_ID")
PAYMENT_WALLET = os.environ.get("PAYMENT_WALLET")
FREE_SIGNAL_CHANNEL = os.environ.get("FREE_SIGNAL_CHANNEL")
FREE_CHANNEL_ID = os.environ.get("FREE_CHANNEL_ID")
# ---------- Render Health Server ----------

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


# ---------- Keyboards ----------

def main_menu():
    return ReplyKeyboardMarkup([
        ["📊 سیگنال‌ها", "🎓 آموزش‌ها"],
        ["🎤 سمینارها", "🤖 پنل تخصصی AI"],
        ["💬 پشتیبانی"]
    ], resize_keyboard=True)


def signals_menu():
    return ReplyKeyboardMarkup([
        ["🎁 تست رایگان سیگنال"],
        ["💳 خرید سیگنال"],
        ["🔎 استعلام وضعیت اشتراک"],
        ["🔙 بازگشت"]
    ], resize_keyboard=True)


def education_menu():
    return ReplyKeyboardMarkup([
        ["📚 عناوین دوره‌ها"],
        ["💳 خرید اشتراک آموزش"],
        ["🔙 بازگشت"]
    ], resize_keyboard=True)


def seminars_menu():
    return ReplyKeyboardMarkup([
        ["📍 شهرهای برگزارکننده"],
        ["🎟 خرید سمینار"],
        ["🔎 استعلام ظرفیت"],
        ["🔙 بازگشت"]
    ], resize_keyboard=True)


def ai_menu():
    return ReplyKeyboardMarkup([
        ["🧠 مشاهده منوهای پنل"],
        ["💳 خرید پنل تخصصی AI"],
        ["🔙 بازگشت"]
    ], resize_keyboard=True)


# ---------- Start ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "به Nixtra خوش اومدی 👋\n\n"
        "خدمت موردنظرت رو از منوی زیر انتخاب کن 👇",
        reply_markup=main_menu()
    )


# ---------- Messages ----------

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    if text == "📊 سیگنال‌ها":
        await update.message.reply_text(
            "📊 بخش سیگنال‌ها\n\nیکی از گزینه‌های زیر رو انتخاب کن:",
            reply_markup=signals_menu()
        )

    elif text == "🎓 آموزش‌ها":
        await update.message.reply_text(
            "🎓 بخش آموزش‌ها\n\nیکی از گزینه‌های زیر رو انتخاب کن:",
            reply_markup=education_menu()
        )

    elif text == "🎤 سمینارها":
        await update.message.reply_text(
            "🎤 بخش سمینارها\n\nیکی از گزینه‌های زیر رو انتخاب کن:",
            reply_markup=seminars_menu()
        )

    elif text == "🤖 پنل تخصصی AI":
        await update.message.reply_text(
            "🤖 پنل تخصصی AI\n\nیکی از گزینه‌های زیر رو انتخاب کن:",
            reply_markup=ai_menu()
        )

    elif text == "💬 پشتیبانی":
        await update.message.reply_text(
            "💬 بخش پشتیبانی\n\n"
            "در این قسمت می‌تونی با پشتیبانی Nixtra در ارتباط باشی."
        )
    elif text == "🎁 تست رایگان سیگنال":
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "📢 عضویت در کانال",
                    url=FREE_SIGNAL_CHANNEL
                )
            ],
            [
                InlineKeyboardButton(
                    "✅ عضو شدم",
                    callback_data="check_free_channel"
                )
            ]
        ])

        await update.message.reply_text(
            "🎁 سیگنال رایگان Nixtra\n\n"
            "برای مشاهده سیگنال‌های رایگان، وارد کانال شو 👇",
            reply_markup=keyboard
        )
    elif text == "💳 خرید سیگنال":
        await update.message.reply_text(
            "📊 اشتراک سیگنال Nixtra\n\n"
            "🔹 روزانه ۱ سیگنال\n"
            "🔹 مدت اشتراک: ۳۰ روز\n"
            "🔹 قیمت: ۱۰ دلار\n\n"
            "برای تهیه اشتراک، گزینه «🛒 ثبت درخواست خرید» رو انتخاب کن.",
            reply_markup=ReplyKeyboardMarkup([
                ["🛒 ثبت درخواست خرید"],
                ["🔙 بازگشت"]
            ], resize_keyboard=True)
        
        )
    elif text == "🛒 ثبت درخواست خرید":
        user = update.effective_user

        await update.message.reply_text(
    "💳 پرداخت اشتراک سیگنال Nixtra\n\n"
    "💵 مبلغ: 10 USDT\n"
    "🌐 شبکه: BEP20 (BNB Smart Chain)\n\n"
    f"👛 آدرس کیف پول:\n{PAYMENT_WALLET}\n\n"
    "⚠️ لطفاً فقط USDT روی شبکه BEP20 ارسال کنید.\n\n"
    "بعد از پرداخت، رسید پرداخت را ارسال کنید."
        )

        if ADMIN_ID:
            await context.bot.send_message(
                chat_id=int(ADMIN_ID),
                text=(
                    "💰 درخواست جدید خرید سیگنال\n\n"
                    f"👤 نام: {user.full_name}\n"
                    f"📱 یوزرنیم: @{user.username if user.username else 'ندارد'}\n"
                    f"🆔 Telegram ID: {user.id}\n\n"
                    "📊 پلن: روزانه ۱ سیگنال\n"
                    "📅 مدت: ۳۰ روز\n"
                    "💵 مبلغ: ۱۰ دلار"
                )
            )
    elif text == "🔎 استعلام وضعیت اشتراک":
        await update.message.reply_text(
            "🔎 استعلام وضعیت اشتراک\n\n"
            "سیستم استعلام اشتراک در مرحله بعد فعال می‌شه."
        )

    elif text == "📚 عناوین دوره‌ها":
        await update.message.reply_text(
            "📚 دوره‌های آموزشی Nixtra\n\n"
            "لیست دوره‌ها در این قسمت نمایش داده خواهد شد."
        )

    elif text == "💳 خرید اشتراک آموزش":
        await update.message.reply_text(
            "💳 خرید آموزش\n\n"
            "اطلاعات خرید دوره‌ها در این قسمت قرار می‌گیره."
        )

    elif text == "📍 شهرهای برگزارکننده":
        await update.message.reply_text(
            "📍 شهرهای برگزارکننده سمینار\n\n"
            "اطلاعات شهرها و برنامه سمینارها در این قسمت نمایش داده می‌شه."
        )

    elif text == "🎟 خرید سمینار":
        await update.message.reply_text(
            "🎟 ثبت‌نام سمینار\n\n"
            "سمینار موردنظر خودت رو می‌تونی از این قسمت انتخاب کنی."
        )

    elif text == "🔎 استعلام ظرفیت":
        await update.message.reply_text(
            "🔎 استعلام ظرفیت سمینار\n\n"
            "ظرفیت سمینارهای فعال در این قسمت نمایش داده می‌شه."
        )

    elif text == "🧠 مشاهده منوهای پنل":
        await update.message.reply_text(
            "🧠 امکانات پنل تخصصی AI\n\n"
            "امکانات پنل در این قسمت معرفی خواهد شد."
        )

    elif text == "💳 خرید پنل تخصصی AI":
        await update.message.reply_text(
            "💳 خرید پنل تخصصی AI\n\n"
            "پلن‌ها و شرایط خرید در این قسمت نمایش داده می‌شه."
        )

    elif text == "🔙 بازگشت":
        await update.message.reply_text(
            "🏠 منوی اصلی",
            reply_markup=main_menu()
        )

    else:
        await update.message.reply_text(
            "لطفاً یکی از گزینه‌های منو رو انتخاب کن 👇",
            reply_markup=main_menu()
        )
async def channel_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"CHANNEL_ID={update.effective_chat.id}")
async def check_free_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    try:
        member = await context.bot.get_chat_member(
            chat_id=int(FREE_CHANNEL_ID),
            user_id=user_id
        )

        if member.status in ["member", "administrator", "creator"]:
            await query.message.reply_text(
                "✅ عضویت شما تأیید شد.\n\n"
                "به کانال سیگنال رایگان Nixtra خوش اومدی 🎉"
            )
        else:
            await query.answer(
                "❌ هنوز عضو کانال نشدی. اول عضو شو و دوباره امتحان کن.",
                show_alert=True
            )

    except Exception:
        await query.answer(
            "⚠️ امکان بررسی عضویت وجود نداشت. دوباره امتحان کن.",
            show_alert=True
        )
        async def payment_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    await update.message.reply_text(
        "✅ رسید پرداخت شما دریافت شد.\n\n"
        "⏳ لطفاً منتظر بمانید تا وضعیت واریز شما بررسی و تأیید شود."
    )

    if ADMIN_ID:
        await context.bot.forward_message(
            chat_id=int(ADMIN_ID),
            from_chat_id=update.effective_chat.id,
            message_id=update.message.message_id
        )

        await context.bot.send_message(
            chat_id=int(ADMIN_ID),
            text=(
                "💳 رسید جدید خرید سیگنال\n\n"
                f"👤 نام: {user.full_name}\n"
                f"🔹 Username: @{user.username if user.username else 'ندارد'}\n"
                f"🆔 Telegram ID: {user.id}"
            )
        )
# ---------- Run ----------

def main():

    if not TOKEN:
        raise RuntimeError("BOT_TOKEN is not set")

    threading.Thread(
        target=run_web_server,
        daemon=True
    ).start()

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_free_channel, pattern="^check_free_channel$"))
    app.add_handler(MessageHandler(filters.ChatType.CHANNEL, channel_id))
    app.add_handler(
        MessageHandler(filters.PHOTO, payment_receipt)
    )
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    app.run_polling()


if __name__ == "__main__":
    main()
