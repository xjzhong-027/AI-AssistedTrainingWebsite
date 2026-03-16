from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AI_module', '0003_add_question_generation_models'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='aiquestionconversationhistory',
            index=models.Index(fields=['generation_record'], name='ai_question_generat_886bb3_idx'),
        ),
        migrations.AddIndex(
            model_name='aiquestionconversationhistory',
            index=models.Index(fields=['message_time'], name='ai_question_message_48fe2a_idx'),
        ),
        migrations.AddIndex(
            model_name='aiquestiongenerationrecord',
            index=models.Index(fields=['material'], name='ai_question_materia_b5d49c_idx'),
        ),
        migrations.AddIndex(
            model_name='aiquestiongenerationrecord',
            index=models.Index(fields=['teacher'], name='ai_question_teacher_c5fd56_idx'),
        ),
        migrations.AddIndex(
            model_name='aiquestiongenerationrecord',
            index=models.Index(fields=['status'], name='ai_question_status_46c8f9_idx'),
        ),
        migrations.AddIndex(
            model_name='aiquestiongenerationrecord',
            index=models.Index(fields=['created_at'], name='ai_question_created_06acb6_idx'),
        ),
    ]

