import requests
import os
import time
from datetime import datetime, timedelta, timezone

COINGECKO = "https://api.coingecko.com/api/v3"

def _cg_headers():
    key = os.getenv("COINGECKO_API_KEY")
    if not key:
        raise RuntimeError("COINGECKO_API_KEY env var is not set")
    return {"x-cg-demo-api-key": key}

# Stablecoins and wrapped tokens to exclude
BLACKLIST = {
    "tether", "usd-coin", "dai", "binance-usd", "trueusd", "frax",
    "first-digital-usd", "usdd", "pax-gold", "wrapped-bitcoin",
    "staked-ether", "wrapped-steth", "bridged-usdc", "figure-heloc",
}


def _cg_get(path, params, retries=3):
    """GET with retry on rate-limit / transient errors."""
    for attempt in range(retries):
        resp = requests.get(f"{COINGECKO}{path}", params=params,
                            headers=_cg_headers(), timeout=15)
        if resp.status_code == 429 and attempt < retries - 1:
            wait = 2 ** attempt * 10
            print(f"CoinGecko rate-limited, retrying in {wait}s...")
            time.sleep(wait)
            continue
        resp.raise_for_status()
        return resp.json()
    raise RuntimeError("CoinGecko kept rate-limiting us")


def get_crypto_data():
    """Top non-stablecoin cryptos by market cap from CoinGecko."""
    coins = _cg_get("/coins/markets", {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 250,
        "page": 1,
        "price_change_percentage": "24h",
    })
    return [c for c in coins if c["id"] not in BLACKLIST]


def get_gainers_losers():
    """Top gainers/losers from CoinGecko's dedicated endpoint.
    Returns (gainers, losers) or (None, None) if unavailable (e.g. demo plan)."""
    try:
        data = _cg_get("/coins/top_gainers_losers",
                       {"vs_currency": "usd", "duration": "24h"})
        gainers = data.get("top_gainers") or []
        losers = data.get("top_losers") or []
        if gainers and losers:
            return gainers, losers
    except Exception:
        pass
    return None, None


def get_cake():
    coins = _cg_get("/coins/markets", {
        "vs_currency": "usd",
        "ids": "pancakeswap-token",
        "price_change_percentage": "24h",
    })
    return coins[0]


def format_msg(all_coins, cake, gainers=None, losers=None):
    iran_time = datetime.now(timezone.utc) + timedelta(hours=3, minutes=30)
    now = iran_time.strftime("%H:%M")

    top_10 = all_coins[:10]
    if gainers and losers:
        best_3 = [(c["name"], c.get("usd_24h_change") or 0) for c in gainers[:3]]
        worst_3 = [(c["name"], c.get("usd_24h_change") or 0) for c in losers[:3]]
    else:
        sorted_by_change = sorted(all_coins, key=lambda x: x.get('price_change_percentage_24h') or 0, reverse=True)
        best_3 = [(c["name"], c.get("price_change_percentage_24h") or 0) for c in sorted_by_change[:3]]
        worst_3 = [(c["name"], c.get("price_change_percentage_24h") or 0) for c in sorted_by_change[-3:]]

    msg = f"\U0001f4ca Crypto Report ({now})\n\n"

    msg += "\U0001f4c8 Top 10 by Market Cap:\n"
    for i, coin in enumerate(top_10, 1):
        price = coin["current_price"]
        change = coin["price_change_percentage_24h"] or 0
        high = coin.get("high_24h") or 0
        low = coin.get("low_24h") or 0
        emoji = "\U0001f7e2" if change >= 0 else "\U0001f534"
        fmt = "${:,.4f}" if price < 1 else "${:,.2f}"

        msg += f"{i}. {coin['name']}\n"
        msg += f"   {fmt.format(price)} {emoji} {change:+.2f}%\n"
        msg += f"   \U0001f4c8 {fmt.format(high)} | \U0001f4c9 {fmt.format(low)}\n\n"

    msg += "\U0001f3c6 Top Gainers (24h):\n"
    for name, change in best_3:
        msg += f"• {name} ({change:+.2f}%)\n"

    msg += "\n\U0001f409 Top Losers (24h):\n"
    for name, change in worst_3:
        msg += f"• {name} ({change:+.2f}%)\n"

    cp = cake["current_price"]
    cc = cake["price_change_percentage_24h"] or 0
    ch = cake.get("high_24h") or 0
    cl = cake.get("low_24h") or 0
    cf = "${:,.3f}" if cp < 1 else "${:,.2f}"

    msg += "\n---\n\U0001f95f CAKE\n"
    msg += f"   {cf.format(cp)} {'🟢' if cc >= 0 else '🔴'} {cc:+.2f}%\n"
    msg += f"   \U0001f4c8 {cf.format(ch)} | \U0001f4c9 {cf.format(cl)}"
    return msg


def send_telegram(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("ERROR: TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID not set")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    resp = requests.post(url, data={"chat_id": chat_id, "text": message}, timeout=10)
    data = resp.json()
    if not data.get("ok"):
        raise RuntimeError(f"Telegram send failed: {data}")
    print(f"Telegram message sent (id={data['result']['message_id']})")


if __name__ == "__main__":
    try:
        all_coins = get_crypto_data()
        cake = get_cake()
        gainers, losers = get_gainers_losers()
        msg = format_msg(all_coins, cake, gainers, losers)
        send_telegram(msg)
    except Exception as e:
        print(f"FATAL: {e}")
        raise
