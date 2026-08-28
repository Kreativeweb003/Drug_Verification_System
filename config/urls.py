from django.contrib import admin
from django.urls import path, include
from verification.views import verify_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', verify_view, name='home'),

    path('accounts/', include('accounts.urls')),
    path('manufacturers/', include('manufacturers.urls')),
    path('drugs/', include('drugs.urls')),
    path('verification/', include('verification.urls')),
    path('reports/', include('reports.urls')),
]

