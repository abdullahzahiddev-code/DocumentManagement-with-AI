from django.urls import path
from . import views

urlpatterns = [
    # API endpoints
    path('api/documents/', views.DocumentListCreateView.as_view(), name='api-documents'),
    path('api/documents/<int:pk>/', views.DocumentDetailView.as_view(), name='api-document-detail'),
    path('api/documents/<int:pk>/download/', views.document_download, name='api-document-download'),
    path('api/documents/<int:pk>/text/', views.document_text, name='api-document-text'),
    path('api/documents/<int:pk>/process/', views.process_document_view, name='api-document-process'),
    path('api/documents/<int:pk>/status/', views.document_status, name='api-document-status'),
    path('api/categories/', views.CategoryListCreateView.as_view(), name='api-categories'),
    path('api/tags/', views.TagListView.as_view(), name='api-tags'),
    # Template pages
    path('documents/', views.DocumentLibraryView.as_view(), name='document-library'),
    path('documents/upload/', views.DocumentUploadView.as_view(), name='document-upload'),
    path('documents/<int:pk>/', views.DocumentDetailPageView.as_view(), name='document-detail'),
]
