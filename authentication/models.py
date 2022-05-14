from django.db import models
from django.contrib.auth.models import AbstractUser,UserManager
from django.contrib.auth.hashers import make_password
from django.dispatch import receiver
from django.db.models.signals import post_save
import datetime

class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = CustomUser(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        assert extra_fields["is_staff"]
        assert extra_fields["is_superuser"]
        return self._create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    USER_TYPE = ((1, "ADMIN"),(2, "Student"))
    GENDER = [("M", "Male"), ("F", "Female"), ("N", "Non-binary")]

    username = None  # Removed username, using email instead
    email = models.EmailField(unique=True)
    user_type = models.CharField(default=1, choices=USER_TYPE, max_length=1)
    gender = models.CharField(max_length=1, choices=GENDER)
    profile_pic = models.ImageField(upload_to="profile_pictures/")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return self.first_name + " " + self.last_name

class Admin(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    roll_no = models.CharField(max_length=32,unique=True)
    branch = models.CharField(max_length = 120)
    course = models.CharField(max_length = 120)
    session = models.CharField(max_length = 9)

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name

class Attendance(models.Model):

    OPTIONS = [("P", "Present"), ("A", "Absent"), ("H", "Holiday")]

    user=models.ForeignKey(Student,on_delete=models.CASCADE)
    date = models.DateField(default=datetime.date.today)
    present=models.CharField(max_length=1,choices=OPTIONS,default="A")

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 1:
            Admin.objects.create(user=instance)
        if instance.user_type == 2:
            Student.objects.create(user=instance)


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.user_type == 1:
        instance.admin.save()
    if instance.user_type == 2:
        instance.student.save()