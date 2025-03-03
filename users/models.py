from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('reader', 'Reader'),
        ('author','Author')
    ]

    email=models.EmailField(unique=True)
    role=models.CharField(max_length=10,choices=ROLE_CHOICES,default='reader')

    USERNAME_FIELD='email'
    REQUIRED_FIELDS=['username']

    def __str__(self):
        return f"{self.username}-{self.role}"