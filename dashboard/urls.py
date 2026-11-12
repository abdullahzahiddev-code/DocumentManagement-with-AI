from django.urls import path
from . import views

urlpatterns = [
    path('api/dashboard/stats/', views.dashboard_stats, name='api-dashboard-stats'),
    path('api/dashboard/recent-documents/', views.recent_documents, name='api-dashboard-recent'),
    path('dashboard/', views.DashboardPageView.as_view(), name='dashboard'),
    path('', views.DashboardPageView.as_view(), name='home'),
]
