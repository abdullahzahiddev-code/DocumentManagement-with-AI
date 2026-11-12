from django.urls import path
from . import views

urlpatterns = [
    path('api/documents/<int:pk>/summarize/', views.summarize_document, name='api-summarize'),
    path('api/documents/<int:pk>/summary/', views.get_summary, name='api-get-summary'),
    path('api/documents/<int:pk>/generate-tags/', views.generate_tags, name='api-generate-tags'),
]
