import requests
import os
from datetime import datetime, timedelta

def get_crypto_data():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 50,
        "page": 1,
        "price_change_percentage": "24h"
    }
    response = requests.get(url, params=params).json()
    
    # لیست سیاه برای حذف سکه‌های بی‌ربط یا پِگ‌شده مثل HELOC یا استیبل‌کوین‌ها
    blacklist = ['heloc', 'figr', 'usdt', 'usdc', 'steth', 'wbtc', 'dai', 'weth', 'usdeb', 'paxg', 'fdusd', 'wrapped', 'stable']
    
    top_coins = []
    for coin in response:
        symbol = coin['symbol'].lower()
        name = coin['name'].lower()
        if any(x in symbol for x in blacklist) or any(x in name for x in blacklist):
            continue
        top_coins.append(coin)
        if len(top_coins) == 10: 
            break
    return top_coins

def get_cake():
    res = requests.get("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=pancakeswap-token&price_change_percentage=24h").json()
    return res[0]

def format_msg(coins, cake):
    # زمان به وقت ایران (UTC + 3:30)
    iran_time = datetime.utcnow() + timedelta(hours=3, minutes=30)
    now = iran_time.strftime("%H:%M")
    
    msg = f"📊 Top 10 Crypto ({now})\n\n"
    
    for i, coin in enumerate(coins, 1):
        change = coin['price_change_percentage_24h'] or 0
        emoji = "🟢" if change >= 0 else "🔴"
        high = coin.get('high_24h') or 0
        low = coin.get('low_24h') or 0
        
        # تعیین تعداد اعشار: زیر ۱ دلار ۳ رقم اعشار، بالای ۱ دلار ۲ رقم اعشار
        if coin['current_price'] < 1:
            price_fmt = "${:,.3f}"
        else:
            price_fmt = "${:,.2f}"
            
        msg += f"{i}. {coin['name']}\n"
        msg += f"   {price_fmt.format(coin['current_price'])} {emoji} {change:+.2f}%\n"
        msg += f"   📈 {price_fmt.format(high)} | 📉 {price_fmt.format(low)}\n\n"
    
    msg += "---\n🥞 CAKE\n"
    change_cake = cake['price_change_percentage_24h'] or 0
    high_cake = cake.get('high_24h') or 0
    low_cake = cake.get('low_24h') or 0
    
    cake_fmt = "${:,.3f}" if cake['current_price'] < 1 else "${:,.2f}"
    
    msg += f"   {cake_fmt.format(cake['current_price'])} {'🟢' if change_cake >= 0 else '🔴'} {change_cake:+.2f}%\n"
    msg += f"   📈 {cake_fmt.format(high_cake)} | 📉 {cake_fmt.format(low_cake)}"
    return msg

def send_telegram(message):
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    requests.post(url, data=payload)

if __name__ == "__main__":
    coins = get_crypto_data()
    cake = get_cake()
    send_telegram(format_msg(coins, cake))
