# Generated by Django 5.1.6 on 2025-03-18 19:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0021_alter_faq_updated_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='faq',
            name='updated_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
