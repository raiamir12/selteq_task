from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ()

    def __str__(self):
        return self.email


class Task(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    task_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.task_name
