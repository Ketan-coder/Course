from django.apps import AppConfig


class StockConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Stock'

    def ready(self):
            from . import stock_poller
            stock_poller.start_poller()