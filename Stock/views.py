from django.shortcuts import render, get_object_or_404
from .models import Stock
import yfinance as yf
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from .stock_poller import redis_client
from Stock.stock_poller import fetch_and_send_stock_data
# Create your views here.
def index(request):
    return render(request,"base.html")

def stock_detail(request, symbol):
    """
    Displays details for a specific stock, including real-time price.
    """
    stock = get_object_or_404(Stock, symbol=symbol)

    try:
        ticker = yf.Ticker(symbol)
        current_price = ticker.history(period="1d")['Close'].iloc[-1]
    except Exception as e:
        current_price = None
        print(f"Error fetching real-time price for {symbol}: {e}")

    context = {
        'stock': stock,
        'current_price': current_price,
    }
    return render(request, 'stock/stock_detail.html', context)

@require_POST
def start_watching_stock(request, symbol):
    """Adds a stock symbol to the watched set in Redis."""
    redis_client.sadd("stocks:watched", symbol)
    return JsonResponse({'status': 'watching started'})

@require_POST
def stop_watching_stock(request, symbol):
    """Removes a stock symbol from the watched set in Redis."""
    redis_client.srem("stocks:watched", symbol)
    return JsonResponse({'status': 'watching stopped'})

@require_GET
def get_realtime_stock_data(request, symbol):
    """Fetches real-time data for a watched stock."""
    try:
        stock_data = fetch_and_send_stock_data(symbol)
        print(stock_data)
        return JsonResponse(stock_data, safe=False)
    except Exception as e:
        print(f"Error fetching real-time data for {symbol}: {e}")
        return JsonResponse({'error': 'Failed to fetch real-time data'}, status=500)

@require_GET
def get_historical_stock_data(request, symbol, duration='1y'):
    """Fetches historical closing prices for a stock."""
    try:
        ticker = yf.Ticker(symbol)
        # What are the different durations i can use:
        # 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
        # Default is '1y' if not provided in the URL

        # Use the duration parameter for fetching history
        hist = ticker.history(period=duration)['Close']
        historical_prices = hist.tolist()
        # Format data as [{ x: timestamp, y: price }, ...]
        formatted_data = [{"x": timestamp.timestamp() * 1000, "y": price} for timestamp, price in hist.items()]
        return JsonResponse(formatted_data, safe=False)
    except Exception as e:
        print(f"Error fetching historical data for {symbol}: {e}")
        return JsonResponse({'error': 'Failed to fetch historical data'}, status=500)
