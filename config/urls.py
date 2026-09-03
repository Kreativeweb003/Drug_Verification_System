from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from verification.views import verify_view
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', verify_view, name='home'),

    path('accounts/', include('accounts.urls')),
    path('manufacturers/', include('manufacturers.urls')),
    path('drugs/', include('drugs.urls')),
    path('verification/', include('verification.urls')),
    path('reports/', include('reports.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
