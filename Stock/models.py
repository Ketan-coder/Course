from decimal import Decimal
from django.db import models

class Stock(models.Model):
    symbol = models.CharField(max_length=25, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    # chart_data = models.JSONField(blank=True, null=True)
    date_added = models.DateField(auto_now_add=True)
    logo = models.ImageField(upload_to='stock_logos', blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    exchange = models.CharField(max_length=50, blank=True, null=True)
    sector = models.CharField(max_length=100, blank=True, null=True)
    industry = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)

    open_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    close_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    day_high = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    day_low = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    week_52_high = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    week_52_low = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    volume = models.BigIntegerField(blank=True, null=True)
    market_cap = models.BigIntegerField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    bookmarked_by = models.ManyToManyField(
        "Users.Profile", related_name="bookmarked_stocks", verbose_name=("Bookmarked by"),
    )

    extra_fields = models.JSONField(blank=True, null=True, default=dict)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # Automatically update 52-week high/low
        if self.week_52_high is None or self.price > self.week_52_high:
            self.week_52_high: Decimal = self.price
        if self.week_52_low is None or self.price < self.week_52_low:
            self.week_52_low: Decimal = self.price

        # Optional: update extra_fields with deltas etc.
        self.extra_fields['last_updated'] = str(self.updated_at)
        self.extra_fields['price_change'] = float(self.price) - float(self.close_price or 0)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.symbol} - {self.name}"


class StockEvents(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='events', null=True, blank=True)
    event_type = models.CharField(max_length=50)  # e.g., 'Earnings', 'Dividend', etc.
    event_date = models.DateField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    extra_fields = models.JSONField(blank=True, null=True, default=dict)

    class Meta:
        ordering = ['-event_date']

    def __str__(self):
        return f"{self.event_type} on {self.event_date} for {self.stock.symbol}"
    

class StockPriceHistory(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='price_history', null=True, blank=True)
    datetime = models.DateTimeField()  # Use DateTimeField if storing hourly/minute data
    open_price = models.DecimalField(max_digits=12, decimal_places=2)
    close_price = models.DecimalField(max_digits=12, decimal_places=2)
    high = models.DecimalField(max_digits=12, decimal_places=2)
    low = models.DecimalField(max_digits=12, decimal_places=2)
    volume = models.BigIntegerField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    extra_fields = models.JSONField(blank=True, null=True, default=dict)

    class Meta:
        # unique_together = ('stock', 'datetime')  # prevent duplicate entries
        ordering = ['-datetime']

    def save(self, *args, **kwargs):
        self.extra_fields['price_change'] = float(self.close_price) - float(self.open_price or 0)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.stock.symbol} on {self.datetime}"


class Wallet(models.Model):
    user = models.OneToOneField("Users.Profile", on_delete=models.CASCADE, related_name='wallet', null=True, blank=True)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    extra_fields = models.JSONField(blank=True, null=True, default=dict)

    def __str__(self):
        return f"{self.user.username}'s Wallet"

class StockPortfolio(models.Model):
    user = models.ForeignKey("Users.Profile", on_delete=models.CASCADE, related_name='stock_portfolio', null=True, blank=True)
    total_holdings = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    total_value = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    extra_fields = models.JSONField(blank=True, null=True, default=dict)

    def __str__(self):
        """Returns a string representation of the StockPortfolio instance, 
        showing the associated user's username and indicating it's their stock portfolio."""
        return f"{self.user.username}'s Stock Portfolio"

class StockHolding(models.Model):
    portfolio = models.ForeignKey(StockPortfolio, on_delete=models.CASCADE, related_name='holdings', null=True, blank=True)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='holdings', null=True, blank=True)
    quantity = models.PositiveIntegerField()
    average_price = models.DecimalField(max_digits=12, decimal_places=2)
    purchase_date = models.DateField()
    current_value = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    sold_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    sold_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    extra_fields = models.JSONField(blank=True, null=True, default=dict)

    # class Meta:
    #     unique_together = ('portfolio', 'stock')

    def __str__(self):
        return f"{self.portfolio.user.username}'s Holding of {self.stock.symbol}"

    def save(self, *args, **kwargs):
        # First, save the holding to include it in related queries
        super().save(*args, **kwargs)

        # Recalculate current_value
        if self.stock and hasattr(self.stock, 'price'):
            self.current_value = self.quantity * self.stock.price
            super().save(update_fields=["current_value"])

        # Recalculate profit/loss
        if self.sold_price and self.sold_date:
            profit = (self.sold_price - self.average_price) * self.quantity
            self.extra_fields['profit_loss'] = float(profit)
        else:
            self.extra_fields['profit_loss'] = None
        super().save(update_fields=["extra_fields"])

        # Recalculate portfolio totals
        portfolio = self.portfolio
        holdings = portfolio.holdings.all()
        portfolio.total_value = sum(h.current_value or 0 for h in holdings)
        portfolio.total_holdings = sum(h.quantity for h in holdings)
        portfolio.save(update_fields=["total_value", "total_holdings"])

