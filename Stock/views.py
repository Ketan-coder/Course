from django.shortcuts import render, get_object_or_404
from .models import Stock
import yfinance as yf

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