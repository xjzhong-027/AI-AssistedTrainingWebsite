import os
from django.conf import settings
from django.core.management.base import BaseCommand
import subprocess
from datetime import datetime

from Backup.models import BackupDatabase


class Command(BaseCommand):
    help = 'Backup the MySQL database'

    def handle(self, *args, **kwargs):
        # 创建一个备份记录
        backup = BackupDatabase.objects.create(operation='backup', status='in_progress')
        try:
            # 获取项目根目录
            project_root = settings.BASE_DIR  # BASE_DIR 是 Django 自动配置的项目根目录路径

            # 构造备份文件的路径 admin_system/backup/backup_databases/
            backup_dir = os.path.join(project_root, 'backup', 'backup_databases')

            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)  # 如果目录不存在，创建该目录

            # 获取当前时间，用于备份文件名
            now = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(backup_dir, f'db_backup_{now}.sql')

            # 配置 MySQL 备份命令
            mysqldump_cmd = [
                'mysqldump',
                '-u', 'root',  # MySQL 用户名
                '-p123456',  # MySQL 密码
                'day0425',  # 要备份的数据库名称
                '--result-file=' + backup_file,  # 备份文件路径
                '--no-tablespaces',  # 避免备份表空间
                '--single-transaction',  # 确保备份一致性
            ]

            # 执行备份命令
            result = subprocess.run(mysqldump_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # 如果备份成功，更新 Backup 模型中的信息
            backup.backup_to = backup_file  # 保存备份文件路径
            backup.status = 'completed'  # 更新状态为完成
            backup.save()

            # 打印成功信息
            self.stdout.write(self.style.SUCCESS(f'Backup completed successfully! Backup file: {backup_file}'))


        except subprocess.CalledProcessError as e:
            # 处理备份失败的情况
            backup.status = 'failed'
            backup.save()
            self.stdout.write(self.style.ERROR(f'Backup failed: {e.stderr.decode()}'))