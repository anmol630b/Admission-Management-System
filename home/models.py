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
    subject = models.CharField(max_length=200, null=True, blank=True)
    message = models.TextField()
    date = models.DateField(auto_now_add=True)

    def __repr__(self):
        return f"{self.name} - {self.email}"


# =========================
# ADMISSION MODEL
# =========================
class Admission(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    name = models.CharField(max_length=255)
    father_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    dob = models.DateField()
    course = models.CharField(max_length=100)
    documents = models.FileField(upload_to='admission_docs/', blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
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


# =========================
# TIMETABLE MODEL
# =========================
class Timetable(models.Model):
    DAY_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
    ]
    course = models.CharField(max_length=100)
    day = models.CharField(max_length=20, choices=DAY_CHOICES)
    subject = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()
    teacher = models.CharField(max_length=100, blank=True, null=True)
    room = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.course} - {self.day} - {self.subject}"

    class Meta:
        ordering = ['day', 'start_time']


# =========================
# RESULT MODEL
# =========================
class Result(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    course = models.CharField(max_length=100)
    semester = models.CharField(max_length=20)
    subject = models.CharField(max_length=100)
    marks_obtained = models.IntegerField()
    total_marks = models.IntegerField(default=100)
    grade = models.CharField(max_length=5, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        percentage = (self.marks_obtained / self.total_marks) * 100
        if percentage >= 90:
            self.grade = 'A+'
        elif percentage >= 80:
            self.grade = 'A'
        elif percentage >= 70:
            self.grade = 'B+'
        elif percentage >= 60:
            self.grade = 'B'
        elif percentage >= 50:
            self.grade = 'C'
        else:
            self.grade = 'F'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.username} - {self.subject}"

    class Meta:
        ordering = ['-created_at']


# =========================
# ATTENDANCE MODEL
# =========================
class Attendance(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    course = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    date = models.DateField()
    is_present = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.username} - {self.subject} - {self.date}"

    class Meta:
        ordering = ['-date']
        unique_together = ['student', 'subject', 'date']


# =========================
# FEE PAYMENT MODEL
# =========================
class FeePayment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    year = models.CharField(max_length=20)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.year} - {self.status}"

    class Meta:
        ordering = ['-created_at']
