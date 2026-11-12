from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from rest_framework.response import Response
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from django.views.generic import TemplateView
from documents.models import Document, DocumentSummary, ActivityLog
from accounts.models import User


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_stats(request):
    user = request.user
    now = timezone.now()
    thirty_ago = now - timedelta(days=30)

    if user.is_admin_user:
        base_qs = Document.objects.filter(is_deleted=False)
    else:
        base_qs = Document.objects.filter(is_deleted=False, owner=user)

    total_docs     = base_qs.count()
    my_docs        = Document.objects.filter(is_deleted=False, owner=user).count()
    recent_30d     = base_qs.filter(upload_date__gte=thirty_ago).count()
    pending        = base_qs.filter(processing_status='pending').count()
    processing     = base_qs.filter(processing_status='processing').count()
    completed      = base_qs.filter(processing_status='completed').count()
    failed         = base_qs.filter(processing_status='failed').count()
    ai_summaries   = DocumentSummary.objects.filter(document__in=base_qs, is_ai_generated=True).count()

    by_category = list(
        base_qs.values('category__name', 'category__color')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    by_type = list(
        base_qs.values('file_type').annotate(count=Count('id')).order_by('-count')
    )

    return Response({
        'total_documents': total_docs,
        'my_documents': my_docs,
        'recent_uploads_30d': recent_30d,
        'ai_summaries_generated': ai_summaries,
        'processing_status': {
            'pending': pending,
            'processing': processing,
            'completed': completed,
            'failed': failed,
        },
        'documents_by_category': by_category,
        'documents_by_type': by_type,
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def recent_documents(request):
    from documents.serializers import DocumentListSerializer
    user = request.user
    limit = min(int(request.GET.get('limit', 10)), 50)
    if user.is_admin_user:
        docs = Document.objects.filter(is_deleted=False).order_by('-upload_date')[:limit]
    else:
        docs = Document.objects.filter(is_deleted=False, owner=user).order_by('-upload_date')[:limit]
    return Response(DocumentListSerializer(docs, many=True).data)


class DashboardPageView(TemplateView):
    template_name = 'dashboard/dashboard.html'
