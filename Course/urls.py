from django.urls import path,include
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
	path('admin/', admin.site.urls),
	path('', include('Users.urls')),
	path('', include('Stock.urls')),
	path('', include('Courseapp.urls')),
	path('', include('Tiers.urls')),
	path('', include('Rewards.urls')),
	path('', include('utils.urls')),
]
if settings.DEBUG:
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
