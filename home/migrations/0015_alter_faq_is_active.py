# Generated by Django 5.1.6 on 2025-03-18 05:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0014_faq_status_alter_blog_content'),
    ]

    operations = [
        migrations.AlterField(
            model_name='faq',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
    ]
