import os
import threading
from flask import Flask
import telebot
from telebot import types
import yfinance as yf
import ta

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

app = Flask(__name__)

@app.route('/')
def home():
    return "Nawabshah Trading Bot is LIVE!"

def get_signal(symbol="BTC-USD"):
    try:
        # Gold ke liye GC=F, BTC ke liye BTC-USD
        if symbol.lower() in ["xauusd", "gold", "xau"]:
            ticker = "GC=F"
            name = "GOLD (XAUUSD)"
        elif symbol.lower() in ["btc", "bitcoin"]:
            ticker = "BTC-USD"
            name = "BTC"
        else:
            ticker = f"{symbol.upper()}-USD"
            name = symbol.upper()

        data = yf.download(ticker, period="2d", interval="15m", auto_adjust=True)
        if len(data) < 50:
            return f"⚠️ {name} ka data kam hai."

        close = data['Close']
        rsi = ta.momentum.RSIIndicator(close).rsi().iloc[-1]
        ema_fast = ta.trend.EMAIndicator(close, window=20).ema_indicator().iloc[-1]
        ema_slow = ta.trend.EMAIndicator(close, window=50).ema_indicator().iloc[-1]

        price = float(close.iloc[-1])

        if ema_fast > ema_slow and rsi > 50:
            signal = "🟢 BUY"
            trend = "Uptrend"
        elif ema_fast < ema_slow and rsi < 50:
            signal = "🔴 SELL"
            trend = "Downtrend"
        else:
            signal = "🟡 WAIT / SIDEWAYS"
            trend = "Sideways"

        msg = f"""📊 *{name} SIGNAL*

Price: `${price:,.2f}`
Signal: {signal}
Trend: {trend}
RSI: {rsi:.2f}
EMA 20: {ema_fast:.2f}
EMA 50: {ema_slow:.2f}

⏰ Timeframe: 15M
⚠️ Ye financial advice nahi hai.
"""
        return msg
    except Exception as e:
        return f"Error: {e}"

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("/signal btc", "/signal xauusd", "/signal eth")
    bot.send_message(message.chat.id,
        "Assalam-o-Alaikum Anas Bhai! 🤝\n\n"
        "✅ *Nawabshah Trading Bot LIVE hai!*\n\n"
        "Commands:\n"
        "/signal btc - Bitcoin signal\n"
        "/signal xauusd - Gold signal\n"
        "/signal eth - Ethereum signal\n\n"
        "Kisi bhi coin ka naam likho: /signal sol",
        parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(commands=['signal'])
def signal_handler(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "Example: /signal btc ya /signal xauusd")
            return
        symbol = parts[1]
        bot.send_chat_action(message.chat.id, 'typing')
        result = get_signal(symbol)
        bot.send_message(message.chat.id, result, parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(func=lambda m: True)
def all_msg(message):
    if message.text and message.text.startswith("/"):
        symbol = message.text.replace("/", "")
        result = get_signal(symbol)
        bot.send_message(message.chat.id, result, parse_mode="Markdown")
    else:
        start(message)

def run_bot():
    print("BOT STARTED - Polling Active")
    bot.infinity_polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
