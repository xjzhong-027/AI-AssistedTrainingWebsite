import django_filters
from django.db.models import Q
from .models import Post

class PostFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    content = django_filters.CharFilter(lookup_expr='icontains')
    name = django_filters.CharFilter(method='filter_name')
    created_at__gte = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_at__lte = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Post
        fields = ['title', 'content', 'name', 'created_at__gte', 'created_at__lte']

    def filter_name(self, queryset, name, value):
        return queryset.filter(
            Q(teacher__name__icontains=value) | Q(student__name__icontains=value)
        )