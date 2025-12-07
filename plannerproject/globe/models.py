from django.db import models
from django.contrib.auth.models import User

# For autosaving a profile when a user is created
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    country = models.CharField(max_length=100, blank=True, null=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    preferred_activities = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class SavedTrip(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_trips')
    source_city = models.CharField(max_length=200)
    destination_city = models.CharField(max_length=200)
    departure_date = models.DateField()
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.source_city} to {self.destination_city} - {self.departure_date}"
