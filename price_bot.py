import requests
import os

token = os.getenv('TELEGRAM_BOT_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')

url = f"https://api.telegram.org/bot{token}/sendMessage"
data = {"chat_id": chat_id, "text": "تست نهایی اتصال ربات"}

response = requests.post(url, data=data)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
