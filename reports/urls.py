from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('list/', views.report_list_view, name='report_list'),
    path('generate/counterfeit/', views.generate_counterfeit_report_view, name='generate_counterfeit'),
    path('generate/compliance/', views.generate_compliance_report_view, name='generate_compliance'),
    path('download/<int:pk>/', views.download_report_view, name='download_report'),
]

