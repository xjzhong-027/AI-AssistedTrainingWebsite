from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import path
from .models import BackupDatabase
from Backup.management.commands.backup_database import Command as BackupCommand
from Backup.management.commands.restore_database import Command as RestoreCommand

class Database(admin.ModelAdmin):
    # 用来显示在列表页的字段
    list_display = ('created_at', 'operation', 'status', 'backup_to',)
    list_filter = ('status', 'operation')
    search_fields = ('created_at', 'operation', 'status', 'backup_to',)
    list_display_links = None
    actions = ['delete_selected']

    def has_add_permission(self, request):
        return False  # 禁用新增按钮

    def has_change_permission(self, request, obj=None):
        return False  # 不允许修改备份记录

    # 设定自定义模板
    change_list_template = "backupdatabase_change_list.html"


    # 自定义URL备份数据库
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('backup_database/', self.admin_site.admin_view(self.backup_database), name='backup_database'),
            path('restore_database/', self.admin_site.admin_view(self.restore_database), name='restore_database'),
        ]
        return custom_urls + urls

    # 备份操作
    def backup_database(self, request):
        try:
            # 执行备份
            cmd = BackupCommand()
            cmd.handle()  # 执行备份命令
            self.message_user(request, "备份成功！")
        except Exception as e:
            self.message_user(request, f"备份失败: {str(e)}", level='error')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    # 恢复操作
    def restore_database(self, request):
        try:
            # 执行恢复
            cmd = RestoreCommand()
            cmd.handle()  # 执行恢复命令
            self.message_user(request, "备份恢复成功！")
        except Exception as e:
            self.message_user(request, f"备份恢复失败: {str(e)}", level='error')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))




admin.site.register(BackupDatabase, Database)
