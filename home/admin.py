from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from home.models import CustomUser, Contact, Admission, OTPModel, Notice, Timetable, Result, Attendance, FeePayment


# =========================
# CUSTOM USER ADMIN
# =========================
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'phone', 'is_email_verified', 'is_active', 'date_joined']
    list_filter = ['is_active', 'is_email_verified', 'is_staff']
    search_fields = ['username', 'email', 'phone']
    ordering = ['-date_joined']
    fieldsets = UserAdmin.fieldsets + (
        ('Extra Info', {'fields': ('phone', 'address', 'profile_photo', 'is_email_verified')}),
    )


# =========================
# CONTACT ADMIN
# =========================
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'subject', 'date']
    search_fields = ['name', 'email', 'subject']
    ordering = ['-date']


# =========================
# ADMISSION ADMIN
# =========================
@admin.register(Admission)
class AdmissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'course', 'email', 'phone', 'status', 'submitted_at']
    list_filter = ['course', 'status']
    search_fields = ['name', 'email', 'phone']
    ordering = ['-submitted_at']


# =========================
# OTP ADMIN
# =========================
@admin.register(OTPModel)
class OTPAdmin(admin.ModelAdmin):
    list_display = ['user', 'otp', 'created_at']
    ordering = ['-created_at']


# =========================
# NOTICE ADMIN
# =========================
@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ['title', 'priority', 'is_active', 'created_at']
    list_filter = ['priority', 'is_active']
    search_fields = ['title', 'content']
    ordering = ['-created_at']


# =========================
# TIMETABLE ADMIN
# =========================
@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ['course', 'day', 'subject', 'start_time', 'end_time', 'teacher', 'room']
    list_filter = ['course', 'day']
    search_fields = ['course', 'subject', 'teacher']
    ordering = ['course', 'day', 'start_time']


# =========================
# RESULT ADMIN
# =========================
@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'semester', 'subject', 'marks_obtained', 'total_marks', 'grade']
    list_filter = ['course', 'semester', 'grade']
    search_fields = ['student__username', 'subject']
    ordering = ['-created_at']


# =========================
# ATTENDANCE ADMIN
# =========================
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'subject', 'date', 'is_present']
    list_filter = ['course', 'subject', 'is_present']
    search_fields = ['student__username', 'subject']
    ordering = ['-date']


# =========================
# FEE PAYMENT ADMIN
# =========================
@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = ['student', 'amount', 'year', 'status', 'payment_id', 'paid_at']
    list_filter = ['status', 'year']
    search_fields = ['student__username', 'payment_id']
    ordering = ['-created_at']
