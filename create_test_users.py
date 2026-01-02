"""
创建测试用户数据的脚本
在 Django Shell 中运行：python manage.py shell < create_test_users.py
或者直接在 Django Shell 中逐行执行
"""

from django.contrib.auth.models import User
from Account.models import Students, Teachers, Admins, Class, Course

# 1. 创建课程
course, created = Course.objects.get_or_create(
    year=2024,
    grade='1',
    semester='上',
    defaults={}
)
print(f"课程: {course} (created: {created})")

# 2. 创建教师
teacher, created = Teachers.objects.get_or_create(
    username='teacher001',
    defaults={
        'name': '王老师',
        'password': 'teacher123'
    }
)
print(f"教师: {teacher} (created: {created})")

# 创建教师对应的 Django User（如果不存在）
teacher_user, created = User.objects.get_or_create(
    username='teacher001',
    defaults={'is_active': True}
)
if not teacher.user:
    teacher.user = teacher_user
    teacher.save()
print(f"教师 User: {teacher_user} (created: {created})")

# 3. 创建班级
class_instance, created = Class.objects.get_or_create(
    course=course,
    teacher=teacher,
    defaults={
        'class_name': '英语听力1班',
        'start_date': '2024-01-01',
        'week': 1,
        'start_time': '08:00:00',
        'end_time': '10:00:00'
    }
)
print(f"班级: {class_instance} (created: {created})")

# 4. 创建学生 1
student1_user, created = User.objects.get_or_create(
    username='student001',
    defaults={'is_active': True}
)
student1, created = Students.objects.get_or_create(
    username='student001',
    defaults={
        'name': '张三',
        'password': 'student123',
        'class_instance': class_instance,
        'seat_number': '1',
        'user': student1_user
    }
)
if not student1.user:
    student1.user = student1_user
    student1.save()
print(f"学生1: {student1} (created: {created})")

# 5. 创建学生 2
student2_user, created = User.objects.get_or_create(
    username='student002',
    defaults={'is_active': True}
)
student2, created = Students.objects.get_or_create(
    username='student002',
    defaults={
        'name': '李四',
        'password': 'student123',
        'class_instance': class_instance,
        'seat_number': '2',
        'user': student2_user
    }
)
if not student2.user:
    student2.user = student2_user
    student2.save()
print(f"学生2: {student2} (created: {created})")

# 6. 创建管理员（可选）
admin, created = Admins.objects.get_or_create(
    username='admin001',
    defaults={
        'password': 'admin123'
    }
)
admin_user, created = User.objects.get_or_create(
    username='admin001',
    defaults={'is_active': True, 'is_staff': True, 'is_superuser': True}
)
if not admin.user:
    admin.user = admin_user
    admin.save()
print(f"管理员: {admin} (created: {created})")

print("\n✅ 测试用户创建完成！")
print("\n可用账号：")
print("  学生: student001 / student123")
print("  学生: student002 / student123")
print("  教师: teacher001 / teacher123")
print("  管理员: admin001 / admin123")







