# home/views.py
from django.shortcuts import render, redirect
from datetime import datetime
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from home.models import Contact, Admission, CustomUser, OTPModel, Notice, Timetable, Result, Attendance, FeePayment
from home.forms import CustomUserCreationForm, CustomAuthenticationForm, CustomPasswordResetForm, CustomSetPasswordForm, LoginOTPForm, VerifyLoginOTPForm, ProfileUpdateForm

try:
    import razorpay
    RAZORPAY_AVAILABLE = True
except ImportError:
    RAZORPAY_AVAILABLE = False


# =========================
# PUBLIC VIEWS
# =========================
def home_view(request):
    return render(request, 'home/index.html')

def about_view(request):
    return render(request, 'home/about.html')

@login_required
def contact_view(request):
    if request.method == "POST":
        name = request.POST.get('name')
        phone = request.POST.get("phone")
        email = request.POST.get('email')
        subject = request.POST.get('subject', '')
        message_text = request.POST.get('message')
        Contact.objects.create(
            name=name,
            phone=phone,
            email=email,
            subject=subject,
            message=message_text,
            date=datetime.today()
        )
        messages.success(request, "Your message has been sent successfully!")
    return render(request, 'home/contact.html')


# =========================
# ADMISSION VIEWS
# =========================
@login_required
def admission_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        father_name = request.POST.get('father_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        dob = request.POST.get('dob')
        course = request.POST.get('course')
        message_text = request.POST.get('message')
        documents = request.FILES.get('documents')
        Admission.objects.create(
            name=name,
            father_name=father_name,
            email=email,
            phone=phone,
            dob=dob,
            course=course,
            message=message_text,
            documents=documents
        )
        messages.success(request, "Your admission form has been submitted successfully!")
        return redirect('admission-success')
    return render(request, 'home/admission.html')

def admission_success(request):
    return render(request, 'home/admission_success.html')


# =========================
# AUTHENTICATION VIEWS
# =========================
def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            verification_link = request.build_absolute_uri(f"/verify-email/{uid}/{token}/")
            send_mail(
                subject="Verify Your Email - Univio",
                message=f"Click the link below to verify your email:\n\n{verification_link}\n\nIf you did not create this account, please ignore this email.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )
            messages.success(request, "Account created! Check your email to verify your account.")
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'home/signup.html', {'form': form})


def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None
    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.is_email_verified = True
        user.save()
        messages.success(request, "Email verified! You can now login.")
        return redirect('login')
    else:
        messages.error(request, "Invalid verification link.")
        return redirect('signup')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('home')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'home/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully!")
    return redirect('home')


def login_otp_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = LoginOTPForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        email = form.cleaned_data['email']
        try:
            user = CustomUser.objects.get(username=username, email=email)
        except CustomUser.DoesNotExist:
            messages.error(request, 'Username or Email is incorrect!')
            return render(request, 'home/login_otp.html', {'form': form})
        otp_obj, _ = OTPModel.objects.get_or_create(user=user)
        otp = otp_obj.generate_otp()
        send_mail(
            'Univio - Login OTP',
            f'Your Login OTP is: {otp}\nThis OTP is valid for 10 minutes.',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        request.session['otp_user_id'] = user.id
        messages.success(request, f'OTP sent to {email}!')
        return redirect('verify_login_otp')
    return render(request, 'home/login_otp.html', {'form': form})


def verify_login_otp_view(request):
    user_id = request.session.get('otp_user_id')
    if not user_id:
        return redirect('login_otp')
    form = VerifyLoginOTPForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        entered_otp = form.cleaned_data['otp']
        try:
            user = CustomUser.objects.get(id=user_id)
            otp_obj = OTPModel.objects.get(user=user)
        except (CustomUser.DoesNotExist, OTPModel.DoesNotExist):
            messages.error(request, 'Something went wrong, please try again.')
            return redirect('login_otp')
        if otp_obj.is_expired():
            messages.error(request, 'OTP has expired! Please request again.')
            return redirect('login_otp')
        if otp_obj.otp == entered_otp:
            del request.session['otp_user_id']
            login(request, user)
            messages.success(request, f'Welcome, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Incorrect OTP! Please try again.')
    return render(request, 'home/verify_login_otp.html', {'form': form})


def password_reset_request(request):
    if request.method == "POST":
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            form.save(
                request=request,
                use_https=request.is_secure(),
                email_template_name='home/password_reset_email.html',
            )
            return redirect('password_reset_done')
    else:
        form = CustomPasswordResetForm()
    return render(request, 'home/password_reset.html', {'form': form})


def password_reset_done_view(request):
    return render(request, 'home/password_reset_done.html')


def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None
    if user is None or not default_token_generator.check_token(user, token):
        messages.error(request, "Invalid reset link")
        return redirect('password_reset')
    if request.method == 'POST':
        form = CustomSetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Password reset successful!")
            return redirect('login')
    else:
        form = CustomSetPasswordForm(user)
    return render(request, 'home/password_reset_confirm.html', {'form': form})


# =========================
# DASHBOARD
# =========================
@login_required
def dashboard_view(request):
    admission = Admission.objects.filter(email=request.user.email).last()
    notices = Notice.objects.filter(is_active=True)[:5]
    results = Result.objects.filter(student=request.user)[:5]
    attendance = Attendance.objects.filter(student=request.user)
    total_classes = attendance.count()
    present_classes = attendance.filter(is_present=True).count()
    attendance_percentage = round((present_classes / total_classes) * 100) if total_classes > 0 else 0
    fee_payments = FeePayment.objects.filter(student=request.user)
    return render(request, 'home/dashboard.html', {
        'user': request.user,
        'admission': admission,
        'notices': notices,
        'results': results,
        'attendance_percentage': attendance_percentage,
        'present_classes': present_classes,
        'total_classes': total_classes,
        'fee_payments': fee_payments,
    })


# =========================
# PROFILE
# =========================
@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'home/profile.html', {'form': form})


# =========================
# DELETE ACCOUNT
# =========================
@login_required
def delete_account_view(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "Your account has been deleted.")
        return redirect('home')
    return redirect('profile')


# =========================
# NOTICE BOARD
# =========================
@login_required
def notice_board_view(request):
    notices = Notice.objects.filter(is_active=True)
    return render(request, 'home/notice_board.html', {'notices': notices})


# =========================
# TIMETABLE
# =========================
@login_required
def timetable_view(request):
    admission = Admission.objects.filter(email=request.user.email).last()
    course = admission.course if admission else None
    timetable = Timetable.objects.filter(course=course) if course else []
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    timetable_by_day = {}
    for day in days:
        timetable_by_day[day] = Timetable.objects.filter(course=course, day=day) if course else []
    return render(request, 'home/timetable.html', {
        'timetable_by_day': timetable_by_day,
        'course': course,
        'days': days,
    })


# =========================
# RESULTS
# =========================
@login_required
def results_view(request):
    results = Result.objects.filter(student=request.user)
    semesters = results.values_list('semester', flat=True).distinct()
    results_by_semester = {}
    for sem in semesters:
        results_by_semester[sem] = results.filter(semester=sem)
    return render(request, 'home/results.html', {
        'results_by_semester': results_by_semester,
        'results': results,
    })


# =========================
# ATTENDANCE
# =========================
@login_required
def attendance_view(request):
    attendance = Attendance.objects.filter(student=request.user)
    total = attendance.count()
    present = attendance.filter(is_present=True).count()
    absent = total - present
    percentage = round((present / total) * 100) if total > 0 else 0
    subjects = attendance.values_list('subject', flat=True).distinct()
    subject_wise = {}
    for sub in subjects:
        sub_att = attendance.filter(subject=sub)
        sub_total = sub_att.count()
        sub_present = sub_att.filter(is_present=True).count()
        subject_wise[sub] = {
            'total': sub_total,
            'present': sub_present,
            'absent': sub_total - sub_present,
            'percentage': round((sub_present / sub_total) * 100) if sub_total > 0 else 0,
        }
    return render(request, 'home/attendance.html', {
        'attendance': attendance,
        'total': total,
        'present': present,
        'absent': absent,
        'percentage': percentage,
        'subject_wise': subject_wise,
    })


# =========================
# FEE RECEIPT PDF
# =========================
@login_required
def fee_receipt_pdf(request):
    admission = Admission.objects.filter(email=request.user.email).last()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="fee_receipt_{request.user.username}.pdf"'
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    p.setFillColor(colors.HexColor('#1a1a2e'))
    p.rect(0, height - 100, width, 100, fill=True, stroke=False)
    p.setFillColor(colors.HexColor('#ffcc00'))
    p.setFont("Helvetica-Bold", 28)
    p.drawString(40, height - 50, "UNIVIO")
    p.setFillColor(colors.white)
    p.setFont("Helvetica", 12)
    p.drawString(40, height - 75, "College Management Portal")
    p.setFont("Helvetica-Bold", 14)
    p.drawRightString(width - 40, height - 55, "FEE RECEIPT")
    p.setFont("Helvetica", 10)
    p.drawRightString(width - 40, height - 75, f"Date: {datetime.today().strftime('%d %B %Y')}")

    p.setFillColor(colors.HexColor('#1a1a2e'))
    p.setFont("Helvetica-Bold", 14)
    p.drawString(40, height - 140, "Student Information")
    p.setStrokeColor(colors.HexColor('#ffcc00'))
    p.setLineWidth(2)
    p.line(40, height - 145, width - 40, height - 145)

    info = [
        ("Student Name", request.user.username),
        ("Email", request.user.email),
        ("Phone", request.user.phone or "Not provided"),
        ("Course", admission.course if admission else "Not Applied"),
        ("Father's Name", admission.father_name if admission else "-"),
        ("Applied On", admission.submitted_at.strftime('%d %B %Y') if admission else "-"),
    ]
    y = height - 170
    p.setFont("Helvetica", 11)
    for label, value in info:
        p.setFillColor(colors.HexColor('#666666'))
        p.drawString(40, y, f"{label}:")
        p.setFillColor(colors.HexColor('#1a1a2e'))
        p.drawString(200, y, str(value))
        y -= 25

    y -= 20
    p.setFillColor(colors.HexColor('#1a1a2e'))
    p.setFont("Helvetica-Bold", 14)
    p.drawString(40, y, "Fee Details")
    p.setStrokeColor(colors.HexColor('#ffcc00'))
    p.line(40, y - 5, width - 40, y - 5)
    y -= 30
    p.setFillColor(colors.HexColor('#1a1a2e'))
    p.rect(40, y - 5, width - 80, 25, fill=True, stroke=False)
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 11)
    p.drawString(50, y + 5, "Year")
    p.drawString(200, y + 5, "Amount")
    p.drawString(350, y + 5, "Status")

    fees = [
        ("1st Year", "Rs.45,000", "Pending"),
        ("2nd Year", "Rs.45,000", "Pending"),
        ("3rd Year", "Rs.45,000", "Pending"),
    ]
    for i, (year, amount, status) in enumerate(fees):
        y -= 28
        if i % 2 == 0:
            p.setFillColor(colors.HexColor('#f8f9ff'))
            p.rect(40, y - 5, width - 80, 25, fill=True, stroke=False)
        p.setFillColor(colors.HexColor('#1a1a2e'))
        p.setFont("Helvetica", 11)
        p.drawString(50, y + 5, year)
        p.drawString(200, y + 5, amount)
        p.setFillColor(colors.HexColor('#856404'))
        p.drawString(350, y + 5, status)

    y -= 35
    p.setFillColor(colors.HexColor('#1a1a2e'))
    p.rect(40, y - 5, width - 80, 25, fill=True, stroke=False)
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y + 5, "Total")
    p.drawString(200, y + 5, "Rs.1,35,000")

    p.setFillColor(colors.HexColor('#1a1a2e'))
    p.rect(0, 0, width, 50, fill=True, stroke=False)
    p.setFillColor(colors.white)
    p.setFont("Helvetica", 9)
    p.drawCentredString(width / 2, 30, "Univio College | Computer generated receipt | No signature required")
    p.drawCentredString(width / 2, 15, "For queries: info@univio.com | +91 00000 00000")
    p.showPage()
    p.save()
    return response


