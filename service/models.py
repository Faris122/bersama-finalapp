from django.db import models
from django.contrib.auth.models import User
from math import radians, cos, sin, asin, sqrt
from django.core.exceptions import ValidationError

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

    def calculate_distance(self, user_lat, user_lon):
        #Calculate distance between this service and a user location using the Haversine formula
        if not self.latitude or not self.longitude:
            return None

        # Convert degrees to radians
        lat1, lon1, lat2, lon2 = map(radians, [user_lat, user_lon, self.latitude, self.longitude])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        radius_km = 6371  # Earth's radius in kilometres
        return round(radius_km * c, 2)
    
class ServiceComment(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.author} on {self.post}'
    
class EventCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Event(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    address = models.TextField()
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    host = models.CharField(max_length=200, blank=True, null=True)
    phone_contact = models.CharField(max_length=10, blank=True, null=True)
    email_contact = models.EmailField(blank=True, null=True)
    categories = models.ManyToManyField(EventCategory, related_name='events')
    datetime_start = models.DateTimeField()
    datetime_end = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_distance(self, user_lat, user_lon):
        # Calculate distance between this service and a user location using the Haversine formula
        if not self.latitude or not self.longitude:
            return None

        # Convert degrees to radians
        lat1, lon1, lat2, lon2 = map(radians, [user_lat, user_lon, self.latitude, self.longitude])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        radius_km = 6371  # Earth's radius in kilometres
        return round(radius_km * c, 2)
    def clean(self): # Makes sure datetime_start is before datetime_end
        if self.datetime_start and self.datetime_end and self.datetime_start >= self.datetime_end:
            raise ValidationError({'datetime_end': 'End time must be after the start time.'})

    def save(self, *args, **kwargs):
        self.full_clean()  # Ensuring Validation
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
class EventComment(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.author} on {self.post}'