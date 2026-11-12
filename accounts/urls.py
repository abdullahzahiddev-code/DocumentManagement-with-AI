from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # API endpoints
    path('api/auth/register/', views.RegisterView.as_view(), name='api-register'),
    path('api/auth/login/', views.login_view, name='api-login'),
    path('api/auth/logout/', views.logout_view, name='api-logout'),
    path('api/auth/me/', views.me_view, name='api-me'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('api/users/', views.UserListView.as_view(), name='api-users'),
    # Template pages
    path('login/', views.LoginPageView.as_view(), name='login'),
    path('register/', views.RegisterPageView.as_view(), name='register'),
    path('profile/', views.ProfilePageView.as_view(), name='profile'),
    path('users/', views.UserManagementPageView.as_view(), name='user-management'),
]
