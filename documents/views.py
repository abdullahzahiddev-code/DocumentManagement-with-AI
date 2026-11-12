import os
import threading
import logging
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.http import FileResponse, Http404
from django.views.generic import TemplateView
from django_filters.rest_framework import DjangoFilterBackend
from .models import Document, Category, Tag, DocumentSummary, ActivityLog
from .serializers import (DocumentListSerializer, DocumentDetailSerializer,
                           DocumentUploadSerializer, CategorySerializer, TagSerializer)
from .permissions import IsOwnerOrAdmin, CanAccessDocument
from .filters import DocumentFilter

logger = logging.getLogger('documents')


def log_activity(user, action, document=None, detail='', request=None):
    ip = None
    if request:
        x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = x_forwarded.split(',')[0] if x_forwarded else request.META.get('REMOTE_ADDR')
    ActivityLog.objects.create(user=user, document=document, action=action, detail=detail, ip_address=ip)


class DocumentListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend]
    filterset_class = DocumentFilter

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DocumentUploadSerializer
        return DocumentListSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_admin_user:
            return Document.objects.filter(is_deleted=False).select_related('owner', 'category').prefetch_related('tags')
        return Document.objects.filter(owner=user, is_deleted=False).select_related('owner', 'category').prefetch_related('tags')

    def perform_create(self, serializer):
        doc = serializer.save(owner=self.request.user)
        log_activity(self.request.user, 'upload', doc, f'Uploaded {doc.filename}', self.request)
        # Trigger processing in background thread
        from .processing import process_document
        t = threading.Thread(target=process_document, args=(doc.id,), daemon=True)
        t.start()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        doc = serializer.instance
        return Response(DocumentListSerializer(doc).data, status=status.HTTP_201_CREATED)


class DocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PATCH', 'PUT']:
            return DocumentUploadSerializer
        return DocumentDetailSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_admin_user:
            return Document.objects.filter(is_deleted=False)
        return Document.objects.filter(is_deleted=False)

    def get_object(self):
        doc = get_object_or_404(Document, pk=self.kwargs['pk'], is_deleted=False)
        if not doc.can_be_accessed_by(self.request.user):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('You do not have permission to access this document.')
        return doc

    def retrieve(self, request, *args, **kwargs):
        doc = self.get_object()
        log_activity(request.user, 'view', doc, '', request)
        return Response(DocumentDetailSerializer(doc).data)

    def update(self, request, *args, **kwargs):
        doc = self.get_object()
        if doc.owner != request.user and not request.user.is_admin_user:
            return Response({'error': 'Only the owner can edit this document.'}, status=403)
        partial = kwargs.pop('partial', False)
        serializer = DocumentDetailSerializer(doc, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        doc = self.get_object()
        if doc.owner != request.user and not request.user.is_admin_user:
            return Response({'error': 'Only the owner can delete this document.'}, status=403)
        doc.is_deleted = True
        doc.save()
        log_activity(request.user, 'delete', doc, '', request)
        return Response({'message': 'Document deleted.'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def document_download(request, pk):
    doc = get_object_or_404(Document, pk=pk, is_deleted=False)
    if not doc.can_be_accessed_by(request.user):
        return Response({'error': 'Access denied.'}, status=403)
    if not doc.file or not os.path.exists(doc.file.path):
        return Response({'error': 'File not found.'}, status=404)
    log_activity(request.user, 'download', doc, '', request)
    response = FileResponse(open(doc.file.path, 'rb'), as_attachment=True, filename=doc.filename)
    return response


@api_view(['GET'])
def document_text(request, pk):
    doc = get_object_or_404(Document, pk=pk, is_deleted=False)
    if not doc.can_be_accessed_by(request.user):
        return Response({'error': 'Access denied.'}, status=403)
    return Response({
        'document_id': doc.id,
        'title': doc.title,
        'extracted_text': doc.extracted_text,
        'processing_status': doc.processing_status,
    })


@api_view(['POST'])
def process_document_view(request, pk):
    doc = get_object_or_404(Document, pk=pk, is_deleted=False)
    if not doc.can_be_accessed_by(request.user):
        return Response({'error': 'Access denied.'}, status=403)
    if doc.owner != request.user and not request.user.is_admin_user:
        return Response({'error': 'Only the owner can reprocess this document.'}, status=403)
    doc.processing_status = Document.Status.PENDING
    doc.processing_error = ''
    doc.save()
    from .processing import process_document
    t = threading.Thread(target=process_document, args=(doc.id,), daemon=True)
    t.start()
    return Response({'message': 'Processing started.', 'status': doc.processing_status})


@api_view(['GET'])
def document_status(request, pk):
    doc = get_object_or_404(Document, pk=pk, is_deleted=False)
    if not doc.can_be_accessed_by(request.user):
        return Response({'error': 'Access denied.'}, status=403)
    return Response({
        'document_id': doc.id,
        'processing_status': doc.processing_status,
        'processing_error': doc.processing_error,
    })


class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]


class TagListView(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]


# Template views
class DocumentLibraryView(TemplateView):
    template_name = 'documents/library.html'

class DocumentUploadView(TemplateView):
    template_name = 'documents/upload.html'

class DocumentDetailPageView(TemplateView):
    template_name = 'documents/detail.html'
