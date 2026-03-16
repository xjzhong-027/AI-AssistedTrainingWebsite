"""
Common 模块 Admin 配置。
"""
from django.contrib import admin
from .models import StudentBehaviorWeeklyScore


@admin.register(StudentBehaviorWeeklyScore)
class StudentBehaviorWeeklyScoreAdmin(admin.ModelAdmin):
    list_display = ('student', 'period_start', 'period_end', 'F_score', 'P_score', 'growth_bonus', 'updated_at')
    list_filter = ('period_start',)
    search_fields = ('student__name', 'student__username')
    ordering = ('-period_start', '-F_score')
