# Generated by Django 5.1.6 on 2025-03-15 23:50

import home.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_rename_instagram_teammember_github_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='teammember',
            old_name='github',
            new_name='instagram',
        ),
        migrations.RenameField(
            model_name='teammember',
            old_name='portfolio',
            new_name='twitter',
        ),
        migrations.AlterField(
            model_name='teammember',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to=home.models.team_member_photo_path),
        ),
    ]
