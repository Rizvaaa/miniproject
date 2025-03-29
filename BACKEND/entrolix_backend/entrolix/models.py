from django.db import models
from django.contrib.auth.models import User

# class Task(models.Model):
#     title = models.CharField(max_length=255)
#     completed = models.BooleanField(default=False)

#     def __str__(self):
#         return self.title

class Student(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    role=models.CharField(max_length=15,default="student")

    def __str__(self):
        return self.user.username
    

class Subadmin(models.Model):
    user = models. OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, unique=True)
    role = models.CharField(max_length=15, default="subadmin")

    def str(self):
        return self.user.username
    