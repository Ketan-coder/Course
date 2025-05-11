from django.contrib import admin
from .models import Voucher, VoucherUsage
# Register your models here.
admin.site.register(Voucher)
admin.site.register(VoucherUsage)