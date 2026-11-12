from django.db import models
from django.conf import settings
import os


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#3B82F6')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


def document_upload_path(instance, filename):
    return f'documents/{instance.owner.username}/{filename}'


class Document(models.Model):
    class FileType(models.TextChoices):
        PDF = 'pdf', 'PDF'
        DOCX = 'docx', 'Word Document'
        TXT = 'txt', 'Text File'
        PNG = 'png', 'PNG Image'
        JPG = 'jpg', 'JPEG Image'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'

    class AccessLevel(models.TextChoices):
        PRIVATE = 'private', 'Private'
        DEPARTMENT = 'department', 'Department'
        PUBLIC = 'public', 'Public'

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to=document_upload_path)
    file_type = models.CharField(max_length=10, choices=FileType.choices)
    file_size = models.PositiveBigIntegerField(default=0)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='documents')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='documents')
    tags = models.ManyToManyField(Tag, blank=True, related_name='documents')
    access_level = models.CharField(max_length=20, choices=AccessLevel.choices, default=AccessLevel.PRIVATE)
    extracted_text = models.TextField(blank=True)
    processing_status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    processing_error = models.TextField(blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['-upload_date']
        indexes = [
            models.Index(fields=['owner', 'upload_date']),
            models.Index(fields=['processing_status']),
            models.Index(fields=['file_type']),
        ]

    def __str__(self):
        return self.title

    @property
    def filename(self):
        return os.path.basename(self.file.name) if self.file else ''

    @property
    def file_size_display(self):
        size = self.file_size
        if size < 1024:
            return f'{size} B'
        elif size < 1024 * 1024:
            return f'{size / 1024:.1f} KB'
        return f'{size / (1024 * 1024):.1f} MB'

    def can_be_accessed_by(self, user):
        if user.is_admin_user:
            return True
        if self.owner == user:
            return True
        if self.access_level == self.AccessLevel.PUBLIC:
            return True
        if self.access_level == self.AccessLevel.DEPARTMENT:
            return user.department and user.department == self.owner.department
        return False


class DocumentSummary(models.Model):
    document = models.OneToOneField(Document, on_delete=models.CASCADE, related_name='summary')
    summary_text = models.TextField()
    key_points = models.JSONField(default=list)
    suggested_tags = models.JSONField(default=list)
    suggested_category = models.CharField(max_length=100, blank=True)
    is_ai_generated = models.BooleanField(default=True)
    model_used = models.CharField(max_length=100, blank=True)
    generated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Summary for: {self.document.title}'


class ActivityLog(models.Model):
    class ActionType(models.TextChoices):
        UPLOAD = 'upload', 'Upload'
        VIEW = 'view', 'View'
        DOWNLOAD = 'download', 'Download'
        DELETE = 'delete', 'Delete'
        SEARCH = 'search', 'Search'
        SUMMARIZE = 'summarize', 'Summarize'
        OCR = 'ocr', 'OCR'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='activities')
    document = models.ForeignKey(Document, on_delete=models.SET_NULL, null=True, blank=True, related_name='activities')
    action = models.CharField(max_length=20, choices=ActionType.choices)
    detail = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} {self.action} at {self.created_at}'
