# Generated by Django 4.2.17 on 2025-03-30 08:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0008_message_read'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='financialprofile',
            name='monthly_expenses',
        ),
    ]
