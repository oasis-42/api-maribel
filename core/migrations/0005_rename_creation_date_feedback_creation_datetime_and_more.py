# Generated by Django 5.0.6 on 2024-06-24 03:00

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_theme_title'),
    ]

    operations = [
        migrations.RenameField(
            model_name='feedback',
            old_name='creation_date',
            new_name='creation_datetime',
        ),
        migrations.RenameField(
            model_name='feedback',
            old_name='feedback',
            new_name='feedback_id',
        ),
        migrations.RenameField(
            model_name='motivationaltext',
            old_name='motivational_text',
            new_name='motivational_text_id',
        ),
        migrations.RenameField(
            model_name='skill',
            old_name='skill',
            new_name='skill_id',
        ),
        migrations.RenameField(
            model_name='theme',
            old_name='theme',
            new_name='theme_id',
        ),
        migrations.RemoveField(
            model_name='skillfeedback',
            name='skill_feedback',
        ),
        migrations.AddField(
            model_name='feedback',
            name='last_retry_datetime',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='feedback',
            name='retries',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='feedback',
            name='status',
            field=models.CharField(choices=[('CREATED', 'Created'), ('QUEUED', 'Queued'), ('PROCESSING', 'Processing'), ('FINISHED', 'Finished'), ('FAILED', 'Failed')], default='CREATED', max_length=50),
        ),
        migrations.AddField(
            model_name='originalessaytext',
            name='full_original_text',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='skillfeedback',
            name='skill_feedback_id',
            field=models.AutoField(db_column='skill_feedback_id', primary_key=True, serialize=False),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='originalessaytext',
            name='feedback',
            field=models.OneToOneField(db_column='feedback_id', on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='originalessaytext', serialize=False, to='core.feedback'),
        ),
        migrations.AlterField(
            model_name='refinedessaytext',
            name='feedback',
            field=models.OneToOneField(db_column='feedback_id', on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='refinedessaytext', serialize=False, to='core.feedback'),
        ),
        migrations.AlterField(
            model_name='userconfig',
            name='allow_notifications',
            field=models.BooleanField(default=False),
        ),
    ]