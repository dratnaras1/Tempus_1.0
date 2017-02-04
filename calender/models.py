from django.db import models

# Create your models here.

class OutlookAuth(models.Model):
    user_email = models.CharField(max_length = 254)
    auth_code = models.TextField()
    refresh_token = models.TextField()

class BookingToken(models.Model):
    analyst = models.ForeignKey(OutlookAuth, on_delete=models.CASCADE)
    token = models.CharField(max_length = 254)
    used = models.BooleanField(default = False)