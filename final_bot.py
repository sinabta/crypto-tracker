import requests
import os
from datetime import datetime, timedelta, timezone

BINANCE = "https://api.binance.com/api/v3"

# Stablecoins, fiat pairs, and wrapped tokens to exclude
BLACKLIST = {
    "USDC", "BUSD", "TUSD", "DAI", "FDUSD", "USDP", "USDD", "EUR",
    "GBP", "AUD", "BRL", "TRY", "AEUR", "UST", "PAXG", "WBTC",
    "STETH", "WBETH", "BETH", "USD1", "BIDR", "USDCUSDT", "FDUSDUSDT",
}


def get_crypto_data():
    """Top 10 USDT pairs by 24h volume from Binance (no API key)."""
    resp = requests.get(f"{BINANCE}/ticker/24hr", timeout=15)
    resp.raise_for_status()
    all_tickers = resp.json()

    usdt_pairs = []
    for t in all_tickers:
        if not t["symbol"].endswith("USDT"):
            continue
        base = t["symbol"][:-4]
        if base in BLACKLIST:
            continue
        usdt_pairs.append(t)

    usdt_pairs.sort(key=lambda t: float(t.get("quoteVolume", 0)), reverse=True)
    return usdt_pairs[:10]


def get_cake():
    resp = requests.get(f"{BINANCE}/ticker/24hr", params={"symbol": "CAKEUSDT"}, timeout=15)
    resp.raise_for_status()
    return resp.json()


def format_msg(coins, cake):
    iran_time = datetime.now(timezone.utc) + timedelta(hours=3, minutes=30)
    now = iran_time.strftime("%H:%M")

    msg = f"\U0001f4ca Top 10 Crypto ({now})\n\n"

    for i, coin in enumerate(coins, 1):
        price = float(coin["lastPrice"])
        change = float(coin["priceChangePercent"])
        high = float(coin["highPrice"])
        low = float(coin["lowPrice"])
        emoji = "\U0001f7e2" if change >= 0 else "\U0001f534"
        fmt = "${:,.4f}" if price < 1 else "${:,.2f}"
        symbol = coin["symbol"].replace("USDT", "")

        msg += f"{i}. {symbol}\n"
        msg += f"   {fmt.format(price)} {emoji} {change:+.2f}%\n"
        msg += f"   \U0001f4c8 {fmt.format(high)} | \U0001f4c9 {fmt.format(low)}\n\n"

    cp = float(cake["lastPrice"])
    cc = float(cake["priceChangePercent"])
    ch = float(cake["highPrice"])
    cl = float(cake["lowPrice"])
    cf = "${:,.3f}" if cp < 1 else "${:,.2f}"

    msg += "---\n\U0001f95f CAKE\n"
    msg += f"   {cf.format(cp)} {'🟢' if cc >= 0 else '🔴'} {cc:+.2f}%\n"
    msg += f"   📈 {cf.format(ch)} | 📉 {cf.format(cl)}"
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
