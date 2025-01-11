from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    ROLE_CHOICES = [
        ('Public', 'Public'),
        ('Low-Income User', 'Low-Income User'),
        ('Organisation','Organisation')
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(blank=True, null=True, max_length=10)
    is_phone_public = models.BooleanField(default=True)
    role = models.CharField(choices=ROLE_CHOICES, default='Public', max_length=256)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    website = models.CharField(blank=True, null=True, max_length=256) #for organisations
    is_dm_open = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username