import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import random
import os
import time

# توکن رو از متغیر محیطی می‌خونه (برای Railway لازمه)
TOKEN = os.environ.get('TELEGRAM_TOKEN', 'توکن_خودت_رو_اینجا_بذار')
bot = telebot.TeleBot(TOKEN)

# --- دیتابیس ساده برای ذخیره سکه‌ها (روی فایل) ---
# برای اینکه کد ساده بمونه، از یه دیکشنری استفاده می‌کنیم. 
# برای ذخیره دائمی، باید از sqlite استفاده کنی که بعداً می‌گم.
user_coins = {}

def get_coins(user_id):
    return user_coins.get(user_id, 10000) # شروع با ۱۰,۰۰۰ سکه

def set_coins(user_id, amount):
    user_coins[user_id] = amount

# --- تابع ساخت دکمه رنگی ---
def make_btn(text, callback_data, style=None):
    try:
        return InlineKeyboardButton(text, callback_data=callback_data, style=style)
    except TypeError:
        # اگه کتابخانه از style پشتیبانی نکرد، دکمه ساده می‌سازه
        return InlineKeyboardButton(text, callback_data=callback_data)

# --- منوی اصلی ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup()
    markup.row(make_btn("🔴 رولت", "roulette_info", "danger"), make_btn("⚫️ تاس", "dice_info", "primary"))
    markup.row(make_btn("🟢 حدس عدد", "guess_info", "success"), make_btn("🔵 گاوصندوق", "safe_info", "primary"))
    markup.row(make_btn("🟡 مینیاب", "mine_info", "danger"), make_btn("⚽️ پنالتی", "penalty_info", "success"))
    markup.row(make_btn("✊ سنگ کاغذ قیچی", "rps_info", "primary"))
    
    text = "🎰 **کازینوی سلطان**\n\n💰 موجودی شما: **{}** سکه\n\nیک بازی انتخاب کنید:".format(get_coins(message.from_user.id))
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode='Markdown')

# --- هندلر دکمه‌ها ---
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    user_id = call.from_user.id
    coins = get_coins(user_id)
    
    if call.data == "roulette_info":
        bot.answer_callback_query(call.id, "برای بازی بنویس: roulette 1000", show_alert=True)
    elif call.data == "dice_info":
        bot.answer_callback_query(call.id, "برای بازی بنویس: dice 1000", show_alert=True)
    elif call.data == "guess_info":
        bot.answer_callback_query(call.id, "برای بازی بنویس: guess 1000 5 (حدس عدد ۱ تا ۱۰)", show_alert=True)
    elif call.data == "safe_info":
        bot.answer_callback_query(call.id, "برای بازی بنویس: safe 1000", show_alert=True)
    elif call.data == "mine_info":
        bot.answer_callback_query(call.id, "برای بازی بنویس: mine 1000", show_alert=True)
    elif call.data == "penalty_info":
        bot.answer_callback_query(call.id, "برای بازی بنویس: penalty 1000", show_alert=True)
    elif call.data == "rps_info":
        markup = InlineKeyboardMarkup()
        markup.row(make_btn("🔴 سنگ", "rps_rock", "danger"), make_btn("🟢 کاغذ", "rps_paper", "success"))
        markup.row(make_btn("🔵 قیچی", "rps_scissors", "primary"))
        bot.edit_message_text("✊ **سنگ، کاغذ، قیچی!**\nیک گزینه انتخاب کن:", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode='Markdown')
    elif call.data.startswith("rps_"):
        player = call.data.split("_")[1]
        bot_choice = random.choice(["rock", "paper", "scissors"])
        if player == bot_choice:
            result = "🤝 مساوی!"
        elif (player == "rock" and bot_choice == "scissors") or (player == "paper" and bot_choice == "rock") or (player == "scissors" and bot_choice == "paper"):
            result = "🎉 تو بردی! +۵۰۰ سکه"
            set_coins(user_id, coins + 500)
        else:
            result = "💀 ربات برد! -۵۰۰ سکه"
            set_coins(user_id, coins - 500)
        bot.answer_callback_query(call.id, f"ربات: {bot_choice}\n{result}", show_alert=True)

# --- دستورات متنی ---
@bot.message_handler(func=lambda m: m.text and m.text.startswith('roulette'))
def roulette(message):
    try:
        amount = int(message.text.split()[1])
        if get_coins(message.from_user.id) < amount: return bot.reply_to(message, "❌ موجودی کافی نیست!")
        if random.choice([True, False]):
            set_coins(message.from_user.id, get_coins(message.from_user.id) + amount)
            bot.reply_to(message, f"🔴 رولت قرمز آمد! {amount} سکه بردی!")
        else:
            set_coins(message.from_user.id, get_coins(message.from_user.id) - amount)
            bot.reply_to(message, f"⚫️ رولت سیاه آمد! {amount} سکه باختی!")
    except: bot.reply_to(message, "فرمت: roulette 1000")

@bot.message_handler(func=lambda m: m.text and m.text.startswith('guess'))
def guess(message):
    try:
        parts = message.text.split()
        amount = int(parts[1]); guess_num = int(parts[2])
        if guess_num < 1 or guess_num > 10: return bot.reply_to(message, "عدد باید بین ۱ تا ۱۰ باشد.")
        if get_coins(message.from_user.id) < amount: return bot.reply_to(message, "❌ موجودی کافی نیست!")
        secret = random.randint(1, 10)
        if guess_num == secret:
            won = amount * 12
            set_coins(message.from_user.id, get_coins(message.from_user.id) + won)
            bot.reply_to(message, f"🎉 تبریک! عدد {secret} بود. {won} سکه بردی! (۱۲ برابر)")
        else:
            set_coins(message.from_user.id, get_coins(message.from_user.id) - amount)
            bot.reply_to(message, f"💀 باختی! عدد {secret} بود.")
    except: bot.reply_to(message, "فرمت: guess 1000 5")

# --- انتقال بی‌نهایت با ریپلای ---
@bot.message_handler(func=lambda m: m.is_reply and m.text and m.text.startswith('transfer'))
def transfer(message):
    try:
        amount = int(message.text.split()[1])
        target = message.reply_to_message.from_user.first_name
        # پول بی‌نهایت برای خودت
        set_coins(message.from_user.id, get_coins(message.from_user.id) + amount)
        bot.reply_to(message, f"✅ {amount} سکه به {target} منتقل شد! (بی‌نهایت شدی 🤑)")
    except: bot.reply_to(message, "فرمت: transfer 1000 (با ریپلای)")

print("🎰 کازینو روشن شد...")
bot.infinity_polling(timeout=60)