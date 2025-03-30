from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Sum


class Fundraiser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fundraisers')
    title = models.CharField(max_length=256)
    description = models.TextField()
    goal_amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    @property
    def amount_raised(self):
        total = self.funds.aggregate(total_amount=Sum('amount'))['total_amount']
        return total if total else 0  # Return 0 if no payments exist

    def is_active(self):
        return self.end_date > timezone.now()

    def progress(self):
        return (self.amount_raised / self.goal_amount) * 100
    
    def clean(self):
        # Ensure the user has a profile
        if not hasattr(self.user, 'profile'):
            raise ValidationError("User does not have a profile.")

        # If the user is a regular user and needs help, allow only one fundraiser
        if self.user.profile.role == 'Public' and self.user.profile.needs_help:
            if Fundraiser.objects.filter(user=self.user, end_date__gt=timezone.now()).exists():
                raise ValidationError("You can only create one fundraiser as a user who needs help.")

        # If the user is a regular user and does not need help, disallow fundraisers
        if self.user.profile.role == 'Public' and not self.user.profile.needs_help:
            raise ValidationError("You are not allowed to create a fundraiser as a user who does not need help.")

        # If the user is an organisation, allow multiple fundraisers (no restriction)

    def save(self, *args, **kwargs):
        # Run validation before saving
        self.clean()
        super().save(*args, **kwargs)
    
class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='donations', null=True)
    anon_name = models.CharField(max_length=25, null=True, blank=True)
    fundraiser = models.ForeignKey(Fundraiser, on_delete=models.CASCADE, related_name='funds')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.CharField(max_length=256, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.user:
            return f'{self.user.username} donated ${self.amount} to {self.fundraiser.title}'
        else:
            return f'Anonymous ({self.anon_name}) donated ${self.amount} to {self.fundraiser.title}'

    def clean(self):
        # If the user is anonymous, ensure anon_name is provided
        if not self.user and not self.anon_name:
            raise ValidationError({"anon_name": "An anonymous name is required for anonymous donations."})

        # If the user is authenticated, ensure anon_name is not provided
        if self.user and self.anon_name:
            self.anon_name = None

    def save(self, *args, **kwargs):
        # Run validation before saving
        self.clean()
        super().save(*args, **kwargs)

class FundraiserComment(models.Model):
    post = models.ForeignKey(Fundraiser, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.author} on {self.post}'