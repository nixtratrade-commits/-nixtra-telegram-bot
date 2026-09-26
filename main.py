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
            ["💳 خرید اشتراک آموزش"],
            ["🔙 بازگشت"],
        ],
        resize_keyboard=True,
    )


def seminars_menu():
    return ReplyKeyboardMarkup(
        [
            ["📍 شهرهای برگزارکننده"],
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
            ["🔙 بازگشت"],
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
            ["🔙 بازگشت"],
        ]

        await update.message.reply_text(
            "📚 دوره‌های آموزشی Nixtra\n\n"
            "سطح موردنظر خود را انتخاب کنید:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True,
            ),
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
async def payment_receipt(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user = update.effective_user

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
                "💳 رسید جدید خرید سیگنال\n\n"
                f"👤 نام: {user.full_name}\n"
                f"🔹 Username: @{user.username if user.username else 'ندارد'}\n"
                f"🆔 Telegram ID: {user.id}"
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "✅ تأیید واریز",
                            callback_data=f"approve_payment:{user.id}",
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
