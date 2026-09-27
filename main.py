import os
import sqlite3
from datetime import datetime, timedelta, timezone
DB_FILE = "subscriptions.db"
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)


TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = os.environ.get("ADMIN_ID")
PAYMENT_WALLET = os.environ.get("PAYMENT_WALLET")
FREE_SIGNAL_CHANNEL = os.environ.get("FREE_SIGNAL_CHANNEL")
FREE_CHANNEL_ID = os.environ.get("FREE_CHANNEL_ID")
VIP_CHANNEL_ID = os.environ.get("VIP_CHANNEL_ID")
pending_purchases = {}
DB_FILE = "subscriptions.db"
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS subscriptions (
            user_id INTEGER PRIMARY KEY,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS course_purchases (
            user_id INTEGER NOT NULL,
            course_level TEXT NOT NULL,
            purchase_date TEXT NOT NULL,
            PRIMARY KEY (user_id, course_level)
        )
        """
    )
    conn.commit()
    conn.close()
def has_course_access(user_id, course_level):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT 1 FROM course_purchases
        WHERE user_id = ? AND course_level = ?
        """,
        (user_id, course_level),
    )

    result = cursor.fetchone()
    conn.close()

    return result is not None
def grant_course_access(user_id, course_level):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO course_purchases
        (user_id, course_level, purchase_date)
        VALUES (?, ?, ?)
        """,
        (
            user_id,
            course_level,
            datetime.now(timezone.utc).isoformat(),
        ),
    )

    conn.commit()
    conn.close()
async def open_course_lesson(update, course_level, video_file_id=None):
    user_id = update.effective_user.id

    if not has_course_access(user_id, course_level):
        await update.message.reply_text(
            "🔒 شما به این دوره دسترسی ندارید.\n\n"
            "برای مشاهده ویدیوهای این دوره ابتدا باید دوره را تهیه کنید."
        )
        return

    if video_file_id:
        await update.message.reply_video(
            video=video_file_id
        )
    else:
        await update.message.reply_text(
            "🎬 ویدیوی این درس به‌زودی در این قسمت قرار می‌گیرد."
        )
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
    return ReplyKeyboardMarkup(
        [
            ["📊 سیگنال‌ها", "🎓 آموزش‌ها"],
            ["🎤 سمینارها", "🤖 پنل تخصصی AI"],
            ["💬 پشتیبانی"],
        ],
        resize_keyboard=True,
    )


def signals_menu():
    return ReplyKeyboardMarkup(
        [
            ["🎁 تست رایگان سیگنال"],
            ["💳 خرید سیگنال"],
            ["🔎 استعلام وضعیت اشتراک"],
            ["🔙 بازگشت"],
        ],
        resize_keyboard=True,
    )


def education_menu():
    return ReplyKeyboardMarkup(
        [
            ["📚 عناوین دوره‌ها"],
            ["💳 خرید اشتراک دوره ها"],
            ["🔙 بازگشت"],
        ],
        resize_keyboard=True,
    )


def seminars_menu():
    return ReplyKeyboardMarkup(
        [
            ["📚 عناوین سمینارها"],
            ["🎟 خرید سمینار"],
            ["🔎 استعلام ظرفیت"],
            ["🔙 بازگشت"],
        ],
        resize_keyboard=True,
    )


def ai_menu():
    return ReplyKeyboardMarkup(
        [
            ["🧠 مشاهده منوهای پنل"],
            ["💳 خرید پنل تخصصی AI"],
            ["🔙 بازگشت"],
        ],
        resize_keyboard=True,
    )


# ---------- Start ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "به Nixtra خوش اومدی 👋\n\n"
        "خدمت موردنظرت رو از منوی زیر انتخاب کن 👇",
        reply_markup=main_menu(),
    )


# ---------- Messages ----------

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if context.user_data.get("seminar_step") == "first_name":
        context.user_data["seminar_first_name"] = text
        context.user_data["seminar_step"] = "last_name"

        await update.message.reply_text(
            "👤 لطفاً نام خانوادگی خود را وارد کنید:"
        )
        return
            if context.user_data.get("seminar_step") == "last_name":
        context.user_data["seminar_last_name"] = text
        context.user_data["seminar_step"] = "phone"

        await update.message.reply_text(
            "📱 لطفاً شماره تماس خود را وارد کنید:"
        )
        return
            if context.user_data.get("seminar_step") == "phone":
        context.user_data["seminar_phone"] = text
        context.user_data["seminar_step"] = "email"

        await update.message.reply_text(
            "📧 لطفاً آدرس ایمیل خود را وارد کنید:"
        )
        return
            if context.user_data.get("seminar_step") == "email":
        context.user_data["seminar_email"] = text
        context.user_data["seminar_step"] = "confirm_info"

        keyboard = [
            ["✅ تأیید مشخصات و ادامه پرداخت"],
            ["🔙 بازگشت"],
        ]

        await update.message.reply_text(
            "📋 مشخصات ثبت‌نام شما:\n\n"
            f"👤 نام: {context.user_data['seminar_first_name']}\n"
            f"👤 نام خانوادگی: {context.user_data['seminar_last_name']}\n"
            f"📱 شماره تماس: {context.user_data['seminar_phone']}\n"
            f"📧 ایمیل: {context.user_data['seminar_email']}\n\n"
            "🎟 سمینار آگاهی مالی\n"
            "📍 شیراز\n"
            "📅 مهر ۱۴۰۵\n"
            "💰 مبلغ: 5 USDT\n\n"
            "در صورت صحیح بودن اطلاعات، تأیید کنید.",
            reply_markup=ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True,
            ),
        )
        return
    if text == "📊 سیگنال‌ها":
        await update.message.reply_text(
            "📊 بخش سیگنال‌ها\n\nیکی از گزینه‌های زیر رو انتخاب کن:",
            reply_markup=signals_menu(),
        )

    elif text == "🎓 آموزش‌ها":
        await update.message.reply_text(
            "🎓 بخش آموزش‌ها\n\nیکی از گزینه‌های زیر رو انتخاب کن:",
            reply_markup=education_menu(),
        )

    elif text == "🎤 سمینارها":
        await update.message.reply_text(
            "🎤 بخش سمینارها\n\nیکی از گزینه‌های زیر رو انتخاب کن:",
            reply_markup=seminars_menu(),
        )

    elif text == "🤖 پنل تخصصی AI":
        await update.message.reply_text(
            "🤖 پنل تخصصی AI\n\nیکی از گزینه‌های زیر رو انتخاب کن:",
            reply_markup=ai_menu(),
        )

    elif text == "💬 پشتیبانی":
        await update.message.reply_text(
            "💬 بخش پشتیبانی\n\n"
            "در این قسمت می‌تونی با پشتیبانی Nixtra در ارتباط باشی."
        )

    elif text == "🎁 تست رایگان سیگنال":
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "📢 عضویت در کانال",
                        url=FREE_SIGNAL_CHANNEL,
                    )
                ],
                [
                    InlineKeyboardButton(
                        "✅ عضو شدم",
                        callback_data="check_free_channel",
                    )
                ],
            ]
        )

        await update.message.reply_text(
            "🎁 سیگنال رایگان Nixtra\n\n"
            "برای مشاهده سیگنال‌های رایگان، وارد کانال شو 👇",
            reply_markup=keyboard,
        )

    elif text == "💳 خرید سیگنال":
        await update.message.reply_text(
            "📊 اشتراک سیگنال Nixtra\n\n"
            "🔹 روزانه ۱ سیگنال\n"
            "🔹 مدت اشتراک: ۳۰ روز\n"
            "🔹 قیمت: ۱۰ دلار\n\n"
            "برای تهیه اشتراک، گزینه «🛒 ثبت درخواست خرید» رو انتخاب کن.",
            reply_markup=ReplyKeyboardMarkup(
                [
                    ["🛒 ثبت درخواست خرید"],
                    ["🔙 بازگشت"],
                ],
                resize_keyboard=True,
            ),
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
                ),
            )

    elif text == "🔎 استعلام وضعیت اشتراک":
        user_id = update.effective_user.id

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT start_date, end_date FROM subscriptions WHERE user_id = ?",
            (user_id,),
        )

        subscription = cursor.fetchone()
        conn.close()

        if not subscription:
            await update.message.reply_text(
                "❌ اشتراک فعالی برای شما ثبت نشده است."
            )
        else:
            start_date = datetime.fromisoformat(subscription[0])
            end_date = datetime.fromisoformat(subscription[1])
            now = datetime.now(timezone.utc)

            if now >= end_date:
                await update.message.reply_text(
                    "❌ اشتراک شما به پایان رسیده است."
                )
            else:
                total_days = (now - start_date).days + 1
                remaining_days = max(0, (end_date - now).days)

                await update.message.reply_text(
                    "✅ اشتراک VIP شما فعال است.\n\n"
                    f"📅 روز {total_days} از اشتراک\n"
                    f"⏳ {remaining_days} روز باقی مانده"
                )

    elif text == "📚 عناوین دوره‌ها":
        keyboard = [
            ["🟢 سطح مقدماتی"],
            ["🟡 سطح متوسط"],
            ["🔴 سطح حرفه‌ای"],
            ["🔙 بازگشت به آموزش‌ها"],
        ]

        await update.message.reply_text(
            "📚 دوره‌های آموزشی Nixtra\n\n"
            "سطح موردنظر خود را انتخاب کنید:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True,
            ),
        )
    elif text == "🟢 سطح مقدماتی":
        keyboard = [
            ["1️⃣ آشنایی با بازارهای مالی"],
            ["2️⃣ انواع بازارهای مالی"],
            ["3️⃣ بروکر و صرافی چیست؟"],
            ["4️⃣ آشنایی با TradingView"],
            ["5️⃣ نمودار و کندل چیست؟"],
            ["6️⃣ تایم‌فریم چیست؟"],
            ["7️⃣ پوزیشن و انواع سفارش"],
            ["8️⃣ Long و Short"],
            ["9️⃣ Spot و Futures"],
            ["🔟 اهرم و مارجین"],
            ["1️⃣1️⃣ حد سود و حد ضرر"],
            ["1️⃣2️⃣ اولین معامله آزمایشی"],
            ["🔙 بازگشت به دوره‌ها"],
        ]

        await update.message.reply_text(
            "🟢 دوره مقدماتی Nixtra\n\n"
            "یکی از درس‌ها را انتخاب کنید:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True,
            ),
        )
    elif text in [
        "1️⃣ آشنایی با بازارهای مالی",
        "2️⃣ انواع بازارهای مالی",
        "3️⃣ بروکر و صرافی چیست؟",
        "4️⃣ آشنایی با TradingView",
        "5️⃣ نمودار و کندل چیست؟",
        "6️⃣ تایم‌فریم چیست؟",
        "7️⃣ پوزیشن و انواع سفارش",
        "8️⃣ Long و Short",
        "9️⃣ Spot و Futures",
        "🔟 اهرم و مارجین",
        "1️⃣1️⃣ حد سود و حد ضرر",
        "1️⃣2️⃣ اولین معامله آزمایشی",
    ]:
        await open_course_lesson(
            update,
            "beginner",
        )
    elif text == "🟡 سطح متوسط":
        keyboard = [
            ["1️⃣ ساختار بازار و روند"],
            ["2️⃣ حمایت و مقاومت"],
            ["3️⃣ کندل‌خوانی"],
            ["4️⃣ تحلیل تکنیکال"],
            ["5️⃣ پرایس اکشن"],
            ["6️⃣ اندیکاتورها"],
            ["7️⃣ فیبوناچی"],
            ["8️⃣ نقاط ورود و خروج"],
            ["9️⃣ ریسک به ریوارد"],
            ["🔟 مدیریت سرمایه"],
            ["1️⃣1️⃣ حجم معامله"],
            ["1️⃣2️⃣ اخبار و تقویم اقتصادی"],
            ["1️⃣3️⃣ ژورنال معاملاتی"],
            ["🔙 بازگشت به دوره‌ها"],
        ]

        await update.message.reply_text(
            "🟡 دوره متوسط Nixtra\n\n"
            "یکی از درس‌ها را انتخاب کنید:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True,
            ),
        )
    elif text in [
        "1️⃣ ساختار بازار و روند",
        "2️⃣ حمایت و مقاومت",
        "3️⃣ کندل‌خوانی",
        "4️⃣ تحلیل تکنیکال",
        "5️⃣ پرایس اکشن",
        "6️⃣ اندیکاتورها",
        "7️⃣ فیبوناچی",
        "8️⃣ نقاط ورود و خروج",
        "9️⃣ ریسک به ریوارد",
        "🔟 مدیریت سرمایه",
        "1️⃣1️⃣ حجم معامله",
        "1️⃣2️⃣ اخبار و تقویم اقتصادی",
        "1️⃣3️⃣ ژورنال معاملاتی",
    ]:
        await open_course_lesson(
            update,
            "intermediate",
        )
    elif text == "🔴 سطح حرفه‌ای":
        keyboard = [
            ["1️⃣ پرایس اکشن پیشرفته"],
            ["2️⃣ نقدینگی (Liquidity)"],
            ["3️⃣ شکست و Fake Breakout"],
            ["4️⃣ سناریونویسی بازار"],
            ["5️⃣ طراحی Setup معاملاتی"],
            ["6️⃣ بک‌تست (Backtest)"],
            ["7️⃣ Win Rate و Expectancy"],
            ["8️⃣ Drawdown"],
            ["9️⃣ مدیریت معامله باز"],
            ["🔟 روان‌شناسی معامله‌گری"],
            ["1️⃣1️⃣ ساخت Trading Plan"],
            ["1️⃣2️⃣ طراحی استراتژی شخصی"],
            ["🔙 بازگشت به دوره‌ها"],
        ]

        await update.message.reply_text(
            "🔴 دوره حرفه‌ای Nixtra\n\n"
            "یکی از درس‌ها را انتخاب کنید:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True,
            ),
        )
    elif text in [
        "1️⃣ ساختار بازار و روند",
        "2️⃣ حمایت و مقاومت",
        "3️⃣ کندل‌خوانی",
        "4️⃣ تحلیل تکنیکال",
        "5️⃣ پرایس اکشن",
        "6️⃣ اندیکاتورها",
        "7️⃣ فیبوناچی",
        "8️⃣ نقاط ورود و خروج",
        "9️⃣ ریسک به ریوارد",
        "🔟 مدیریت سرمایه",
        "1️⃣1️⃣ حجم معامله",
        "1️⃣2️⃣ اخبار و تقویم اقتصادی",
        "1️⃣3️⃣ ژورنال معاملاتی",
    ]:
        await open_course_lesson(
            update,
            "intermediate",
        )
    elif text == "🔙 بازگشت به دوره‌ها":
        keyboard = [
            ["🟢 سطح مقدماتی"],
            ["🟡 سطح متوسط"],
            ["🔴 سطح حرفه‌ای"],
            ["🔙 بازگشت به آموزش‌ها"],
        ]

        await update.message.reply_text(
            "📚 دوره‌های آموزشی Nixtra\n\n"
            "سطح موردنظر خود را انتخاب کنید:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True,
            ),
        )
    elif text == "💳 خرید اشتراک دوره ها":
        keyboard = [
            ["🟢 خرید دوره مقدماتی"],
            ["🟡 خرید دوره متوسط"],
            ["🔴 خرید دوره حرفه‌ای"],
            ["💎 خرید کامل سه سطح"],
            ["🔙 بازگشت"],
        ]

        await update.message.reply_text(
            "🎓 خرید دوره‌های آموزشی\n\n"
            "دوره موردنظر خود را انتخاب کنید:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True,
            ),
        )
        
    elif text == "🟢 خرید دوره مقدماتی":
        keyboard = [
        
            ["✅ تأیید و ادامه خرید مقدماتی"],
            ["🔙 بازگشت"],
        ]
        await update.message.reply_text(
            "🟢 دوره مقدماتی بازارهای مالی\n\n"
            "📚 این دوره شامل آموزش مفاهیم پایه بازارهای مالی، "
            "کندل، تایم‌فریم، پوزیشن، Long و Short، Spot و Futures، "
            "اهرم، حد سود و حد ضرر و اولین معامله آزمایشی است.\n\n"
            "💰 قیمت: 20 USDT\n"
            "♾ دسترسی: دائمی\n\n"
            "در صورت تأیید، گزینه «تأیید و ادامه خرید» را بزنید.",
            reply_markup=ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True,
            ),
        )
    elif text == "🔙 بازگشت به خرید دوره‌ها":
        keyboard = [
            ["🟢 خرید دوره مقدماتی"],
            ["🟡 خرید دوره متوسط"],
            ["🔴 خرید دوره حرفه‌ای"],
            ["💎 خرید کامل سه سطح"],
            ["🔙 بازگشت"],
        ]

        await update.message.reply_text(
            "🎓 خرید دوره‌های آموزشی\n\n"
            "دوره موردنظر خود را انتخاب کنید:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True,
            ),
        )
    

    elif text == "✅ تأیید و ادامه خرید مقدماتی":
        user_id = update.effective_user.id
        pending_purchases[user_id] = "beginner"
        keyboard = [
["🔙 بازگشت به خرید دوره‌ها"],
          ]
        payment_message = await update.message.reply_text(
            "💳 پرداخت دوره مقدماتی\n\n"
            "💰 مبلغ: 20 USDT\n"
            "🌐 شبکه: BEP20 (BNB Smart Chain)\n\n"
            "📌 آدرس کیف پول:\n"
            f"{PAYMENT_WALLET}\n\n"
                        "پس از واریز، تصویر رسید پرداخت را همین‌جا برای ربات ارسال کنید.",
            reply_markup=ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True,
            ),
        )
        context.user_data["course_payment_message_id"] = payment_message.message_id
    elif text == "🔙 بازگشت به خرید دوره‌ها":
        message_id = context.user_data.pop("course_payment_message_id", None)

        if message_id:
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=message_id,
                )
            except Exception:
                pass
        keyboard = [
            ["🟢 خرید دوره مقدماتی"],
            ["🟡 خرید دوره متوسط"],
            ["🔴 خرید دوره حرفه‌ای"],
            ["💎 خرید کامل سه سطح"],
            ["🔙 بازگشت"],
        ]

        await update.message.reply_text(
            "🎓 خرید دوره‌های آموزشی\n\n"
            "دوره موردنظر خود را انتخاب کنید:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True,
            ),
        )
    elif text == "🟡 خرید دوره متوسط":
        keyboard = [
            ["✅ تأیید و ادامه خرید متوسط"],
            ["🔙 بازگشت"],
        ]

        await update.message.reply_text(
            "🟡 دوره متوسط بازارهای مالی\n\n"
            "📚 شامل آموزش ساختار بازار، حمایت و مقاومت، کندل‌خوانی، "
            "تحلیل تکنیکال، پرایس اکشن، اندیکاتورها، فیبوناچی، "
            "نقاط ورود و خروج، ریسک به ریوارد، مدیریت سرمایه، "
            "حجم معامله، اخبار و تقویم اقتصادی و ژورنال معاملاتی است.\n\n"
            "💰 قیمت: 30 USDT\n"
            "♾ دسترسی: دائمی\n\n"
            "در صورت تأیید، گزینه «تأیید و ادامه خرید متوسط» را بزنید.",
            reply_markup=ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True,
            ),
        )
    elif text == "✅ تأیید و ادامه خرید متوسط":
        user_id = update.effective_user.id

        if not has_course_access(user_id, "beginner"):
            await update.message.reply_text(
                "🔒 شما هنوز دوره مقدماتی را تهیه نکرده‌اید."
            )
        else:
            pending_purchases[user_id] = "intermediate"

            await update.message.reply_text(
                "💳 پرداخت دوره متوسط\n\n"
                "💰 مبلغ: 30 USDT\n"
                "🌐 شبکه: BEP20 (BNB Smart Chain)\n\n"
                "📌 آدرس کیف پول:\n"
                f"{PAYMENT_WALLET}\n\n"
                "پس از واریز، تصویر رسید پرداخت را همین‌جا برای ربات ارسال کنید."
            )

    elif text == "🔴 خرید دوره حرفه‌ای":
        user_id = update.effective_user.id

        if not has_course_access(user_id, "intermediate"):
            await update.message.reply_text(
                "🔒 شما هنوز دوره متوسط را تهیه نکرده‌اید.\n\n"
                "برای خرید دوره حرفه‌ای، ابتدا باید دوره متوسط را تهیه کنید."
            )
        else:
            keyboard = [
                ["✅ تأیید و ادامه خرید حرفه‌ای"],
                ["🔙 بازگشت"],
            ]

            await update.message.reply_text(
                "🔴 دوره حرفه‌ای بازارهای مالی\n\n"
                "💰 قیمت: 50 USDT\n"
                "♾ دسترسی: دائمی\n\n"
                "در صورت تأیید، گزینه «تأیید و ادامه خرید» را بزنید.",
                reply_markup=ReplyKeyboardMarkup(
                    keyboard,
                    resize_keyboard=True,
                ),
            )

    elif text == "✅ تأیید و ادامه خرید حرفه‌ای":
        user_id = update.effective_user.id

        if not has_course_access(user_id, "intermediate"):
            await update.message.reply_text(
                "🔒 شما هنوز دوره متوسط را تهیه نکرده‌اید."
            )
        else:
            pending_purchases[user_id] = "professional"

            await update.message.reply_text(
                "💳 پرداخت دوره حرفه‌ای\n\n"
                "💰 مبلغ: 50 USDT\n"
                "🌐 شبکه: BEP20 (BNB Smart Chain)\n\n"
                "📌 آدرس کیف پول:\n"
                f"{PAYMENT_WALLET}\n\n"
                "پس از واریز، تصویر رسید پرداخت را همین‌جا برای ربات ارسال کنید."
            )

    elif text == "💎 خرید کامل سه سطح":
        keyboard = [
            ["✅ تأیید و ادامه خرید پکیج کامل"],
            ["🔙 بازگشت"],
        ]

        await update.message.reply_text(
            "💎 پکیج کامل آموزش بازارهای مالی\n\n"
            "🟢 دوره مقدماتی\n"
            "🟡 دوره متوسط\n"
            "🔴 دوره حرفه‌ای\n\n"
            "💰 قیمت کل: 100 USDT\n"
            "♾ دسترسی به هر سه دوره: دائمی\n\n"
            "با خرید این پکیج، هر سه سطح به‌صورت همزمان برای شما فعال می‌شود.\n\n"
            "در صورت تأیید، گزینه «تأیید و ادامه خرید» را بزنید.",
            reply_markup=ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True,
            ),
        )

    elif text == "✅ تأیید و ادامه خرید پکیج کامل":
        user_id = update.effective_user.id
        pending_purchases[user_id] = "all_courses"

        await update.message.reply_text(
            "💳 پرداخت پکیج کامل آموزش\n\n"
            "💰 مبلغ: 100 USDT\n"
            "🌐 شبکه: BEP20 (BNB Smart Chain)\n\n"
            "📌 آدرس کیف پول:\n"
            f"{PAYMENT_WALLET}\n\n"
            "پس از واریز، تصویر رسید پرداخت را همین‌جا برای ربات ارسال کنید."
        )
    elif text == "📚 عناوین سمینارها":
        await update.message.reply_text(
            "💰 سمینار آگاهی مالی\n\n"
            "در این سمینار درباره مفاهیم مهم آگاهی مالی، "
            "نگرش درست نسبت به پول، مدیریت بهتر منابع مالی "
            "و تصمیم‌گیری آگاهانه‌تر در مسائل مالی صحبت می‌کنیم."
        )
    elif text == "🎟 خرید سمینار":
        keyboard = [
            ["💰 سمینار آگاهی مالی"],
            ["🔙 بازگشت"],
        ]

        await update.message.reply_text(
            "🎟 خرید تیکت سمینار\n\n"
            "سمینار موردنظر خود را انتخاب کنید:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True,
            ),
        )
    elif text == "💰 سمینار آگاهی مالی":
        keyboard = [
            ["📍 شیراز", "📍 تهران"],
            ["📍 اصفهان", "📍 کرمان"],
            ["📍 مشهد", "📍 تبریز"],
            ["🔙 بازگشت"],
        ]

        await update.message.reply_text(
            "📍 شهر محل برگزاری سمینار آگاهی مالی را انتخاب کنید:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True,
            ),
        )
    elif text == "📍 شیراز":
        keyboard = [
            ["✅ تأیید خرید تیکت شیراز"],
            ["🔙 بازگشت"],
        ]

        await update.message.reply_text(
            "🎟 سمینار آگاهی مالی\n\n"
            "📍 شهر: شیراز\n"
            "📅 زمان برگزاری: مهر ۱۴۰۵\n"
            "💰 مبلغ تیکت: 5 USDT\n\n"
            "برای ادامه ثبت‌نام، گزینه تأیید خرید را بزنید.",
            reply_markup=ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True,
            ),
        )
    elif text == "✅ تأیید خرید تیکت شیراز":
        context.user_data["seminar_city"] = "شیراز"
        context.user_data["seminar_step"] = "first_name"

        await update.message.reply_text(
            "📝 برای ثبت‌نام، مشخصات شما را مرحله‌به‌مرحله دریافت می‌کنیم.\n\n"
            "👤 لطفاً نام خود را وارد کنید:"
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
    elif text == "🔙 بازگشت به آموزش‌ها":
        await update.message.reply_text(
            "🎓 بخش آموزش‌ها\n\nیکی از گزینه‌های زیر رو انتخاب کن:",
            reply_markup=education_menu(),
        )
    elif text == "🔙 بازگشت":
        await update.message.reply_text(
            "🏠 منوی اصلی",
            reply_markup=main_menu(),
        )

    else:
        await update.message.reply_text(
            "لطفاً یکی از گزینه‌های منو رو انتخاب کن 👇",
            reply_markup=main_menu(),
        )

async def channel_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"VIP_CHANNEL_ID={update.effective_chat.id}")
# ---------- Free Channel Check ----------

async def check_free_channel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    try:
        member = await context.bot.get_chat_member(
            chat_id=int(FREE_CHANNEL_ID),
            user_id=user_id,
        )

        if member.status in ["member", "administrator", "creator"]:
            await query.message.reply_text(
                "✅ عضویت شما تأیید شد.\n\n"
                "به کانال سیگنال رایگان Nixtra خوش اومدی 🎉"
            )
        else:
            await query.answer(
                "❌ هنوز عضو کانال نشدی. اول عضو شو و دوباره امتحان کن.",
                show_alert=True,
            )

    except Exception:
        await query.answer(
            "⚠️ امکان بررسی عضویت وجود نداشت. دوباره امتحان کن.",
            show_alert=True,
        )


# ---------- VIP Payment Approval ----------

async def approve_payment(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query
    await query.answer()

    user_id = int(query.data.split(":")[1])
    activate_subscription(user_id)
    try:
        invite = await context.bot.create_chat_invite_link(
            chat_id=int(VIP_CHANNEL_ID),
            member_limit=1,
        )

        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "✅ پرداخت شما تأیید شد.\n\n"
                "🎟 برای ورود به کانال VIP از لینک زیر استفاده کنید:\n"
                f"{invite.invite_link}\n\n"
                "⏳ مدت اشتراک شما ۳۰ روز است."
            ),
        )

        await query.edit_message_reply_markup(reply_markup=None)

        await query.message.reply_text(
            "✅ پرداخت تأیید شد و لینک VIP برای خریدار ارسال شد."
        )

    except Exception as error:
        print(f"VIP_APPROVAL_ERROR: {error}")

        await query.message.reply_text(
f"⚠️ خطای VIP:\n{error}"
        )


# ---------- Payment Receipt ----------
def activate_subscription(user_id):
    start_date = datetime.now(timezone.utc)
    end_date = start_date + timedelta(days=30)

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR REPLACE INTO subscriptions
        (user_id, start_date, end_date)
        VALUES (?, ?, ?)
        """,
        (
            user_id,
            start_date.isoformat(),
            end_date.isoformat(),
        ),
    )

    conn.commit()
    conn.close()
