from django.urls import path
from . import views

app_name = 'verification'

urlpatterns = [
    path('history/', views.scan_history_view, name='scan_history'),
    path('flags/', views.flag_list_view, name='flag_list'),
    path('flags/<int:pk>/resolve/', views.flag_resolve_view, name='flag_resolve'),
]