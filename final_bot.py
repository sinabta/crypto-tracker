import requests
import os
from datetime import datetime

def get_crypto_data():
    # CoinGecko doesn't provide 24h high/low in the same list call easily without sparkline or extra calls
    # but I can use 'price_change_percentage_24h' and build a mock High/Low or omit if not available
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 50,
        "page": 1,
        "price_change_percentage": "24h"
    }
    response = requests.get(url, params=params).json()
    
    # Filter for the specific list requested or top 10
    blacklist = ['usdt', 'usdc', 'steth', 'wbtc', 'dai', 'weth', 'usdeb', 'paxg', 'fdusd']
    top_coins = []
    for coin in response:
        if any(x in coin['symbol'].lower() for x in blacklist) or 'wrapped' in coin['name'].lower():
            continue
        top_coins.append(coin)
        if len(top_coins) == 10: break
    return top_coins

def get_cake():
    res = requests.get("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=pancakeswap-token&price_change_percentage=24h").json()
    return res[0]

def format_msg(coins, cake):
    now = datetime.now().strftime("%H:%M")
    msg = f"📊 Top 10 Crypto ({now})\n\n"
    
    for i, coin in enumerate(coins, 1):
        change = coin['price_change_percentage_24h'] or 0
        emoji = "🟢" if change >= 0 else "🔴"
        # Since standard free CoinGecko API doesn't give High/Low in this endpoint, I'll use placeholders
        # or indicate data limitation. 
        msg += f"{i}. {coin['name']}\n   `${coin['current_price']:,.2f}` {emoji} {change:+.2f}%\n"
        msg += f"   📈 N/A | 📉 N/A\n\n"
    
    msg += "---\n🥞 CAKE\n"
    change_cake = cake['price_change_percentage_24h'] or 0
    msg += f"   `${cake['current_price']:,.2f}` {'🟢' if change_cake >= 0 else '🔴'} {change_cake:+.2f}%\n"
    msg += "   📈 N/A | 📉 N/A"
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
