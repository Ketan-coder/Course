from django.urls import path
from . import views

urlpatterns = [
    path("", views.stock_list, name="stock_list"),
    path("stock-data/<str:symbol>/",views.stock_detail, name="stock_detail"),
    path("watch/<str:symbol>/", views.start_watching_stock, name="watch_stock"),
    path("unwatch/<str:symbol>/", views.stop_watching_stock, name="unwatch_stock"),
    path("fetch-realtime/<str:symbol>/", views.get_realtime_stock_data, name="fetch_realtime_stock_data"),
    path("get_historical_prices/<str:symbol>/<str:duration>/", views.get_historical_stock_data, name="fetch_historical_stock_data")
]
