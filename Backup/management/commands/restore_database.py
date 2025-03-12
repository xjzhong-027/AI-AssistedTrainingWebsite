from django.core.management.base import BaseCommand
import subprocess
from Backup.models import BackupDatabase


class Command(BaseCommand):
    help = 'Restore the database from a backup file'

    def handle(self, *args, **kwargs):
        # 创建一个恢复记录
        restore = BackupDatabase.objects.create(operation='restore', status='in_progress')
        try:
            backups = BackupDatabase.objects.filter(operation='backup')
            backups_with_backup_to = backups.filter(backup_to__isnull=False)
            latest_backup = backups_with_backup_to.order_by('-created_at').first()
            if latest_backup:
                # 获取备份文件路径
                backup_file_path = latest_backup.backup_to

                user = 'root'  # MySQL 用户名
                password = '123456'  # MySQL 密码
                database_name = 'day1130'  # 将备份文件恢复到新的数据库中

                # 恢复操作：使用 mysql 命令恢复数据库
                restore_cmd = [
                    'mysql',  # MySQL 命令
                    '-u', user,  # 用户名
                    '-p' + password,  # 密码
                    database_name  # 目标数据库
                ]

                # 执行恢复命令
                with open(backup_file_path, 'r') as backup_file:
                    subprocess.run(restore_cmd, stdin=backup_file, check=True)

                self.stdout.write(self.style.SUCCESS('Database restored successfully'))

                # 如果恢复成功，更新 Backup 模型中的信息
                restore.backup_to = backup_file_path  # 保存备份文件路径
                restore.status = 'completed'  # 更新状态为完成
                restore.save()
            else:
                self.stdout.write(self.style.ERROR('No backup file found to restore'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error restoring database: {e}'))