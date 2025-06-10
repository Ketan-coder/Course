from django.contrib import admin
from .models import *
# Register your models here.
@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'symbol')
    search_fields = ('name', 'code', 'symbol')

@admin.register(PhoneNoPrefix)
class PhoneNoPrefixAdmin(admin.ModelAdmin):
    list_display = ('country_code', 'country_name')
    search_fields = ('country_code', 'country_name')

@admin.register(FeedBack)
class FeedBackAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'message')
    search_fields = ('name', 'email', 'message')