from django.contrib import admin
from .models import Stock, StockEvents, StockPriceHistory
# Register your models here.
class StockAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'name', 'price', 'market_cap', 'created_at')
    search_fields = ('symbol', 'name')
    list_filter = ('sector', 'industry', 'country')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    fieldsets = (
        (None, {
            'fields': ('symbol', 'name', 'description', 'logo')
        }),
        ('Financial Information', {
            'fields': ('price', 'open_price', 'close_price', 'day_high', 'day_low',
                       'week_52_high', 'week_52_low', 'volume', 'market_cap')
        }),
        ('Additional Information', {
            'fields': ('website', 'exchange', 'sector', 'industry', 'country')
        }),
        ('Extra Fields', {
            'fields': ('extra_fields',)
        }),
    )

class StockEventsAdmin(admin.ModelAdmin):
    list_display = ('stock', 'event_type', 'event_date', 'created_at')
    search_fields = ('stock__symbol', 'event_type')
    list_filter = ('event_type',)
    ordering = ('-event_date',)
    date_hierarchy = 'event_date'
    fieldsets = (
        (None, {
            'fields': ('stock', 'event_type', 'event_date', 'description')
        }),
        ('Extra Fields', {
            'fields': ('extra_fields',)
        }),
    )

class StockPriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('stock', 'close_price', 'datetime')
    search_fields = ('stock__symbol',)
    list_filter = ('stock__sector', 'stock__industry')
    ordering = ('-datetime',)
    date_hierarchy = 'datetime'
    fieldsets = (
        (None, {
            'fields': ('stock', 'close_price', 'datetime')
        }),
        ('Extra Fields', {
            'fields': ('extra_fields',)
        }),
    )

admin.site.register(Stock, StockAdmin)
admin.site.register(StockEvents, StockEventsAdmin)
admin.site.register(StockPriceHistory, StockPriceHistoryAdmin)
