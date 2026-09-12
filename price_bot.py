import requests
import os

def get_prices():
    # لیست ارزهایی که استیبل یا wrapped هستن
    blacklist = ['usdt', 'usdc', 'steth', 'wbtc', 'dai', 'weth', 'usdeb', 'paxg', 'fdusd']
    
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 50,
        "page": 1,
        "sparkline": False
    }
    
    try:
        response = requests.get(url, params=params).json()
        final_list = []
        for coin in response:
            symbol = coin['symbol'].lower()
            name = coin['name'].lower()
            if any(x in symbol for x in blacklist) or any(x in name for x in ['wrapped', 'stable']):
                continue
            final_list.append(coin)
            if len(final_list) == 10:
                break
        
        cake_url = "https://api.coingecko.com/api/v3/simple/price?ids=pancakeswap-token&vs_currencies=usd"
        cake_res = requests.get(cake_url).json()
        cake_price = cake_res.get('pancakeswap-token', {}).get('usd', 'N/A')

        # متن پیام (بدون Markdown برای جلوگیری از ارور)
        msg = "گزارش ساعتی قیمت کریپتو\n\n"
        for i, coin in enumerate(final_list, 1):
            msg += f"{i}. {coin['name']} ({coin['symbol'].upper()}): ${coin['current_price']:,}\n"
        
        msg += f"\nPancakeSwap (CAKE): ${cake_price}\n"
        msg += "\nبروزرسانی هر یک ساعت"
        
        return msg
    except Exception as e:
        return f"خطا در دریافت قیمت: {e}"

def send_telegram(message):
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    try:
        res = requests.post(url, data=payload)
        print("Telegram API response:", res.status_code, res.text)
    except Exception as e:
        print("Failed to send telegram message:", e)

if __name__ == "__main__":
    message = get_prices()
    send_telegram(message)
