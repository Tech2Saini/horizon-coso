# Generated by Django 5.1.6 on 2025-03-18 03:35

import ckeditor_uploader.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0013_category_tag_blog'),
    ]

    operations = [
        migrations.AddField(
            model_name='faq',
            name='status',
            field=models.CharField(choices=[('Panding', 'Panding'), ('Solved', 'solved'), ('Rejected', 'Rejected')], default='panding', max_length=10),
        ),
        migrations.AlterField(
            model_name='blog',
            name='content',
            field=ckeditor_uploader.fields.RichTextUploadingField(),
        ),
    ]
