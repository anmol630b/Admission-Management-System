# 🎓 Univio - Admission Management System

A modern web-based admission management system built with Django.

## ✨ Features

- 🏠 Beautiful home page with animations
- 📝 Online admission form
- 👤 Student dashboard
- 📊 Results & attendance tracking
- 📅 Timetable management
- 🔔 Notice board
- 💳 Fee payment (Razorpay)
- 📧 OTP login via email
- 🔐 Secure authentication
- 📱 Fully responsive design

## 🛠️ Tech Stack

- **Backend:** Django (Python)
- **Frontend:** HTML, CSS, Bootstrap 5
- **Database:** SQLite
- **Admin:** Jazzmin
- **Payment:** Razorpay

## 🚀 Setup
```bash
# Clone karo
git clone https://github.com/anmol630b/Admission-Management-System.git
cd Admission-Management-System

# Dependencies install karo
pip install -r requirements.txt

# .env file banao
cp .env.example .env
# .env mein apni keys daalo

# Database migrate karo
python manage.py migrate

# Server chalao
python manage.py runserver
```

## ⚙️ Environment Variables

`.env` file mein yeh variables daalo:
```
SECRET_KEY=your-secret-key
DEBUG=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
RAZORPAY_KEY_ID=your-razorpay-key
RAZORPAY_KEY_SECRET=your-razorpay-secret
```

## 📸 Pages

- `/` - Home
- `/admission` - Admission Form
- `/about` - About Us
- `/contact` - Contact
- `/login` - Login
- `/dashboard` - Student Dashboard
- `/admin` - Admin Panel

## 👨‍💻 Developer

Made with ❤️ by Anmol
