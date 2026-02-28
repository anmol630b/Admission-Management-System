from django.db import models
from django.contrib.auth.models import AbstractUser
import random
from django.utils import timezone


# =========================
# CUSTOM USER MODEL
# =========================
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.username


# =========================
# OTP MODEL
# =========================
class OTPModel(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now=True)

    def generate_otp(self):
        self.otp = str(random.randint(100000, 999999))
        self.save()
        return self.otp

    def is_expired(self):
        # 10 minute baad expire
        return (timezone.now() - self.created_at).seconds > 600

    def __str__(self):
        return f"OTP for {self.user.username}"


# =========================
# CONTACT MODEL
# =========================
class Contact(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, null=True, blank=True)
    email = models.CharField(max_length=100)
    message = models.TextField()
    date = models.DateField(auto_now_add=True)

    def __repr__(self):
        return f"{self.name} - {self.email}"


# =========================
# ADMISSION MODEL
# =========================
class Admission(models.Model):
    name = models.CharField(max_length=255)
    father_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    dob = models.DateField()
    course = models.CharField(max_length=100)
    documents = models.FileField(upload_to='admission_docs/', blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __repr__(self):
        return f"{self.name} - {self.course}"
    
    # =========================
# NOTICE MODEL
# =========================
class Notice(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    title = models.CharField(max_length=200)
    content = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']