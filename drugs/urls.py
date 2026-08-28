from django.urls import path
from . import views

app_name = 'drugs'

urlpatterns = [
    path('', views.drug_list_view, name='drug_list'),
    path('create/', views.drug_create_view, name='drug_create'),
    path('<int:pk>/', views.drug_detail_view, name='drug_detail'),

    path('<int:drug_pk>/batch/create/', views.batch_create_view, name='batch_create'),
    path('batch/<int:pk>/', views.batch_detail_view, name='batch_detail'),
    path('batch/<int:pk>/recall/', views.batch_recall_view, name='batch_recall'),

    path('search/', views.public_drug_search_view, name='public_search'),
]