# Generated by Django 5.1.6 on 2025-03-15 23:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='teammember',
            old_name='instagram',
            new_name='github',
        ),
        migrations.RenameField(
            model_name='teammember',
            old_name='twitter',
            new_name='portfolio',
        ),
    ]
