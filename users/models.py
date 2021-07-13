from django.db import models
from django.db.models.base import Model

# Create your models here.

class User(models.Model):
    email = models.EmailField()
    phone = models.CharField(max_length=14)
    password = models.CharField(max_length=24)
    verified = models.BooleanField(default=False)
    user_role = models.CharField(default='Customer',max_length=64)

class Profile(models.Model):
    name = models.CharField(max_length=124)
    profession = models.CharField(max_length=64)
    district = models.CharField(max_length=64)
    divison = models.CharField(max_length=64)
    upazilla = models.CharField(max_length=64)
    adress = models.CharField(max_length=128)
    profession = models.CharField(max_length=64)

class OTP(models.Model):
    phone_or_email = models.CharField(max_length=64)
    otp_code = models.CharField(max_length=10)
    timestamp = models.DateTimeField(auto_now=True)
