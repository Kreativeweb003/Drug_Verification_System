from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),

    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/officer/', views.officer_dashboard, name='officer_dashboard'),
    path('dashboard/manufacturer/', views.manufacturer_dashboard, name='manufacturer_dashboard'),
    path('dashboard/consumer/', views.consumer_dashboard, name='consumer_dashboard'),

    path('approve/<int:user_id>/', views.approve_user_view, name='approve_user'),
]