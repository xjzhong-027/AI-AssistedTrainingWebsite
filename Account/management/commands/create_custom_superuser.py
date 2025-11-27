from getpass import getpass

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from Account.models import Admins


class Command(BaseCommand):
    help = (
        "创建或重置超级管理员账号：\n"
        "1. Django 原生 User 表中创建/更新超级管理员（加密密码）\n"
        "2. Admins 表保存一份明文密码，供管理员端登录使用"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            type=str,
            help="可选：直接指定超级管理员的用户名（不提供则进入交互模式）",
        )
        parser.add_argument(
            "--password",
            type=str,
            help="可选：直接指定明文密码（不提供则进入交互模式）",
        )

    def handle(self, *args, **options):
        User = get_user_model()

        username = options.get("username")
        password = options.get("password")

        # 交互获取用户名
        if not username:
            username = input("请输入超级管理员用户名：").strip()
            while not username:
                username = input("用户名不能为空，请重新输入：").strip()

        # 交互获取密码
        if not password:
            password = getpass("请输入密码：")
            password_confirm = getpass("请再次输入密码确认：")
            while not password or password != password_confirm:
                if not password:
                    self.stderr.write("密码不能为空，请重新输入。")
                else:
                    self.stderr.write("两次输入的密码不一致，请重新输入。")
                password = getpass("请输入密码：")
                password_confirm = getpass("请再次输入密码确认：")

        # 如果用户已存在，则执行重置逻辑；否则创建新的超级管理员
        user, created = User.objects.get_or_create(username=username)

        user.email = user.email or ""
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        admin_values = {
            "password": password,  # 按需求以明文形式保存
            "user": user,
        }
        Admins.objects.update_or_create(username=username, defaults=admin_values)

        if created:
            self.stdout.write(self.style.SUCCESS(f"已创建新的超级管理员 '{username}'。"))
        else:
            self.stdout.write(self.style.SUCCESS(f"已重置超级管理员 '{username}' 的密码。"))

        self.stdout.write(self.style.SUCCESS("现在可以使用该用户名和明文密码从管理员端登录。"))