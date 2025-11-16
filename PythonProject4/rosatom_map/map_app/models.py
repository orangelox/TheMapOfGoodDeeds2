from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class City(models.Model):
    name = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    latitude = models.FloatField(default=55.7558)
    longitude = models.FloatField(default=37.6173)

    def __str__(self):
        return f"{self.name}, {self.region}"

class NKOCategory(models.Model):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#0055a5')

    def __str__(self):
        return self.name

class NKO(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(NKOCategory, on_delete=models.CASCADE)
    description = models.TextField()
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    vk_link = models.URLField(blank=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    city = models.ForeignKey('City', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Профиль {self.user.username}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()