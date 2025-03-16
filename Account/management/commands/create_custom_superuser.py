from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.contrib.auth.management.commands import createsuperuser
from Account.models import Admins


class Command(createsuperuser.Command):
    def handle(self, *args, **options):
        # 创建超级管理员
        super().handle(*args, **options)

        # 在创建超级管理员后，插入自定义数据表
        username = options.get('username')
        password = options.get('password')

        if username:
            try:
                user = User.objects.get(username=username)
                Admins.objects.create(
                    username=username,
                    password=password,
                    user=user
                )
                self.stdout.write(self.style.SUCCESS(f"Custom user data added for {username}"))
            except ObjectDoesNotExist:
                self.stdout.write(self.style.ERROR(f"User with username '{username}' not found."))