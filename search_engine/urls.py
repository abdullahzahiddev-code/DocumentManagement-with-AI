from django.urls import path
from . import views

urlpatterns = [
    path('api/search/', views.search_documents, name='api-search'),
    path('search/', views.SearchPageView.as_view(), name='search'),
]
