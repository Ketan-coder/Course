# yourapp/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/metrics/$", consumers.MetricsConsumer.as_asgi()),
    re_path(r"ws/security/$", consumers.SecurityConsumer.as_asgi()),
    re_path(r"ws/records/$", consumers.RecordsConsumer.as_asgi()),
]
