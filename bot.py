import telebot
from flask import Flask, render_template
from threading import Thread

BOT_TOKEN = "YOUR_BOT_TOKEN"
WEBAPP_URL = "https://your-app-name.onrender.com"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

@bot.message_handler(commands=['start'])
def start_handler(message):
    markup = telebot.types.InlineKeyboardMarkup()
    btn = telebot.types.InlineKeyboardButton("🚀 बॉट लॉन्च करें", web_app=telebot.types.WebAppInfo(url=WEBAPP_URL))
    markup.add(btn)
    bot.send_message(message.chat.id, f"नमस्ते {message.from_user.first_name}!\n👇 नीचे बटन पर क्लिक करें बॉट शुरू करने के लिए:", reply_markup=markup)

keep_alive()
bot.polling()
