from django.contrib.admin import SimpleListFilter
from django.utils import timezone
from datetime import timedelta

class LogEntryTimeFilter(SimpleListFilter):
    title = '日志时间'
    parameter_name = 'created_at'

    def lookups(self, request, model_admin):
        return (
            ('last_week', '最近一周'),
            ('last_30_days', '最近30天'),
            ('older_than_30', '30天前'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'last_week':
            last_week = timezone.now() - timedelta(weeks=1)
            return queryset.filter(created_at__gte=last_week)
        elif value == 'last_30_days':
            last_30_days = timezone.now() - timedelta(days=30)
            return queryset.filter(created_at__gte=last_30_days)
        elif value == 'older_than_30':
            older_than_30 = timezone.now() - timedelta(days=30)
            return queryset.filter(created_at__lt=older_than_30)
        return queryset