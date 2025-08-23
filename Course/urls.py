from django.urls import path,include
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings

handler404 = 'utils.views.custom_404'
handler500 = 'utils.views.custom_500'

def trigger_error(request):
    division_by_zero = 1 / 0
    return division_by_zero

urlpatterns = [
	path('sentry-debug/', trigger_error),
	path('admin/', admin.site.urls),
	path('accounts/', include('Users.urls')),
	path('stock/', include('Stock.urls')),
	path('course/', include('Courseapp.urls')),
	path('tiers/', include('Tiers.urls')),
	path('rewards/', include('Rewards.urls')),
	path('', include('utils.urls')),
]
if settings.DEBUG:
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
