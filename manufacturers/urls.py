from django.urls import path
from . import views

app_name = 'manufacturers'

urlpatterns = [
    path('profile/create/', views.create_profile_view, name='create_profile'),
    path('profile/', views.profile_detail_view, name='profile_detail'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),

    path('list/', views.manufacturer_list_view, name='manufacturer_list'),
    path('review/<int:pk>/', views.manufacturer_review_view, name='manufacturer_review'),
]