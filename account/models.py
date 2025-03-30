from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    ROLE_CHOICES = [
        ('Public', 'Public'),
        ('Organisation','Organisation')
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(blank=True, null=True, max_length=10)
    is_phone_public = models.BooleanField(default=True)
    needs_help = models.BooleanField(default=False)
    role = models.CharField(choices=ROLE_CHOICES, default='Public', max_length=256)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    website = models.CharField(blank=True, null=True, max_length=256) #for organisations
    is_dm_open = models.BooleanField(default=True)
    address = models.TextField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.role != "Public" and self.needs_help:
            raise ValueError("Only Public users can request help.")
        if self.role != "Organisation" and not (self.website == '' or self.website == None):
            raise ValueError("Only organisations can have a website field.")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username
    
class FinancialProfile(models.Model):
    EMPLOYMENT_STATUS_CHOICES = [
        ('Working', 'Working'),
        ('Student', 'Student'),
        ('Unemployed', 'Unemployed'),
        ('Retired', 'Retired'),
        ('Disabled', 'Disabled'),
    ]

    HOUSING_STATUS_CHOICES = [
        ('Owned', 'Owned'),
        ('Rented', 'Rented'),
        ('Homeless', 'Homeless'),
        ('Shelter', 'Shelter'),
        ('Other', 'Other'),
    ]

    # Financial Information
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='financial_profile')
    own_income = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    household_income = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    household_members = models.IntegerField(default=1)
    has_elderly = models.BooleanField(default=False)
    has_children = models.BooleanField(default=False)

    employment_status = models.CharField(choices=EMPLOYMENT_STATUS_CHOICES, max_length=20)

    housing_status = models.CharField(choices=HOUSING_STATUS_CHOICES, max_length=20)

    def save(self, *args, **kwargs):
        if self.profile.needs_help == False:
            raise ValueError("Only users who need help can have a financial profile.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.employment_status}"

class Chat(models.Model):
    user1 = models.ForeignKey(User, related_name='chat_user1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='chat_user2', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat between {self.user1.username} and {self.user2.username}"

    def clean(self):
        if self.user1 == self.user2:
            raise ValueError("Users cannot chat with themselves.")
        
    def unread_message_count(self, user):
        return self.messages.filter(read=False).exclude(sender=user).count()

    class Meta: # Make sure the two users are uniquely paired
        unique_together = ('user1', 'user2')
    

class Message(models.Model):
    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False) 

    def __str__(self):
        return f"Message from {self.sender.username} at {self.timestamp}"



    

