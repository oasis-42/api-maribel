# Generated by Django 5.0.6 on 2024-06-21 03:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='EssayOriginalText',
            new_name='OriginalEssayText',
        ),
        migrations.RenameModel(
            old_name='EssayCorrectedText',
            new_name='RefinedEssayText',
        ),
    ]