async def approve_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    parts = query.data.split(":")
    user_id = int(parts[1])
    purchase_type = parts[2]

    if purchase_type == "beginner":
        grant_course_access(user_id, "beginner")

    elif purchase_type == "intermediate":
        grant_course_access(user_id, "intermediate")

    elif purchase_type == "professional":
        grant_course_access(user_id, "professional")

    elif purchase_type == "all_courses":
        grant_course_access(user_id, "beginner")
        grant_course_access(user_id, "intermediate")
        grant_course_access(user_id, "professional")

    elif purchase_type == "signal":
        await approve_payment(update, context)
        return

    pending_purchases.pop(user_id, None)

    await context.bot.send_message(
        chat_id=user_id,
        text=(
            "✅ پرداخت شما تأیید شد.\n\n"
            "🎓 دسترسی آموزشی شما با موفقیت فعال شد."
        ),
    )

    await query.edit_message_reply_markup(reply_markup=None)

    await query.message.reply_text(
        "✅ پرداخت تأیید شد و دسترسی آموزشی خریدار فعال شد."
    )
async def payment_receipt(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user = update.effective_user
    purchase_type = pending_purchases.get(user.id, "signal")
    await update.message.reply_text(
        "✅ رسید پرداخت شما دریافت شد.\n\n"
        "⏳ لطفاً منتظر بمانید تا وضعیت واریز شما بررسی و تأیید شود."
    )

    if ADMIN_ID:
        await context.bot.forward_message(
            chat_id=int(ADMIN_ID),
            from_chat_id=update.effective_chat.id,
            message_id=update.message.message_id,
        )

        await context.bot.send_message(
            chat_id=int(ADMIN_ID),
            text=(
                f"💳 رسید جدید\n\n"
                f"🛒 نوع خرید: {purchase_type}\n\n"
                f"👤 نام: {user.full_name}\n"
                f"🔹 Username: @{user.username if user.username else 'ندارد'}\n"
                f"🆔 Telegram ID: {user.id}"
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "✅ تأیید واریز",
callback_data=f"approve_purchase:{user.id}:{purchase_type}",
                        )
                    ]
                ]
            ),
        )

