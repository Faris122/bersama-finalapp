# Generated by Django 4.2.17 on 2025-03-08 09:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resource', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='resource',
            name='deadline',
            field=models.DateField(blank=True, null=True),
        ),
    ]
