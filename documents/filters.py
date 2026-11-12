import django_filters
from .models import Document


class DocumentFilter(django_filters.FilterSet):
    category = django_filters.NumberFilter(field_name='category__id')
    file_type = django_filters.CharFilter(field_name='file_type')
    upload_date_after = django_filters.DateFilter(field_name='upload_date', lookup_expr='gte')
    upload_date_before = django_filters.DateFilter(field_name='upload_date', lookup_expr='lte')
    tags = django_filters.CharFilter(method='filter_tags')
    status = django_filters.CharFilter(field_name='processing_status')

    class Meta:
        model = Document
        fields = ['category', 'file_type', 'status']

    def filter_tags(self, queryset, name, value):
        tag_names = [t.strip() for t in value.split(',')]
        return queryset.filter(tags__name__in=tag_names).distinct()
