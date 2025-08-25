import telebot
from telebot import types
import sqlite3
from flask import Flask
import threading
import os

# ---------------- CONFIG ----------------
BOT_TOKEN = "8267991203:AAH7-oOq-qKAed4OSBQdMxlg-UDCVZLyzF0"     # 👉 अपना Bot Token डालो
ADMIN_ID = 7459795138            # 👉 अपना Admin ID डालो
GROUP_ID =      # 👉 अपना Group ID डालो
DAILY_BONUS = 10
REFERRAL_POINTS = 100
SUBMIT_COST = 1280
BOT_USERNAME = "ytbotkb_bot" # 👉 अपना बॉट username (बिना @)

bot = telebot.TeleBot(BOT_TOKEN)

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY, points INTEGER, ref INTEGER)''')
    conn.commit()
    conn.close()

def check_user(user_id):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    if not c.fetchone():
        c.execute("INSERT INTO users (user_id, points, ref) VALUES (?, ?, ?)", (user_id, 0, 0))
    conn.commit()
    conn.close()

def update_points(user_id, amount):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("UPDATE users SET points = points + ? WHERE user_id=?", (amount, user_id))
    conn.commit()
    conn.close()

def deduct_points(user_id, amount):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("UPDATE users SET points = points - ? WHERE user_id=?", (amount, user_id))
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect("bot.db")
    c = conn.cursor()
    c.execute("SELECT points, ref FROM users WHERE user_id=?", (user_id,))
    data = c.fetchone()
    conn.close()
    return data if data else (0, 0)

# ---------------- MAIN MENU ----------------
def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🎁 Daily Bonus", "👥 Invite Friends")
    kb.row("👛 Wallet", "🔗 Submit URL")
    return kb

# ---------------- START ----------------
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    args = message.text.split()
    check_user(user_id)

    # ग्रुप जॉइन चेक
    try:
        member = bot.get_chat_member(GROUP_ID, user_id)
        if member.status == "left":
            bot.send_message(user_id, "🚫 पहले हमारे ग्रुप को Join करें फिर बॉट इस्तेमाल करें:\nhttps://t.me/YourGroupLink")
            return
    except:
        bot.send_message(user_id, "⚠️ Error: Group ID सही नहीं है।")
        return

    # Referral System
    if len(args) > 1:
        referrer_id = args[1]
        if referrer_id != str(user_id):
            check_user(referrer_id)
            update_points(int(referrer_id), REFERRAL_POINTS)
            conn = sqlite3.connect("bot.db")
            c = conn.cursor()
            c.execute("UPDATE users SET ref = ref + 1 WHERE user_id=?", (referrer_id,))
            conn.commit()
            conn.close()
            bot.send_message(int(referrer_id), f"🎉 आपके लिंक से नया यूज़र जुड़ा! +{REFERRAL_POINTS} Coin")

    bot.send_message(user_id,
        "👋 Welcome!\n\n👉 नीचे Menu से अपना Option चुनें:",
        reply_markup=main_menu()
    )

# ---------------- DAILY BONUS ----------------
@bot.message_handler(func=lambda m: m.text == "🎁 Daily Bonus")
def daily_bonus(message):
    user_id = message.from_user.id
    update_points(user_id, DAILY_BONUS)
    bot.reply_to(message, f"✅ आपको {DAILY_BONUS} Coin मिले!\n👛 बैलेंस: {get_user(user_id)[0]} Coin")

# ---------------- INVITE FRIENDS ----------------
@bot.message_handler(func=lambda m: m.text == "👥 Invite Friends")
def invite(message):
    user_id = message.from_user.id
    bot.reply_to(message,
        f"👉 अपना Invite Link:\nhttps://t.me/{BOT_USERNAME}?start={user_id}\n\n"
        f"हर नए यूज़र पर आपको {REFERRAL_POINTS} Coin मिलेंगे ✅"
    )

# ---------------- WALLET ----------------
@bot.message_handler(func=lambda m: m.text == "👛 Wallet")
def wallet(message):
    user_id = message.from_user.id
    points, ref = get_user(user_id)
    bot.reply_to(message, f"👤 Profile:\n\n👛 Coins: {points}\n👥 Referrals: {ref}")

# ---------------- SUBMIT URL ----------------
@bot.message_handler(func=lambda m: m.text == "🔗 Submit URL")
def submit_url(message):
    user_id = message.from_user.id
    points, _ = get_user(user_id)
    if points >= SUBMIT_COST:
        msg = bot.send_message(user_id, "👉 अपना YouTube URL भेजें (Cost: 1280 Coin):")
        bot.register_next_step_handler(msg, process_url)
    else:
        bot.reply_to(message, f"❌ आपके पास पर्याप्त Coin नहीं हैं!\n1280 Coin चाहिए।\n👛 बैलेंस: {points}")

def process_url(message):
    user_id = message.from_user.id
    url = message.text
    points, _ = get_user(user_id)
    if points >= SUBMIT_COST:
        deduct_points(user_id, SUBMIT_COST)
        bot.send_message(ADMIN_ID, f"📤 नया URL सबमिट:\n👤 {user_id}\n🔗 {url}")
        bot.send_message(user_id, f"✅ आपका URL Admin को भेज दिया गया!\n👛 नया बैलेंस: {get_user(user_id)[0]}")
    else:
        bot.send_message(user_id, "❌ पर्याप्त Coin नहीं हैं!")

# ---------------- ADMIN PANEL ----------------
@bot.message_handler(commands=["admin"])
def admin(message):
    if message.from_user.id == ADMIN_ID:
        conn = sqlite3.connect("bot.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users")
        users = c.fetchall()
        conn.close()
        report = "📊 User Data:\n"
        for u in users:
            report += f"👤 {u[0]} | 💰 {u[1]} | 👥 {u[2]}\n"
        bot.send_message(ADMIN_ID, report)
    else:
        bot.reply_to(message, "⛔ Access Denied!")

# ---------------- KEEP ALIVE ----------------
app = Flask('')
@app.route('/')
def home():
    return "Bot is Running!"

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = threading.Thread(target=run)
    t.start()

# ---------------- START BOT ----------------
if __name__ == "__main__":
    init_db()
    keep_alive()
    bot.polling()