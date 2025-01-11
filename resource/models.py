from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class ResourceCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Resource(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    link = models.CharField(max_length=200, blank=True, null=True)
    attachment = models.FileField(upload_to='resources/', blank=True, null=True)
    categories = models.ManyToManyField(ResourceCategory, related_name='resources')
    min_income_pc = models.FloatField(blank=True, null=True)
    max_income_pc = models.FloatField(blank=True, null=True)
    min_income_gross = models.FloatField(blank=True, null=True)
    max_income_gross = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class ResourceComment(models.Model):
    post = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.author} on {self.post}'