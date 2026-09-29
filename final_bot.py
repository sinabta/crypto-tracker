import requests
import os
from datetime import datetime, timedelta, timezone

COINGECKO = "https://api.coingecko.com/api/v3"
HEADERS = {"x-cg-demo-api-key": os.getenv("COINGECKO_API_KEY", "CG-kDLigiy8EcKVENdf7cKEDbUL")}

# Stablecoins and wrapped tokens to exclude
BLACKLIST = {
    "tether", "usd-coin", "dai", "binance-usd", "trueusd", "frax",
    "first-digital-usd", "usdd", "pax-gold", "wrapped-bitcoin",
    "staked-ether", "wrapped-steth", "bridged-usdc", "figure-heloc",
}


def get_crypto_data():
    """Top 10 non-stablecoin cryptos by market cap from CoinGecko."""
    resp = requests.get(
        f"{COINGECKO}/coins/markets",
        params={
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 50,
            "page": 1,
            "price_change_percentage": "24h",
        },
        headers=HEADERS,
        timeout=15,
    )
    resp.raise_for_status()
    coins = [c for c in resp.json() if c["id"] not in BLACKLIST]
    return coins[:10]


def get_cake():
    resp = requests.get(
        f"{COINGECKO}/coins/markets",
        params={
            "vs_currency": "usd",
            "ids": "pancakeswap-token",
            "price_change_percentage": "24h",
        },
        headers=HEADERS,
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()[0]


def format_msg(coins, cake):
    iran_time = datetime.now(timezone.utc) + timedelta(hours=3, minutes=30)
    now = iran_time.strftime("%H:%M")

    msg = f"\U0001f4ca Top 10 Crypto ({now})\n\n"

    for i, coin in enumerate(coins, 1):
        price = coin["current_price"]
        change = coin["price_change_percentage_24h"] or 0
        high = coin.get("high_24h") or 0
        low = coin.get("low_24h") or 0
        emoji = "\U0001f7e2" if change >= 0 else "\U0001f534"
        fmt = "${:,.4f}" if price < 1 else "${:,.2f}"

        msg += f"{i}. {coin['name']}\n"
        msg += f"   {fmt.format(price)} {emoji} {change:+.2f}%\n"
        msg += f"   \U0001f4c8 {fmt.format(high)} | \U0001f4c9 {fmt.format(low)}\n\n"

    cp = cake["current_price"]
    cc = cake["price_change_percentage_24h"] or 0
    ch = cake.get("high_24h") or 0
    cl = cake.get("low_24h") or 0
    cf = "${:,.3f}" if cp < 1 else "${:,.2f}"

    msg += "---\n\U0001f95f CAKE\n"
    msg += f"   {cf.format(cp)} {'🟢' if cc >= 0 else '🔴'} {cc:+.2f}%\n"
    msg += f"   \U0001f4c8 {cf.format(ch)} | \U0001f4c9 {cf.format(cl)}"
    return msg


def send_telegram(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("ERROR: TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID not set")
        print(message)
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    resp = requests.post(url, data={"chat_id": chat_id, "text": message}, timeout=10)
    if resp.status_code != 200:
        print(f"Telegram error {resp.status_code}: {resp.text}")


if __name__ == "__main__":
    try:
        coins = get_crypto_data()
        cake = get_cake()
        msg = format_msg(coins, cake)
        send_telegram(msg)
    except Exception as e:
        print(f"FATAL: {e}")
        raise
