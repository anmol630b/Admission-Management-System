from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from home.models import CustomUser, Contact, Admission, OTPModel, Notice


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
    list_display = ['name', 'email', 'phone', 'date']
    search_fields = ['name', 'email']
    ordering = ['-date']


# =========================
# ADMISSION ADMIN
# =========================
@admin.register(Admission)
class AdmissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'course', 'email', 'phone', 'submitted_at']
    list_filter = ['course']
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