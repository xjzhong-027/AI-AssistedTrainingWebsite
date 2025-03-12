from django.contrib import admin
from .models import LogEntry
from .filters import LogEntryTimeFilter

def mark_as_read(modeladmin, request, queryset):
    queryset.update(status='read')
mark_as_read.short_description = "将选中的日志标记为已读"

def mark_as_unread(modeladmin, request, queryset):
    queryset.update(status='unread')
mark_as_unread.short_description = "将选中的日志标记为未读"

class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'log_type', 'module', 'operation_time', 'message', 'status')
    search_fields = ('user__username', 'message')
    list_filter = (LogEntryTimeFilter, 'log_type', 'status')
    readonly_fields = ('user', 'log_type', 'operation_time', 'module', 'message')

    actions = [mark_as_read, mark_as_unread]

    def has_add_permission(self, request):
        return False  # 禁用手动新增日志


admin.site.register(LogEntry, LogEntryAdmin)