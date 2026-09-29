import requests
import os
from datetime import datetime, timedelta, timezone

# Stablecoins, wrapped tokens, and pegged assets to exclude
BLACKLIST = {
    "USDT", "USDC", "DAI", "BUSD", "TUSD", "FDUSD", "USDP", "USDD",
    "WBTC", "STETH", "WBETH", "BETH", "WSTETH", "PAXG", "USDE",
    "EUR", "GBP", "AUD", "BRL", "TRY",
}


def get_crypto_data():
    """Top 10 by market cap from CoinPaprika (free, no API key)."""
    resp = requests.get(
        "https://api.coinpaprika.com/v1/tickers",
        params={"limit": 100},
        timeout=15,
    )
    resp.raise_for_status()
    tickers = resp.json()

    result = []
    for t in tickers:
        if t["symbol"] in BLACKLIST:
            continue
        result.append(t)
        if len(result) == 10:
            break
    return result


def get_cake():
    """Fetch CAKE specifically from CoinPaprika."""
    resp = requests.get(
        "https://api.coinpaprika.com/v1/tickers/cake-pancakeswap",
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def format_msg(coins, cake):
    iran_time = datetime.now(timezone.utc) + timedelta(hours=3, minutes=30)
    now = iran_time.strftime("%H:%M")

    msg = f"\U0001f4ca Top 10 Crypto ({now})\n\n"

    for i, coin in enumerate(coins, 1):
        q = coin["quotes"]["USD"]
        price = q["price"]
        change = q["percent_change_24h"] or 0
        emoji = "\U0001f7e2" if change >= 0 else "\U0001f534"
        fmt = "${:,.4f}" if price < 1 else "${:,.2f}"

        msg += f"{i}. {coin['symbol']}\n"
        msg += f"   {fmt.format(price)} {emoji} {change:+.2f}%\n\n"

    q = cake["quotes"]["USD"]
    cp = q["price"]
    cc = q["percent_change_24h"] or 0
    cf = "${:,.3f}" if cp < 1 else "${:,.2f}"

    msg += "---\n\U0001f95f CAKE\n"
    msg += f"   {cf.format(cp)} {'🟢' if cc >= 0 else '🔴'} {cc:+.2f}%"
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
