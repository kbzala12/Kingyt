import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

BOT_TOKEN = "7559801414:AAG6nHs9zoF9CLDknI9E3c5zBqz8ekcgPXQ"
WEB_APP_URL = "https://kingyt.onrender.com/"  # ✅ WebApp URL लिंक

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(
        KeyboardButton("🎥 वीडियो देखो"),
        KeyboardButton("🧑‍🤝‍🧑 रेफ़रल")
    )
    markup.row(
        KeyboardButton("🎁 मेरा अकाउंट", web_app=WebAppInfo(url=WEB_APP_URL))  # ✅ WebApp खोलने वाला बटन
    )
    bot.send_message(message.chat.id, "🙏 स्वागत है! नीचे दिए गए विकल्पों में से चुनें:", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    if message.text == "🎥 वीडियो देखो":
        bot.send_message(message.chat.id, "📺 उपलब्ध वीडियो देखने के लिए WebApp खोलें।")
    elif message.text == "🧑‍🤝‍🧑 रेफ़रल":
        bot.send_message(message.chat.id, f"👥 अपने दोस्तों को जोड़ें और पॉइंट्स पाएं!\nआपका लिंक: https://t.me/Hkzyt_bot?start={message.from_user.id}")
    elif message.text == "🎁 मेरा अकाउंट":
        bot.send_message(message.chat.id, "🔄 कृपया वेट करें, WebApp लोड हो रहा है...")

print("🤖 Bot is running...")
bot.infinity_polling()
