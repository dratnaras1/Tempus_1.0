from django.db import models

# Create your models here.

class OutlookAuth(models.Model):
    user_email = models.CharField(max_length = 254)
    auth_code = models.TextField()