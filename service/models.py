from django.db import models
from django.contrib.auth.models import User
from django.db.models import FloatField, F, Func, Value
from django.db.models.functions import Sqrt, Sin, Cos, ACos, Radians

class ServiceCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Service(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    address = models.TextField()
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    phone_contact = models.CharField(max_length=10, blank=True, null=True)
    email_contact = models.EmailField(blank=True, null=True)
    categories = models.ManyToManyField(ServiceCategory, related_name='services')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class ServiceComment(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.author} on {self.post}'