async def check_expired_subscriptions(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now(timezone.utc)

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT user_id FROM subscriptions WHERE end_date <= ?",
        (now.isoformat(),),
    )

    expired_users = cursor.fetchall()

    for (user_id,) in expired_users:
        try:
            await context.bot.ban_chat_member(
                chat_id=int(VIP_CHANNEL_ID),
                user_id=user_id,
            )

            await context.bot.unban_chat_member(
                chat_id=int(VIP_CHANNEL_ID),
                user_id=user_id,
                only_if_banned=True,
            )

            cursor.execute(
                "DELETE FROM subscriptions WHERE user_id = ?",
                (user_id,),
            )

        except Exception as error:
            print(f"EXPIRATION_ERROR {user_id}: {error}")

    conn.commit()
    conn.close()
# ---------- Run ----------

def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN is not set")

    threading.Thread(
        target=run_web_server,
        daemon=True,
    ).start()
    init_db()
    app = Application.builder().token(TOKEN).build()
    app.job_queue.run_repeating(
        check_expired_subscriptions,
        interval=3600,
        first=10,
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ChatType.CHANNEL, channel_id))
    app.add_handler(
        CallbackQueryHandler(
            check_free_channel,
            pattern="^check_free_channel$",
        )
    )
    app.add_handler(
    CallbackQueryHandler(
        approve_purchase,
        pattern="^approve_purchase:",
    )
        )
    app.add_handler(
    CallbackQueryHandler(
        approve_purchase,
        pattern="^approve_purchase:",
    )
)
    app.add_handler(
        CallbackQueryHandler(
            approve_payment,
            pattern="^approve_payment:",
        )
    )

    app.add_handler(
        MessageHandler(
            filters.PHOTO,
            payment_receipt,
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message,
        )
    )

    app.run_polling()


if __name__ == "__main__":
    main()
