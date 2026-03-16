from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('AI_module', '0002_add_hint_request_log'),
        ('ELW', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AIQuestionGenerationRecord',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('question_type', models.CharField(max_length=20, verbose_name='题目类型')),
                ('difficulty', models.CharField(default='medium', max_length=20, verbose_name='难度')),
                ('generated_questions', models.JSONField(default=list, verbose_name='生成的题目')),
                ('final_questions', models.JSONField(default=list, verbose_name='最终确定的题目')),
                ('is_applied', models.BooleanField(default=False, verbose_name='是否已应用到题库')),
                ('ai_model', models.CharField(default='VolcEngine', max_length=50, verbose_name='AI模型')),
                ('status', models.CharField(default='pending', max_length=20, verbose_name='状态')),
                ('message', models.TextField(default='', verbose_name='消息')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('material', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ai_generation_records', to='ELW.mediamaterial', verbose_name='素材')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ai_generation_records', to=settings.AUTH_USER_MODEL, verbose_name='教师')),
            ],
            options={
                'db_table': 'ai_question_generation_record',
                'verbose_name': 'AI出题记录',
                'verbose_name_plural': 'AI出题记录',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='AIQuestionConversationHistory',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('role', models.CharField(max_length=20, verbose_name='角色')),
                ('content', models.TextField(verbose_name='消息内容')),
                ('context', models.JSONField(default=dict, verbose_name='上下文信息')),
                ('message_time', models.DateTimeField(auto_now_add=True, verbose_name='消息时间')),
                ('generation_record', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conversations', to='AI_module.aiquestiongenerationrecord', verbose_name='出题记录')),
            ],
            options={
                'db_table': 'ai_question_conversation_history',
                'verbose_name': 'AI出题对话历史',
                'verbose_name_plural': 'AI出题对话历史',
                'ordering': ['message_time'],
            },
        ),
    ]

