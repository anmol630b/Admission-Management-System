from django.urls import path
from home import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('admission/', views.admission_view, name='admission'),
    path('admission-success/', views.admission_success, name='admission-success'),
    path('signup/', views.signup_view, name='signup'),
    path('verify-email/<uidb64>/<token>/', views.verify_email, name='verify_email'),
    path('login/', views.login_view, name='login'),
    path('login-otp/', views.login_otp_view, name='login_otp'),
    path('verify-login-otp/', views.verify_login_otp_view, name='verify_login_otp'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('profile/', views.profile_view, name='profile'),
    path('notices/', views.notice_board_view, name='notice_board'),
    path('fee-receipt/', views.fee_receipt_pdf, name='fee_receipt'),
    path('fee-payment/', views.fee_payment_view, name='fee_payment'),
    path('payment-success/', views.payment_success, name='payment_success'),
]