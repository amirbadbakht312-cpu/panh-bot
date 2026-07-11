# ============================================
# Abyss AI - ربات تلگرام پنگوئن ابیس
# ============================================

import logging
import json
import requests
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ============================================
# تنظیمات اولیه
# ============================================
TOKEN = '8705538996:AAH_8wukB7mR3eoQb_XFZu7IASDDscFLkG4'

# تنظیمات API
SUPABASE_URL = 'https://sqiaabmdxhwlqmphcvrv.supabase.co'
SUPABASE_KEY = 'sb_publishable_UySoruVSw1t6DL5MoHsoKA_LocT4Knz'
MISTRAL_API_KEY = 'BOVuOxjc7VUwRKzcHAn55Jm7FgN38aBs'
MISTRAL_ENDPOINT = 'https://api.mistral.ai/v1/chat/completions'

# تنظیمات توکن
CHAT_COST = 100
CHARITY_RATE = 10000
ENERGY_MAX = 10

# لاگ‌گیری
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================
# دیتابیس محلی با SQLite
# ============================================
import sqlite3
import random

def init_db():
    conn = sqlite3.connect('abyss_bot.db')
    cursor = conn.cursor()
    
    # جدول کاربران
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            tokens INTEGER DEFAULT 100,
            energy INTEGER DEFAULT 10,
            fish INTEGER DEFAULT 0,
            card_number TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # جدول تراکنش‌ها
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_user INTEGER,
            to_user INTEGER,
            amount INTEGER,
            type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # جدول سپرده‌ها
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS deposits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount INTEGER,
            duration INTEGER,
            interest_rate INTEGER,
            start_date TIMESTAMP,
            end_date TIMESTAMP,
            status TEXT DEFAULT 'active'
        )
    ''')
    
    conn.commit()
    conn.close()

# ============================================
# توابع دیتابیس
# ============================================
def get_user(user_id):
    conn = sqlite3.connect('abyss_bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def create_user(user_id, username, first_name):
    conn = sqlite3.connect('abyss_bot.db')
    cursor = conn.cursor()
    
    # تولید شماره کارت
    card_number = ''.join([str(random.randint(0, 9)) for _ in range(16)])
    
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, username, first_name, tokens, energy, fish, card_number)
        VALUES (?, ?, ?, 100, 10, 0, ?)
    ''', (user_id, username, first_name, card_number))
    
    conn.commit()
    conn.close()

def update_user_field(user_id, field, value):
    conn = sqlite3.connect('abyss_bot.db')
    cursor = conn.cursor()
    cursor.execute(f'UPDATE users SET {field} = ? WHERE user_id = ?', (value, user_id))
    conn.commit()
    conn.close()

def add_transaction(from_user, to_user, amount, type):
    conn = sqlite3.connect('abyss_bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO transactions (from_user, to_user, amount, type)
        VALUES (?, ?, ?, ?)
    ''', (from_user, to_user, amount, type))
    conn.commit()
    conn.close()

def add_deposit(user_id, amount, duration, rate):
    conn = sqlite3.connect('abyss_bot.db')
    cursor = conn.cursor()
    start = datetime.now()
    end = start + timedelta(days=duration)
    cursor.execute('''
        INSERT INTO deposits (user_id, amount, duration, interest_rate, start_date, end_date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, amount, duration, rate, start, end))
    conn.commit()
    conn.close()

