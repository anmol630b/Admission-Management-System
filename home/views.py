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
import razorpay
from home.models import Contact, Admission, CustomUser, OTPModel, Notice
from home.forms import CustomUserCreationForm, CustomAuthenticationForm, CustomPasswordResetForm, CustomSetPasswordForm, LoginOTPForm, VerifyLoginOTPForm, ProfileUpdateForm


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
        message_text = request.POST.get('message')
        Contact.objects.create(
            name=name,
            phone=phone,
            email=email,
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

# ===== SIGNUP WITH EMAIL VERIFICATION =====
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
                subject="Verify Your Email",
                message=f"Click to verify your email: {verification_link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )
            messages.success(request, "Account created! Check your email to verify your account.")
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'home/signup.html', {'form': form})


# ===== EMAIL VERIFICATION =====
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


# ===== LOGIN =====
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


# ===== LOGOUT =====
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully!")
    return redirect('home')


# ===== OTP LOGIN - Step 1 =====
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
            messages.error(request, 'Username ya Email galat hai!')
            return render(request, 'home/login_otp.html', {'form': form})
        otp_obj, _ = OTPModel.objects.get_or_create(user=user)
        otp = otp_obj.generate_otp()
        send_mail(
            'College Portal - Login OTP',
            f'Tumhara Login OTP hai: {otp}\nYe 10 minute ke liye valid hai.',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        request.session['otp_user_id'] = user.id
        messages.success(request, f'OTP {email} pe bhej diya!')
        return redirect('verify_login_otp')
    return render(request, 'home/login_otp.html', {'form': form})


# ===== OTP LOGIN - Step 2 =====
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
            messages.error(request, 'Kuch galat hua, dobara try karo.')
            return redirect('login_otp')
        if otp_obj.is_expired():
            messages.error(request, 'OTP expire ho gaya! Dobara request karo.')
            return redirect('login_otp')
        if otp_obj.otp == entered_otp:
            del request.session['otp_user_id']
            login(request, user)
            messages.success(request, f'Welcome, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Galat OTP! Dobara try karo.')
    return render(request, 'home/verify_login_otp.html', {'form': form})


# ===== PASSWORD RESET REQUEST =====
def password_reset_request(request):
    if request.method == "POST":
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            form.save(
                request=request,
                use_https=request.is_secure(),
                email_template_name='home/password_reset_email.html',
            )
            messages.success(request, "Password reset email sent!")
            return redirect('login')
    else:
        form = CustomPasswordResetForm()
    return render(request, 'home/password_reset.html', {'form': form})


# ===== PASSWORD RESET CONFIRM =====
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


# ===== DASHBOARD =====
@login_required
def dashboard_view(request):
    admission = Admission.objects.filter(email=request.user.email).last()
    notices = Notice.objects.filter(is_active=True)[:5]
    return render(request, 'home/dashboard.html', {
        'user': request.user,
        'admission': admission,
        'notices': notices,
    })


# ===== PROFILE =====
@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile update ho gaya!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'home/profile.html', {'form': form})


# ===== NOTICE BOARD =====
@login_required
def notice_board_view(request):
    notices = Notice.objects.filter(is_active=True)
    return render(request, 'home/notice_board.html', {'notices': notices})


# ===== FEE RECEIPT PDF =====
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


# ===== FEE PAYMENT =====
@login_required
def fee_payment_view(request):
    admission = Admission.objects.filter(email=request.user.email).last()
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    amount = 45000 * 100
    order_data = {
        'amount': amount,
        'currency': 'INR',
        'payment_capture': 1
    }
    order = client.order.create(data=order_data)
    return render(request, 'home/fee_payment.html', {
        'order': order,
        'razorpay_key': settings.RAZORPAY_KEY_ID,
        'amount': amount,
        'admission': admission,
        'user': request.user,
    })


# ===== PAYMENT SUCCESS =====
@login_required
def payment_success(request):
    return render(request, 'home/payment_success.html')