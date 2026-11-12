from rest_framework import serializers
from django.conf import settings
from .models import Document, Category, Tag, DocumentSummary
from accounts.serializers import UserProfileSerializer
import os


class CategorySerializer(serializers.ModelSerializer):
    document_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'color', 'document_count', 'created_at']

    def get_document_count(self, obj):
        return obj.documents.filter(is_deleted=False).count()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class DocumentSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentSummary
        fields = ['id', 'summary_text', 'key_points', 'suggested_tags',
                  'suggested_category', 'is_ai_generated', 'model_used', 'generated_at']


class DocumentListSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    has_summary = serializers.SerializerMethodField()
    file_size_display = serializers.ReadOnlyField()

    class Meta:
        model = Document
        fields = ['id', 'title', 'description', 'file_type', 'file_size', 'file_size_display',
                  'owner_username', 'category_name', 'tags', 'access_level',
                  'processing_status', 'upload_date', 'updated_at', 'has_summary']

    def get_has_summary(self, obj):
        return hasattr(obj, 'summary') and obj.summary is not None


class DocumentDetailSerializer(serializers.ModelSerializer):
    owner = UserProfileSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True, required=False, allow_null=True
    )
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), source='tags', write_only=True, many=True, required=False
    )
    summary = DocumentSummarySerializer(read_only=True)
    file_size_display = serializers.ReadOnlyField()
    filename = serializers.ReadOnlyField()

    class Meta:
        model = Document
        fields = ['id', 'title', 'description', 'file', 'filename', 'file_type', 'file_size',
                  'file_size_display', 'owner', 'category', 'category_id', 'tags', 'tag_ids',
                  'access_level', 'extracted_text', 'processing_status', 'processing_error',
                  'upload_date', 'updated_at', 'summary']
        read_only_fields = ['file', 'file_type', 'file_size', 'owner', 'processing_status',
                            'processing_error', 'upload_date', 'updated_at']


class DocumentUploadSerializer(serializers.ModelSerializer):
    tag_names = serializers.ListField(child=serializers.CharField(), required=False, write_only=True)

    class Meta:
        model = Document
        fields = ['title', 'description', 'file', 'category', 'access_level', 'tag_names']

    def validate_file(self, value):
        allowed = [ext.lower() for ext in settings.ALLOWED_UPLOAD_EXTENSIONS]
        ext = os.path.splitext(value.name)[1].lstrip('.').lower()
        if ext not in allowed:
            raise serializers.ValidationError(f'File type .{ext} is not allowed. Allowed: {", ".join(allowed)}')
        max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError(f'File too large. Max size: {settings.MAX_UPLOAD_SIZE_MB} MB')
        return value

    def create(self, validated_data):
        tag_names = validated_data.pop('tag_names', [])
        file = validated_data['file']
        ext = os.path.splitext(file.name)[1].lstrip('.').lower()
        if ext == 'jpeg':
            ext = 'jpg'
        validated_data['file_type'] = ext
        validated_data['file_size'] = file.size
        document = Document.objects.create(**validated_data)
        for name in tag_names:
            tag, _ = Tag.objects.get_or_create(name=name.strip().lower())
            document.tags.add(tag)
        return document
