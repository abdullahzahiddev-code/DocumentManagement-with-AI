import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from documents.models import Document, DocumentSummary, Tag, ActivityLog
from .ai_service import generate_summary_with_ai, generate_tags_with_ai

logger = logging.getLogger('ai_assistant')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def summarize_document(request, pk):
    doc = get_object_or_404(Document, pk=pk, is_deleted=False)
    if not doc.can_be_accessed_by(request.user):
        return Response({'error': 'Access denied.'}, status=403)

    if not doc.extracted_text.strip():
        return Response({'error': 'Document has no extracted text. Process it first.'}, status=400)

    force_regenerate = request.data.get('force_regenerate', False)
    if not force_regenerate and hasattr(doc, 'summary') and doc.summary:
        return Response({
            'message': 'Summary already exists. Use force_regenerate=true to regenerate.',
            'summary': {
                'summary_text': doc.summary.summary_text,
                'key_points': doc.summary.key_points,
                'suggested_tags': doc.summary.suggested_tags,
                'suggested_category': doc.summary.suggested_category,
                'is_ai_generated': doc.summary.is_ai_generated,
                'model_used': doc.summary.model_used,
                'generated_at': doc.summary.generated_at.isoformat(),
            }
        })

    result = generate_summary_with_ai(doc.extracted_text, doc.title)
    summary_obj, _ = DocumentSummary.objects.update_or_create(
        document=doc,
        defaults={
            'summary_text': result['summary'],
            'key_points': result['key_points'],
            'suggested_tags': result['suggested_tags'],
            'suggested_category': result.get('suggested_category', ''),
            'is_ai_generated': result['is_ai_generated'],
            'model_used': result.get('model_used', ''),
        }
    )
    ActivityLog.objects.create(user=request.user, document=doc, action='summarize',
                               detail=f"{'AI' if result['is_ai_generated'] else 'Fallback'} summary generated")
    return Response({
        'message': 'Summary generated.',
        'is_ai_generated': result['is_ai_generated'],
        'fallback_reason': result.get('fallback_reason', ''),
        'summary': {
            'summary_text': summary_obj.summary_text,
            'key_points': summary_obj.key_points,
            'suggested_tags': summary_obj.suggested_tags,
            'suggested_category': summary_obj.suggested_category,
            'is_ai_generated': summary_obj.is_ai_generated,
            'model_used': summary_obj.model_used,
            'generated_at': summary_obj.generated_at.isoformat(),
        }
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_summary(request, pk):
    doc = get_object_or_404(Document, pk=pk, is_deleted=False)
    if not doc.can_be_accessed_by(request.user):
        return Response({'error': 'Access denied.'}, status=403)
    if not hasattr(doc, 'summary') or not doc.summary:
        return Response({'error': 'No summary available. Generate one first.'}, status=404)
    s = doc.summary
    return Response({
        'summary_text': s.summary_text,
        'key_points': s.key_points,
        'suggested_tags': s.suggested_tags,
        'suggested_category': s.suggested_category,
        'is_ai_generated': s.is_ai_generated,
        'model_used': s.model_used,
        'generated_at': s.generated_at.isoformat(),
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_tags(request, pk):
    doc = get_object_or_404(Document, pk=pk, is_deleted=False)
    if not doc.can_be_accessed_by(request.user):
        return Response({'error': 'Access denied.'}, status=403)
    if not doc.extracted_text.strip():
        return Response({'error': 'Document has no extracted text. Process it first.'}, status=400)

    result = generate_tags_with_ai(doc.extracted_text, doc.title)
    suggested = result.get('tags', [])
    # Apply tags to document
    for tag_name in suggested[:10]:
        tag, _ = Tag.objects.get_or_create(name=tag_name.strip().lower())
        doc.tags.add(tag)

    return Response({
        'message': 'Tags generated and applied.',
        'tags': suggested,
        'is_ai_generated': result.get('is_ai_generated', False),
    })
