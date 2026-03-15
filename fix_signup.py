content = open('home/views.py').read()

old = """            user = form.save(commit=False)
            user.is_active = False
            user.save()
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            verification_link = request.build_absolute_uri(f"/verify-email/{uid}/{token}/")
            send_mail(
                subject="Verify Your Email - Univio",
                message=f"Click the link below to verify your email:\\n\\n{verification_link}\\n\\nIf you did not create this account, please ignore this email.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )
            messages.success(request, "Account created! Check your email to verify your account.")
            return redirect('login')"""

new = """            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully! Welcome to Univio.")
            return redirect('home')"""

if old in content:
    content = content.replace(old, new)
    open('home/views.py', 'w').write(content)
    print('Fixed!')
else:
    print('Pattern not found')
