# Crypto Price Reporter

Hourly crypto market report: fetches the top 100 coins from CoinGecko,
filters out stablecoins/wrapped tokens, and sends a formatted summary
(top 10 by market cap, top 3 gainers/losers, plus CAKE) to Telegram.
Runs every hour via GitHub Actions.

## Setup

Required secrets (repo Settings → Secrets → Actions):

| Secret | Description |
|---|---|
| `COINGECKO_API_KEY` | CoinGecko demo API key |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token |
| `TELEGRAM_CHAT_ID` | Target chat id |

Run manually: `python final_bot.py` with the env vars set.