# =========================
# FEE PAYMENT
# =========================
@login_required
def fee_payment_view(request):
    if not RAZORPAY_AVAILABLE:
        messages.error(request, "Payment gateway is not available at the moment.")
        return redirect('dashboard')
    admission = Admission.objects.filter(email=request.user.email).last()
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    amount = 45000 * 100
    order = client.order.create(data={'amount': amount, 'currency': 'INR', 'payment_capture': 1})
    return render(request, 'home/fee_payment.html', {
        'order': order,
        'razorpay_key': settings.RAZORPAY_KEY_ID,
        'amount': amount,
        'admission': admission,
        'user': request.user,
    })


# =========================
# PAYMENT SUCCESS
# =========================
@login_required
def payment_success(request):
    return render(request, 'home/payment_success.html')


# =========================
# STUDENT ID CARD PDF
# =========================
@login_required
def student_id_card(request):
    from reportlab.lib.utils import ImageReader
    import os, io

    admission = Admission.objects.filter(email=request.user.email).last()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="UniVio_ID_{request.user.username}.pdf"'

    W, H = 360, 620
    p = canvas.Canvas(response, pagesize=(W, H))

    # BACKGROUND
    p.setFillColor(colors.HexColor('#0f0f1a'))
    p.rect(0, 0, W, H, fill=True, stroke=False)

    # TOP GOLD BAR
    p.setFillColor(colors.HexColor('#ffcc00'))
    p.rect(0, H - 10, W, 10, fill=True, stroke=False)
    p.rect(0, 0, 6, H, fill=True, stroke=False)
    p.rect(W - 6, 0, 6, H, fill=True, stroke=False)

    # LOGO CIRCLE
    p.setFillColor(colors.HexColor('#ffcc00'))
    p.circle(W / 2, H - 55, 28, fill=True, stroke=False)
    p.setFillColor(colors.HexColor('#0f0f1a'))
    p.setFont("Helvetica-Bold", 20)
    p.drawCentredString(W / 2, H - 63, "U")

    # COLLEGE NAME
    p.setFillColor(colors.HexColor('#ffcc00'))
    p.setFont("Helvetica-Bold", 24)
    p.drawCentredString(W / 2, H - 100, "UNIVIO")
    p.setFillColor(colors.HexColor('#aaaacc'))
    p.setFont("Helvetica", 7.5)
    p.drawCentredString(W / 2, H - 114, "COLLEGE OF EXCELLENCE  •  EST. 2010")

    # GOLD LINE
    p.setStrokeColor(colors.HexColor('#ffcc00'))
    p.setLineWidth(0.8)
    p.line(30, H - 124, W - 30, H - 124)

    # LABEL
    p.setFillColor(colors.HexColor('#ffcc00'))
    p.setFont("Helvetica-Bold", 9)
    p.drawCentredString(W / 2, H - 138, "STUDENT IDENTITY CARD")

    # PROFILE PHOTO
    photo_cx = W / 2
    photo_cy = H - 215
    p.setStrokeColor(colors.HexColor('#ffcc00'))
    p.setLineWidth(3)
    p.circle(photo_cx, photo_cy, 50, fill=False, stroke=True)

    if request.user.profile_photo:
        try:
            photo_path = request.user.profile_photo.path
            if os.path.exists(photo_path):
                p.drawImage(ImageReader(photo_path), photo_cx-46, photo_cy-46, width=92, height=92, preserveAspectRatio=True, mask='auto')
        except Exception:
            pass
    else:
        p.setFillColor(colors.HexColor('#1e1e3a'))
        p.circle(photo_cx, photo_cy, 46, fill=True, stroke=False)
        p.setFillColor(colors.HexColor('#ffcc00'))
        p.setFont("Helvetica-Bold", 34)
        p.drawCentredString(photo_cx, photo_cy - 13, request.user.username[0].upper())

    # NAME
    name_y = photo_cy - 72
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 15)
    name_display = admission.name.upper() if admission and admission.name else request.user.username.upper()
    p.drawCentredString(W / 2, name_y, name_display)

    # COURSE BADGE
    badge_y = name_y - 28
    if admission:
        badge_w = 110
        p.setFillColor(colors.HexColor('#ffcc00'))
        p.roundRect(W/2 - badge_w/2, badge_y - 7, badge_w, 20, 10, fill=True, stroke=False)
        p.setFillColor(colors.HexColor('#0f0f1a'))
        p.setFont("Helvetica-Bold", 9)
        p.drawCentredString(W / 2, badge_y + 3, admission.course)

    # INFO BOX
    info_top = badge_y - 26
    info_items = [
        ("Student ID", f"UNV{request.user.id:05d}"),
        ("Username", request.user.username),
        ("Email", request.user.email if len(request.user.email) <= 32 else request.user.email[:30] + ".."),
        ("Phone", request.user.phone if request.user.phone else "Not Provided"),
        ("Valid Till", "May 2027"),
    ]

    row_h = 34
    box_h = len(info_items) * row_h + 20
    box_y = info_top - box_h

    p.setFillColor(colors.HexColor('#16162a'))
    p.roundRect(18, box_y, W - 36, box_h, 10, fill=True, stroke=False)

    y = info_top - 18
    for label, value in info_items:
        p.setFillColor(colors.HexColor('#888899'))
        p.setFont("Helvetica", 7)
        p.drawString(32, y, label.upper())
        p.setFillColor(colors.white)
        p.setFont("Helvetica-Bold", 10)
        p.drawString(32, y - 14, value)
        p.setStrokeColor(colors.HexColor('#2a2a45'))
        p.setLineWidth(0.4)
        p.line(32, y - 19, W - 32, y - 19)
        y -= row_h

    # QR CODE
    try:
        import qrcode
        qr_data = f"UNIVIO|{request.user.username}|UNV{request.user.id:05d}|{request.user.email}"
        qr_img = qrcode.make(qr_data)
        qr_buffer = io.BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        qr_size = 55
        qr_x = W - qr_size - 20
        qr_y = 42
        p.drawImage(ImageReader(qr_buffer), qr_x, qr_y, width=qr_size, height=qr_size)
        p.setFillColor(colors.HexColor('#888899'))
        p.setFont("Helvetica", 6)
        p.drawCentredString(qr_x + qr_size/2, qr_y - 8, "Scan to Verify")
    except Exception:
        pass

    # BOTTOM BAR
    p.setFillColor(colors.HexColor('#ffcc00'))
    p.rect(0, 0, W, 36, fill=True, stroke=False)
    p.setFillColor(colors.HexColor('#0f0f1a'))
    p.setFont("Helvetica-Bold", 8)
    p.drawString(18, 22, "univio.edu.in")
    p.drawString(18, 10, "info@univio.edu.in  |  +91 98765 43210")

    p.showPage()
    p.save()
    return response