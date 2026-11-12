from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from rest_framework.response import Response
from django.db.models import Q
from django.views.generic import TemplateView
from documents.models import Document
from documents.serializers import DocumentListSerializer
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def search_documents(request):
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category')
    file_type = request.GET.get('file_type')
    sort = request.GET.get('sort', '-upload_date')
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))

    user = request.user
    if user.is_admin_user:
        qs = Document.objects.filter(is_deleted=False)
    else:
        qs = Document.objects.filter(is_deleted=False, owner=user)

    if query:
        qs = qs.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(extracted_text__icontains=query) |
            Q(tags__name__icontains=query) |
            Q(summary__summary_text__icontains=query)
        ).distinct()

    if category_id:
        qs = qs.filter(category__id=category_id)
    if file_type:
        qs = qs.filter(file_type=file_type)

    valid_sorts = ['upload_date', '-upload_date', 'title', '-title', 'file_size', '-file_size']
    if sort not in valid_sorts:
        sort = '-upload_date'
    qs = qs.order_by(sort).select_related('owner', 'category').prefetch_related('tags')

    total = qs.count()
    start = (page - 1) * page_size
    docs = qs[start:start + page_size]

    results = []
    for doc in docs:
        data = DocumentListSerializer(doc).data
        if query and doc.extracted_text:
            idx = doc.extracted_text.lower().find(query.lower())
            if idx >= 0:
                snippet_start = max(0, idx - 100)
                snippet_end = min(len(doc.extracted_text), idx + 200)
                data['snippet'] = '...' + doc.extracted_text[snippet_start:snippet_end] + '...'
            else:
                data['snippet'] = doc.description[:200] if doc.description else ''
        else:
            data['snippet'] = doc.description[:200] if doc.description else ''
        results.append(data)

    # Log the search activity
    from documents.models import ActivityLog
    ActivityLog.objects.create(user=user, action='search', detail=query[:500] if query else '')

    return Response({
        'query': query,
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size,
        'results': results,
    })


class SearchPageView(TemplateView):
    template_name = 'search_engine/search.html'
