import asyncio
import yfinance as yf
from telegram import Bot
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")  # Apni Telegram ID
SYMBOL = "BTC-USD" # BTC, ETH, GC=F for Gold

async def get_signal():
    data = yf.download(SYMBOL, period="1d", interval="15m")
    close = data['Close']
    rsi = 100 - (100 / (1 + close.pct_change().mean()))
    # Simple logic
    price = close.iloc[-1]
    sma20 = close.rolling(20).mean().iloc[-1]
    
    if price > sma20:
        return f"🟢 BUY Signal for {SYMBOL}\nPrice: {price:.2f}\nSMA20 se upar hai - Uptrend"
    else:
        return f"🔴 SELL Signal for {SYMBOL}\nPrice: {price:.2f}\nSMA20 se neeche hai - Downtrend"

async def main():
    bot = Bot(token=BOT_TOKEN)
    while True:
        signal = await get_signal()
        await bot.send_message(chat_id=CHAT_ID, text=signal)
        await asyncio.sleep(3600) # Har 1 ghante me

if __name__ == "__main__":
    asyncio.run(main())
