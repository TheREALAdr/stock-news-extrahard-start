# ----------------------------- IMPORTS ----------------------------- #
import os
import requests
from twilio.rest import Client

# ---------------------------- CONSTANTS ---------------------------- #

STOCK = "TSLA"
COMPANY_NAME = "Tesla"

test_ALPHA_VANTAGE_API_KEY = os.environ.get("test_ALPHA_VANTAGE_API_KEY")
test_NEWS_API_KEY = os.environ.get("test_NEWS_API_KEY")
test_TWILIO_PHONE_NUMBER = os.environ.get("test_TWILIO_PHONE_NUMBER")
test_TWILIO_ACCOUNT_SID = os.environ.get("test_TWILIO_ACCOUNT_SID")
test_TWILIO_AUTH_TOKEN = os.environ.get("test_TWILIO_AUTH_TOKEN")
test_USER_PHONE_NUMBER = os.environ.get("test_USER_PHONE_NUMBER")


# ------------------------ ALPHA-VANTAGE API ------------------------ #

alpha_vantage_parameters = {
    "function": "TIME_SERIES_DAILY_ADJUSTED",
    "symbol": STOCK,
    "outputsize": "compact",
    "datatype": "json",
    "apikey": test_ALPHA_VANTAGE_API_KEY
}

alpha_vantage_data = requests.get(url="https://www.alphavantage.co/query", params=alpha_vantage_parameters).json()
alpha_vantage_time_series = alpha_vantage_data["Time Series (Daily)"]
alpha_vantage_data_list = [(key, value) for key, value in alpha_vantage_time_series.items()]
recent_alpha_vantage_data = alpha_vantage_data_list[:2]

# -------------------- CALCULATING STOCK CHANGES -------------------- #

last_day_closing_price = float(recent_alpha_vantage_data[0][1]['4. close'])
second_last_day_closing_price = float(recent_alpha_vantage_data[1][1]['4. close'])

closing_price_difference = last_day_closing_price - second_last_day_closing_price
closing_price_comparison = abs(closing_price_difference)
closing_price_comparison_percentage = format(closing_price_comparison / second_last_day_closing_price * 100, ".2f")

negative_comparison = 0.99 * second_last_day_closing_price
positive_comparison = 1.01 * second_last_day_closing_price

# ------------------- GETTING NEWS WITH NEWS API ------------------- #

news_parameters = {
    "apikey": test_NEWS_API_KEY,
    "q": COMPANY_NAME,
    "pageSize": 3,
}


def find_change_in_percentage():
    if closing_price_difference > 0:
        return f"{STOCK}: 🔺{closing_price_comparison_percentage}%"
    else:
        return f"{STOCK}: 🔻{closing_price_comparison_percentage}%"


def get_news():
    news_api_data = requests.get("https://newsapi.org/v2/top-headlines", params=news_parameters).json()
    news_api_articles = news_api_data["articles"][:3]
    news_to_send = ""
    for article in news_api_articles:
        news_to_send += f"Headline: {article['title']}\nBrief: {article['description']}\n\n"
    return news_to_send


# ---------------- SENDING NOTIFICATION WITH TWILIO ---------------- #

news_to_find = False

if last_day_closing_price >= positive_comparison or last_day_closing_price <= negative_comparison:
    news_to_find = True

if news_to_find:
    client = Client(test_TWILIO_ACCOUNT_SID, test_TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=f"\n{find_change_in_percentage()}\n\n{get_news()}",
        from_=test_TWILIO_PHONE_NUMBER,
        to=test_USER_PHONE_NUMBER
    )
