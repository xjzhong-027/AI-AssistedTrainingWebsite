# Generated migration for LoginInfo model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LoginInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=20, verbose_name='用户名')),
                ('week', models.IntegerField(default=0, verbose_name='周次')),
                ('action', models.CharField(max_length=20, verbose_name='操作类型')),
                ('action_time', models.DateTimeField(verbose_name='操作时间')),
                ('last_active_time', models.CharField(max_length=50, verbose_name='最后活跃时间')),
                ('device_info', models.CharField(blank=True, default='', max_length=500, verbose_name='设备信息')),
            ],
            options={
                'verbose_name_plural': '登录记录',
                'ordering': ['-action_time'],
            },
        ),
    ]

