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
    

class StudentApplication(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE,null=True)
    course_name = models.CharField(max_length=100, blank=True, null=True)
    plus_two_certificate = models.ImageField(upload_to='certificates/', blank=True, null=True)
    fee_reciept = models.ImageField(upload_to='certificates/', blank=True, null=True)
    sslc_certificate = models.ImageField(upload_to='certificates/', blank=True, null=True)
    admit_card = models.ImageField(upload_to='certificates/', blank=True, null=True)
    passport_size_photo = models.ImageField(upload_to='photos/', blank=True, null=True)
    income_certificate = models.ImageField(upload_to='certificates/', blank=True, null=True)
    annual_income = models.PositiveIntegerField(default=0)
    community_certificate = models.ImageField(upload_to='certificates/', blank=True, null=True)
    nativity_certificate = models.ImageField(upload_to='certificates/', blank=True, null=True)
    transfer_certificate = models.ImageField(upload_to='certificates/', blank=True, null=True)
    conduct_certificate = models.ImageField(upload_to='certificates/', blank=True, null=True)
    physical_certificate = models.ImageField(upload_to='certificates/', blank=True, null=True)
    migration_certificate = models.ImageField(upload_to='certificates/', blank=True, null=True)
    is_approved = models.BooleanField(default=False,null=True)

    def _str_(self):
        return f"Application for {self.student.user.username}"
    

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    message = models.TextField()
    is_read = models.BooleanField(default=False)  
    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"Notification for {self.user.username} - {self.message[:50]}"