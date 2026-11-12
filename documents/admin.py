from django.contrib import admin
from .models import Document, Category, Tag, DocumentSummary, ActivityLog


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'file_type', 'processing_status', 'upload_date']
    list_filter = ['file_type', 'processing_status', 'category']
    search_fields = ['title', 'description', 'extracted_text']
    readonly_fields = ['file_size', 'file_type', 'upload_date', 'updated_at']


@admin.register(DocumentSummary)
class DocumentSummaryAdmin(admin.ModelAdmin):
    list_display = ['document', 'is_ai_generated', 'model_used', 'generated_at']


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'document', 'created_at']
    list_filter = ['action']
    readonly_fields = ['created_at']
