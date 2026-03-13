from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Contact, Admission, OTPModel, Notice, Timetable, Result, Attendance, FeePayment


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone', 'is_email_verified', 'is_active', 'date_joined')
    list_filter = ('is_active', 'is_email_verified', 'is_staff')
    search_fields = ('username', 'email', 'phone')
    ordering = ('-date_joined',)
    fieldsets = UserAdmin.fieldsets + (
        ('Extra Info', {'fields': ('phone', 'profile_photo', 'is_email_verified')}),
    )


@admin.register(Admission)
class AdmissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'email', 'phone', 'status', 'submitted_at')
    list_filter = ('course', 'status')
    search_fields = ('name', 'email', 'phone')
    ordering = ('-submitted_at',)
    list_editable = ('status',)
    readonly_fields = ('submitted_at',)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'date')
    search_fields = ('name', 'email', 'subject')
    ordering = ('-date',)


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'priority', 'is_active', 'created_at')
    list_filter = ('priority', 'is_active')
    search_fields = ('title', 'content')
    ordering = ('-created_at',)
    list_editable = ('priority', 'is_active')


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ('course', 'day', 'subject', 'start_time', 'end_time', 'teacher', 'room')
    list_filter = ('course', 'day')
    search_fields = ('subject', 'teacher', 'course')
    ordering = ('course', 'day', 'start_time')


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'semester', 'subject', 'marks_obtained', 'total_marks', 'grade')
    list_filter = ('course', 'semester', 'grade')
    search_fields = ('student__username', 'subject', 'course')
    ordering = ('student', 'semester')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'subject', 'date', 'is_present')
    list_filter = ('course', 'is_present', 'date')
    search_fields = ('student__username', 'subject')
    ordering = ('-date',)
    list_editable = ('is_present',)


@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = ('student', 'amount', 'year', 'status', 'paid_at')
    list_filter = ('status', 'year')
    search_fields = ('student__username', 'payment_id')
    ordering = ('-paid_at',)
    readonly_fields = ('paid_at',)


@admin.register(OTPModel)
class OTPModelAdmin(admin.ModelAdmin):
    list_display = ('user', 'otp', 'created_at')
    search_fields = ('user__username',)
    ordering = ('-created_at',)
