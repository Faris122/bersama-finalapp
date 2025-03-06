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
    monthly_expenses = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
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
    



    

