import os
import yfinance as yf
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

SYMBOL_MAP = {
    "btc": "BTC-USD",
    "eth": "ETH-USD",
    "gold": "GC=F",
    "eurusd": "EURUSD=X"
}

def get_signal_text(symbol="BTC-USD"):
    try:
        data = yf.download(symbol, period="1d", interval="15m", progress=False)
        if data.empty:
            return "Data nahi mila, dobara try karo"
        close = data['Close']
        price = float(close.iloc[-1])
        sma20 = float(close.rolling(20).mean().iloc[-1])
        sma50 = float(close.rolling(50).mean().iloc[-1])
        if price > sma20 and sma20 > sma50:
            trend = "🟢 STRONG BUY"
        elif price > sma20:
            trend = "🟢 BUY"
        elif price < sma20 and sma20 < sma50:
            trend = "🔴 STRONG SELL"
        else:
            trend = "🔴 SELL"
        return f"{trend}\n\nPair: {symbol}\nPrice: {price:.2f}\nSMA20: {sma20:.2f}\nSMA50: {sma50:.2f}\n\nTimeframe: 15m"
    except Exception as e:
        return f"Error: {e}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Bot Live hai.\nCommands:\n/signal btc\n/signal eth\n/signal gold\n/signal eurusd")

async def signal_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    coin = "btc"
    if context.args:
        coin = context.args[0].lower()
    symbol = SYMBOL_MAP.get(coin, "BTC-USD")
    text = get_signal_text(symbol)
    await update.message.reply_text(text)

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("signal", signal_cmd))
print("Bot Running...")
app.run_polling()
