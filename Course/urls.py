from django.urls import path,include
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings

handler404 = 'utils.views.custom_404'
handler500 = 'utils.views.custom_500'

urlpatterns = [
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