# ============================================
# صفحه اصلی (منو)
# ============================================
async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or 'کاربر'
    first_name = update.effective_user.first_name or 'عزیز'
    
    # ثبت کاربر
    create_user(user_id, username, first_name)
    user = get_user(user_id)
    
    # ساخت کیبورد
    keyboard = [
        [InlineKeyboardButton("💬 هوش مصنوعی", callback_data="chat")],
        [InlineKeyboardButton("🎣 ماینینگ", callback_data="mine")],
        [InlineKeyboardButton("❤️ خیریه", callback_data="charity")],
        [InlineKeyboardButton("🏦 بانک", callback_data="bank")],
        [InlineKeyboardButton("💸 انتقال توکن", callback_data="transfer")],
        [InlineKeyboardButton("📊 وضعیت من", callback_data="profile")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # متن خوش‌آمدگویی
    text = f"""
🐧 **سلام {first_name} عزیز!**

به **Abyss AI** خوش آمدی!
من **پنگوئن ابیس** هستم، همراهمه تو.

📊 **وضعیت شما:**
🪙 توکن: {user[3]}
⚡ انرژی: {user[4]}
🐟 ماهی: {user[5]}

"تنهایی رو با هم تقسیم می‌کنیم" ❤️
    """
    
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')

# ============================================
# پردازش دکمه‌ها (Callback)
# ============================================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = update.effective_user.id
    user = get_user(user_id)
    
    if data == "profile":
        await show_profile(update, context)
    
    elif data == "chat":
        await show_chat(update, context)
    
    elif data == "mine":
        await show_mine(update, context)
    
    elif data == "charity":
        await show_charity(update, context)
    
    elif data == "bank":
        await show_bank(update, context)
    
    elif data == "transfer":
        await show_transfer(update, context)
    
    elif data.startswith("donate_"):
        amount = int(data.split("_")[1])
        await process_donation(update, context, amount)
    
    elif data.startswith("deposit_"):
        parts = data.split("_")
        days = int(parts[1])
        rate = int(parts[2])
        await process_deposit(update, context, days, rate)
    
    elif data == "back_menu":
        await back_to_menu(update, context)

# ============================================
# نمایش پروفایل
# ============================================
async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    user = get_user(user_id)
    
    text = f"""
🐧 **پروفایل شما:**

👤 نام: {user[2]}
🆔 آیدی: {user[0]}
💳 شماره کارت: `{user[6]}`

📊 **آمار:**
🪙 توکن: {user[3]}
⚡ انرژی: {user[4]}
🐟 ماهی: {user[5]}

📅 تاریخ عضویت: {user[7]}
    """
    
    keyboard = [[InlineKeyboardButton("🔙 برگشت به منو", callback_data="back_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

# ============================================
# چت با هوش مصنوعی
# ============================================
async def show_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    context.user_data['chat_mode'] = True
    
    text = """
💬 **چت با پنگوئن ابیس**

سلام! من پنگوئن ابیس هستم. 
هر پیام **۱۰۰ توکن** مصرف میکنه.

📝 پیامت رو بفرست تا باهات حرف بزنم!

⚠️ برای خروج از چت، دکمه زیر رو بزن.
    """
    
    keyboard = [[InlineKeyboardButton("🔙 خروج از چت", callback_data="back_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup)

# پردازش پیام‌های چت
async def chat_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('chat_mode', False):
        return
    
    user_id = update.effective_user.id
    user = get_user(user_id)
    message = update.message.text
    
    # بررسی توکن
    if user[3] < CHAT_COST:
        await update.message.reply_text("❌ توکن کافی ندارید! (نیاز: ۱۰۰ توکن)")
        return
    
    # کسر توکن
    new_tokens = user[3] - CHAT_COST
    update_user_field(user_id, 'tokens', new_tokens)
    
    # ارسال پیام به Mistral
    await update.message.reply_text("🐧 در حال فکر کردن...")
    
    try:
        response = requests.post(
            MISTRAL_ENDPOINT,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {MISTRAL_API_KEY}'
            },
            json={
                'model': 'mistral-small-latest',
                'messages': [
                    {
                        'role': 'system',
                        'content': '''تو یک پنگوئن به نام "ابیس" هستی. 
                        تو پدر و مادرت رو از دست دادی و خیلی تنهایی.
                        اما همیشه مهربونی و سعی می‌کنی به دیگران کمک کنی.
                        با لهجه بامزه صحبت می‌کنی.
                        پاسخ‌هات کوتاه و صمیمی باشه.'''
                    },
                    {'role': 'user', 'content': message}
                ],
                'temperature': 0.8,
                'max_tokens': 300
            }
        )
        
        if response.status_code == 200:
            reply = response.json()['choices'][0]['message']['content']
            await update.message.reply_text(f"🐧 {reply}")
        else:
            # برگشت توکن در صورت خطا
            update_user_field(user_id, 'tokens', user[3])
            await update.message.reply_text("❌ خطا در ارتباط با هوش مصنوعی. توکن شما برگشت داده شد.")
            
    except Exception as e:
        update_user_field(user_id, 'tokens', user[3])
        await update.message.reply_text(f"❌ خطا: {str(e)}")

# ============================================
# ماینینگ (بازی ماهی‌گیری)
# ============================================
async def show_mine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    user = get_user(user_id)
    
    text = f"""
🎣 **ماهی‌گیری**

🐟 ماهی‌ها رو بگیر و به پنگوئن غذا بده!

📊 وضعیت:
⚡ انرژی: {user[4]}
🐟 ماهی: {user[5]}

🎯 هر بار ماهی‌گیری ۱ انرژی مصرف میکنه
🐧 هر ۱۰ ماهی = ۱ غذا +۵ انرژی
    """
    
    keyboard = [
        [InlineKeyboardButton("🎣 چوب بینداز", callback_data="fish")],
        [InlineKeyboardButton("🐧 غذا دادن به پنگوئن", callback_data="feed")],
        [InlineKeyboardButton("🔙 برگشت", callback_data="back_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup)

async def fish_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    user = get_user(user_id)
    
    # بررسی انرژی
    if user[4] < 1:
        await query.answer("❌ انرژی کافی ندارید!", show_alert=True)
        return
    
    # مصرف انرژی
    new_energy = user[4] - 1
    update_user_field(user_id, 'energy', new_energy)
    
    # شانس گرفتن ماهی (۵۰٪)
    import random
    if random.random() > 0.5:
        # ماهی گرفتی!
        new_fish = user[5] + 1
        update_user_field(user_id, 'fish', new_fish)
        await query.answer("🎉 یه ماهی گرفتی! +۱ 🐟", show_alert=True)
        
        text = f"""
🎉 **ماهی گرفتی!**

🐟 ماهی جدید: {new_fish}
⚡ انرژی باقی‌مونده: {new_energy}

به ماهی‌گیری ادامه بده! 
هر ۱۰ ماهی = ۱ غذا برای پنگوئن
        """
    else:
        # ماهی نرفتی
        await query.answer("😔 ماهی رفت! دوباره امتحان کن", show_alert=True)
        text = f"""
😔 **ماهی رفت!**

⚡ انرژی باقی‌مونده: {new_energy}
🐟 ماهی: {user[5]}

دوباره امتحان کن!
        """
    
    keyboard = [
        [InlineKeyboardButton("🎣 دوباره", callback_data="fish")],
        [InlineKeyboardButton("🔙 برگشت", callback_data="back_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup)

async def feed_penguin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    user = get_user(user_id)
    
    # بررسی ماهی کافی
    if user[5] < 10:
        await query.answer("❌ به ۱۰ ماهی نیاز داری!", show_alert=True)
        return
    
    # بررسی انرژی کامل
    if user[4] >= 10:
        await query.answer("✅ انرژی پنگوئن کامل است!", show_alert=True)
        return
    
    # غذا دادن
    new_fish = user[5] - 10
    new_energy = min(user[4] + 5, 10)
    
    update_user_field(user_id, 'fish', new_fish)
    update_user_field(user_id, 'energy', new_energy)
    
    await query.answer("🐧 پنگوئن خوشحال شد! +۵ انرژی", show_alert=True)
    
    text = f"""
🐧 **پنگوئن غذا خورد!**

⚡ انرژی جدید: {new_energy}
🐟 ماهی باقی‌مونده: {new_fish}

پنگوئن خیلی خوشحال شد! ❤️
    """
    
    keyboard = [
        [InlineKeyboardButton("🎣 ادامه ماهی‌گیری", callback_data="mine")],
        [InlineKeyboardButton("🔙 برگشت", callback_data="back_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup)

# ============================================
# خیریه (Charity)
# ============================================
async def show_charity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    user = get_user(user_id)
    
    text = f"""
❤️ **حمایت از پنگوئن‌ها**

با اهدای توکن‌ها به خیریه‌های پنگوئن کمک کن!

📊 هر ۱۰,۰۰۰ توکن = ۱ دلار کمک

🪙 توکن شما: {user[3]}

🌐 **خیریه‌های معتبر:**
• Penguins Global
• Penguins International  
• Global Penguin Society

💰 برای اهدا، یکی از گزینه‌ها رو انتخاب کن:
    """
    
    keyboard = [
        [InlineKeyboardButton("💰 ۱,۰۰۰ توکن", callback_data="donate_1000")],
        [InlineKeyboardButton("💰 ۵,۰۰۰ توکن", callback_data="donate_5000")],
        [InlineKeyboardButton("💰 ۱۰,۰۰۰ توکن", callback_data="donate_10000")],
        [InlineKeyboardButton("💰 ۵۰,۰۰۰ توکن", callback_data="donate_50000")],
        [InlineKeyboardButton("🌐 مشاهده خیریه‌ها", url="https://www.penguinsg.org/")],
        [InlineKeyboardButton("🔙 برگشت", callback_data="back_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup)

async def process_donation(update: Update, context: ContextTypes.DEFAULT_TYPE, amount: int):
    query = update.callback_query
    user_id = update.effective_user.id
    user = get_user(user_id)
    
    # بررسی توکن کافی
    if user[3] < amount:
        await query.answer(f"❌ توکن کافی ندارید! (نیاز: {amount})", show_alert=True)
        return
    
    # کسر توکن
    new_tokens = user[3] - amount
    update_user_field(user_id, 'tokens', new_tokens)
    
    # محاسبه دلار
    dollars = amount / CHARITY_RATE
    
    # ثبت در دیتابیس
    add_transaction(user_id, 0, amount, 'donation')
    
    await query.answer(f"❤️ {amount} توکن (${dollars:.2f}) اهدا شد!", show_alert=True)
    
    text = f"""
✅ **اهدا با موفقیت انجام شد!**

❤️ مقدار اهدا: {amount} توکن
💵 معادل دلار: ${dollars:.2f}

🪙 توکن باقی‌مونده: {new_tokens}

🌍 **خیریه‌های پنگوئن:**
• [Penguins Global](https://www.penguinsg.org/)
• [Penguins International](https://www.penguinsinternational.org/)
• [Global Penguin Society](https://www.globalpenguinsociety.org/)

از مهربانی تو سپاسگزارم! 🐧❤️
    """
    
    keyboard = [
        [InlineKeyboardButton("❤️ اهدای دوباره", callback_data="charity")],
        [InlineKeyboardButton("🔙 برگشت", callback_data="back_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

# ============================================
# بانک (سپرده‌گذاری)
# ============================================
async def show_bank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    user = get_user(user_id)
    
    text = f"""
🏦 **بانک Abyss**

توکن‌های خودت رو سپرده‌گذاری کن و سود بگیر!

🪙 موجودی: {user[3]} توکن

📊 **طرح‌های سپرده:**
• ۷ روز → ۲٪ سود
• ۴۰ روز → ۵٪ سود  
• ۱ سال → ۲۰٪ سود

💰 برای سپرده‌گذاری، یکی از گزینه‌ها رو انتخاب کن:
    """
    
    keyboard = [
        [InlineKeyboardButton("📊 ۷ روز - ۲٪", callback_data="deposit_7_2")],
        [InlineKeyboardButton("📊 ۴۰ روز - ۵٪", callback_data="deposit_40_5")],
        [InlineKeyboardButton("📊 ۱ سال - ۲۰٪", callback_data="deposit_365_20")],
        [InlineKeyboardButton("🔙 برگشت", callback_data="back_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup)

async def process_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE, days: int, rate: int):
    query = update.callback_query
    user_id = update.effective_user.id
    user = get_user(user_id)
    
    # مقدار پیش‌فرض
    amount = 100
    
    if user[3] < amount:
        await query.answer(f"❌ توکن کافی ندارید! (نیاز: {amount})", show_alert=True)
        return
    
    # کسر توکن
    new_tokens = user[3] - amount
    update_user_field(user_id, 'tokens', new_tokens)
    
    # ثبت سپرده
    add_deposit(user_id, amount, days, rate)
    
    await query.answer(f"✅ {amount} توکن برای {days} روز سپرده شد!", show_alert=True)
    
    text = f"""
✅ **سپرده‌گذاری موفق!**

💰 مبلغ: {amount} توکن
📅 مدت: {days} روز
📊 سود: {rate}%

🪙 توکن باقی‌مونده: {new_tokens}

📌 **محاسبه سود نهایی:**
سود دریافتی: {int(amount * rate / 100)} توکن
مجموع دریافت: {int(amount + (amount * rate / 100))} توکن

پس از پایان مدت، سود به حساب شما واریز میشه! 🐧
    """
    
    keyboard = [
        [InlineKeyboardButton("💰 سپرده جدید", callback_data="bank")],
        [InlineKeyboardButton("🔙 برگشت", callback_data="back_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup)

# ============================================
# انتقال توکن
# ============================================
async def show_transfer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    user = get_user(user_id)
    
    text = f"""
💸 **انتقال توکن**

🪙 موجودی شما: {user[3]} توکن
💳 شماره کارت شما: `{user[6]}`

📝 برای انتقال:
۱. شماره کارت ۱۶ رقمی گیرنده رو وارد کن
۲. مقدار توکن رو مشخص کن

⚠️ توجه: انتقال غیرقابل برگشت است!
    """
    
    keyboard = [
        [InlineKeyboardButton("🔙 برگشت", callback_data="back_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    
    # فعال کردن حالت انتقال
    context.user_data['transfer_mode'] = True
    context.user_data['transfer_user_id'] = user_id

# پردازش انتقال
async def transfer_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('transfer_mode', False):
        return
    
    user_id = update.effective_user.id
    user = get_user(user_id)
    text = update.message.text.strip()
    
    # بررسی فرمت: شماره کارت و مقدار
    parts = text.split()
    if len(parts) != 2:
        await update.message.reply_text("❌ فرمت صحیح: `شماره_کارت مقدار`\nمثال: `1234567890123456 50`", parse_mode='Markdown')
        return
    
    card_number = parts[0]
    amount = int(parts[1])
    
    # بررسی شماره کارت
    if len(card_number) != 16 or not card_number.isdigit():
        await update.message.reply_text("❌ شماره کارت باید ۱۶ رقم باشد!")
        return
    
    # بررسی توکن کافی
    if user[3] < amount:
        await update.message.reply_text(f"❌ توکن کافی ندارید! (نیاز: {amount})")
        return
    
    # پیدا کردن گیرنده
    conn = sqlite3.connect('abyss_bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, username FROM users WHERE card_number = ?', (card_number,))
    recipient = cursor.fetchone()
    conn.close()
    
    if not recipient:
        await update.message.reply_text("❌ شماره کارت نامعتبر است!")
        return
    
    if recipient[0] == user_id:
        await update.message.reply_text("❌ نمی‌توانید به خودتان انتقال دهید!")
        return
    
    # انجام انتقال
    new_tokens_sender = user[3] - amount
    update_user_field(user_id, 'tokens', new_tokens_sender)
    
    # به‌روزرسانی گیرنده
    recipient_user = get_user(recipient[0])
    new_tokens_recipient = recipient_user[3] + amount
    update_user_field(recipient[0], 'tokens', new_tokens_recipient)
    
    # ثبت تراکنش
    add_transaction(user_id, recipient[0], amount, 'transfer')
    
    await update.message.reply_text(f"""
✅ **انتقال موفق!**

💰 {amount} توکن به {recipient[1]} منتقل شد!

🪙 موجودی جدید شما: {new_tokens_sender}

📊 وضعیت:
• فرستنده: {user[2]} → {new_tokens_sender} توکن
• گیرنده: {recipient[1]} → {new_tokens_recipient} توکن
    """)
    
    # خروج از حالت انتقال
    context.user_data['transfer_mode'] = False
    
    # برگشت به منو
    keyboard = [[InlineKeyboardButton("🔙 برگشت به منو", callback_data="back_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("برای برگشت کلیک کن:", reply_markup=reply_markup)

# ============================================
# برگشت به منو
# ============================================
async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    user = get_user(user_id)
    
    # خروج از حالت‌ها
    context.user_data['chat_mode'] = False
    context.user_data['transfer_mode'] = False
    
    # منوی اصلی
    keyboard = [
        [InlineKeyboardButton("💬 هوش مصنوعی", callback_data="chat")],
        [InlineKeyboardButton("🎣 ماینینگ", callback_data="mine")],
        [InlineKeyboardButton("❤️ خیریه", callback_data="charity")],
        [InlineKeyboardButton("🏦 بانک", callback_data="bank")],
        [InlineKeyboardButton("💸 انتقال توکن", callback_data="transfer")],
        [InlineKeyboardButton("📊 وضعیت من", callback_data="profile")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = f"""
🐧 **به منوی اصلی خوش آمدی!**

📊 وضعیت شما:
🪙 توکن: {user[3]}
⚡ انرژی: {user[4]}  
🐟 ماهی: {user[5]}

چی کار می‌خوای بکنی؟ 😊
    """
    
    await query.edit_message_text(text, reply_markup=reply_markup)

# ============================================
# شروع مجدد (Restart)
# ============================================
async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    
    if user:
        await main_menu(update, context)
    else:
        await start(update, context)

# ============================================
# دستور start
# ============================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await main_menu(update, context)

# ============================================
# راه‌اندازی ربات
# ============================================
def main():
    # راه‌اندازی دیتابیس
    init_db()
    
    # ایجاد اپلیکیشن
    application = Application.builder().token(TOKEN).build()
    
    # دستورات
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", start))
    application.add_handler(CommandHandler("restart", restart))
    
    # دکمه‌ها
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # پیام‌ها
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_message))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, transfer_message))
    
    # راه‌اندازی
    print("🐧 ربات Abyss AI روشن شد!")
    print("🤖 @AbyssAIBot")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
