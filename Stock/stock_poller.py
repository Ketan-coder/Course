import time
import json
import redis
import yfinance as yf
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import random
from django.conf import settings

# Ensure settings.STOCK_CACHE_TTL is defined in your Django settings.py

redis_client = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
channel_layer = get_channel_layer()

def get_cached_stock_data(symbol):
    try:
        cached_data = redis_client.get(f"stock_data:{symbol}")
        if cached_data:
            return json.loads(cached_data)
    except Exception as e:
        print(f"Error retrieving cached data for {symbol}: {e}")
        return None

def fetch_and_send_stock_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        # Fetching real-time data (using history with period='1d' is a common way to get the last closing price)
        hist = ticker.history(period="1d")
        # print("Hist",hist)
        if not hist.empty:
            current_price = hist['Close'].iloc[-1]
            price_change = current_price - hist['Open'].iloc[-1]
            if hist['Open'].iloc[-1] != 0:
                percentage_change = (price_change / hist['Open'].iloc[-1]) * 100
            else:
                percentage_change = 0.0
        else:
            print(f"No history data for {symbol}")
            return

        data = {
            'symbol': symbol,
            'price': round(current_price, 2),
            'price_change': round(price_change, 2),
            'percentage_change': round(percentage_change, 2),
        # Add other data you want to send, e.g., 'volume': hist['Volume'].iloc[-1]
        }

        # print("Data",data)

        # Cache data in Redis
        # redis_client.setex(f"stock_data:{symbol}", settings.STOCK_CACHE_TTL, json.dumps(data))
    except Exception as e:
        print(f"Error fetching real-time data for {symbol}: {e}")
        # Fallback: Attempt to use cached data if real-time fetching fails
        cached_data = get_cached_stock_data(symbol)
        if cached_data:
            print(f"Using cached data for {symbol} as fallback.")
            data = cached_data
        else:
            print(f"No cached data available for {symbol}. Consider more frequent background polling for this stock.")
            return None # Exit if no data is available
    return data


def poll_unwatched_stocks():
    # This function is now less critical as watched stocks are polled separately
    pass # We rely on the watched_poller for watched stocks and on-demand fetches for real-time data

def poll_watched_stocks():
    # This scheduler job is primarily for the initial setup and fallback
    # Real-time polling for actively watched stocks should be triggered by the frontend
    pass # The frontend will call the specific view to trigger real-time fetches

def add_watched_stock(symbol):
    try:
        redis_client.sadd('stocks:watched', symbol)
        print(f"Added {symbol} to watched stocks.")
    except Exception as e:
        print(f"Error adding {symbol} to watched stocks: {e}")

def remove_watched_stock(symbol):
    try:
        redis_client.srem('stocks:watched', symbol)
        print(f"Removed {symbol} from watched stocks.")
    except Exception as e:
        print(f"Error removing {symbol} from watched stocks: {e}")


scheduler = BackgroundScheduler()

def start_poller():
    # Poll unwatched stocks every 2-5 minutes
    scheduler.add_job(poll_unwatched_stocks, IntervalTrigger(minutes=random.randint(2, 5)), id='unwatched_poller')

    if not scheduler.running:
        scheduler.start()
        print("Stock poller started.")
