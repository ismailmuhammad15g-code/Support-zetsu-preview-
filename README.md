# ZetsuServ Support Portal

A professional Flask web application for support ticket management with Microsoft Fluent Design.

![Version](https://img.shields.io/badge/version-4.0.0-blue)
![Python](https://img.shields.io/badge/python-3.7+-blue)
![Flask](https://img.shields.io/badge/flask-3.0.0-green)

## 🎯 Key Features

### Ticket Management
- **Submit Support Tickets** - Easy form with file attachments (up to 5MB)
- **Track Tickets** - Search by ticket ID or email
- **Priority Levels** - Low, Medium, High, Urgent
- **Multiple Issue Types** - Technical Support, Billing, Bug Reports, Feature Requests, etc.
- **Email Notifications** - Automatic confirmations and responses

### Admin Dashboard (Protected)
- **View All Tickets** - Comprehensive ticket overview
- **Advanced Filtering** - Filter by status, priority, and issue type
- **Reply to Tickets** - Respond directly and auto-mark as resolved
- **Bulk Operations** - Resolve multiple tickets at once
- **CSV Export** - Export ticket data for reporting
- **File Management** - Clean up orphaned attachments

### Authentication & Registration
- **Open Registration** - Anyone can register with email OTP verification
- **Secure Login** - Password hashing with Flask-Login
- **Admin Privileges** - Auto-granted to `zetsuserv@gmail.com`
- **Newsletter Subscription** - Optional opt-in for updates

### Design
- **Microsoft Fluent Design** - Professional, modern interface
- **Responsive Layout** - Works on desktop, tablet, and mobile
- **Toast Notifications** - Beautiful glassmorphism alerts

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Local Development

1. **Clone and setup:**
```bash
git clone https://github.com/ismailmuhammad15g-code/Support-zetsu-preview-.git
cd Support-zetsu-preview-
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Set environment variables (optional):**
```bash
export SECRET_KEY=your-secret-key-here
export SENDER_EMAIL=your-email@gmail.com
export EMAIL_PASSWORD=your-app-password
export SMTP_SERVER=smtp.gmail.com
export SMTP_PORT=587
```

3. **Run the application:**
```bash
python flask_app.py
```

4. **Access the app:**
```
http://127.0.0.1:5000
```

## 🌐 Deployment on PythonAnywhere

### Step-by-Step

1. **Upload your project:**
   - Clone from GitHub or upload files via the Files tab

2. **Install dependencies:**
```bash
cd ~/Support-zetsu-preview-
pip3 install --user -r requirements.txt
```

3. **Create Web App:**
   - Go to Web tab → Add new web app
   - Choose Manual configuration
   - Select Python 3.10+

4. **Configure WSGI file:**
```python
import sys
import os

project_home = '/home/yourusername/Support-zetsu-preview-'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Generate a secure key: import secrets; print(secrets.token_hex(32))
os.environ['SECRET_KEY'] = 'your-generated-secret-key'

# Optional: Email configuration
# os.environ['SENDER_EMAIL'] = 'your-email@gmail.com'
# os.environ['EMAIL_PASSWORD'] = 'your-app-password'

from flask_app import app as application
```

5. **Configure static files:**
   - URL: `/static/`
   - Directory: `/home/yourusername/Support-zetsu-preview-/static/`

6. **Create uploads directory:**
```bash
mkdir -p ~/Support-zetsu-preview-/uploads
chmod 755 ~/Support-zetsu-preview-/uploads
```

7. **Reload the web app** from the Web tab

### First-Time Admin Setup
1. Visit `yourusername.pythonanywhere.com/register`
2. Register with email: `zetsuserv@gmail.com`
3. Verify with OTP code (check email or console if email not configured)
4. Login at `/login`
5. Access dashboard to manage tickets

## 🔧 Troubleshooting

### Common Issues

**Database errors:**
```bash
# Delete and recreate database
rm ~/Support-zetsu-preview-/support_tickets.db
# Then reload web app
```

**Static files not loading:**
- Verify static files path in Web tab
- Hard refresh browser (Ctrl+Shift+R)

**Email not working:**
- App works without email (tickets still saved)
- For Gmail, use App-Specific Password
- Set environment variables in WSGI file

**Health check:**
Visit `/health` endpoint to diagnose issues

## 📦 Dependencies

Core: Flask 3.0.0, SQLAlchemy 2.0.23, Flask-Login 0.6.3, Flask-WTF 1.2.1

See `requirements.txt` for complete list.

## 🔐 Security Features

- ✅ CSRF Protection on all forms
- ✅ Email OTP verification for registration  
- ✅ Password hashing (Werkzeug PBKDF2)
- ✅ XSS protection (Jinja2 auto-escaping)
- ✅ SQL injection protection (SQLAlchemy ORM)
- ✅ Secure file upload handling
- ✅ Session security

## 📄 License

All rights reserved © 2024 ZetsuServ

## 👨‍💻 Author

Created by ismailmuhammad15g-code for ZetsuServ Support Portal

## 📞 Support

- GitHub Issues: [Report a bug](https://github.com/ismailmuhammad15g-code/Support-zetsu-preview-/issues)
- Submit a ticket through the application

