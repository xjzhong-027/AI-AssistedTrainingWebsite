# Generated manually for AI 提示请求记录

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('AI_module', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HintRequestLog',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('level', models.PositiveSmallIntegerField(choices=[(1, '轻提示'), (2, '方向提示'), (3, '详细解释')], verbose_name='提示级别')),
                ('hint_content', models.TextField(blank=True, default='', verbose_name='返回的提示内容')),
                ('request_time', models.DateTimeField(auto_now_add=True, verbose_name='请求时间')),
                ('context', models.JSONField(default=dict, help_text='练习/页面等 {"practice_id": 1, "page_id": 2}', verbose_name='上下文')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hint_request_logs', to='Account.students', verbose_name='学生')),
                ('sub_question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hint_request_logs', to='ELW.subquestion', verbose_name='题目')),
            ],
            options={
                'verbose_name': '提示请求记录',
                'verbose_name_plural': '提示请求记录',
                'db_table': 'ai_hint_request_log',
                'ordering': ['-request_time'],
                'indexes': [
                    models.Index(fields=['student'], name='ai_hint_req_student_idx'),
                    models.Index(fields=['sub_question'], name='ai_hint_req_sub_que_idx'),
                    models.Index(fields=['request_time'], name='ai_hint_req_request_idx'),
                ],
            },
        ),
    ]