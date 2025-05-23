# Generated by Django 5.1.3 on 2025-01-11 14:34

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(blank=True, max_length=10, null=True)),
                ('is_phone_public', models.BooleanField(default=True)),
                ('role', models.CharField(choices=[('Public', 'Public'), ('Low-Income User', 'Low-Income User'), ('Organisation', 'Organisation')], default='Public', max_length=256)),
                ('bio', models.TextField(blank=True, null=True)),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='profile_pics/')),
                ('website', models.CharField(blank=True, max_length=256, null=True)),
                ('is_dm_open', models.BooleanField(default=True)),
                ('is_verified', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
