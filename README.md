# ZetsuServ Support Portal

A professional, production-ready Flask web application for enterprise support solutions, styled with Microsoft Fluent Design System.

## 🎯 Features

- **Professional Landing Page** - Hero section with call-to-action
- **Support Ticket Form** - Clean, intuitive form interface
- **Microsoft Fluent Design** - Clean white/light gray theme with Segoe UI
- **Responsive Design** - Works on desktop and mobile devices
- **Input Validation** - Server-side validation for security
- **Console Logging** - Prints submitted tickets to console (pre-database implementation)

## 📁 Project Structure

```
Support-zetsu-preview-/
├── flask_app.py          # Main Flask application
├── templates/
│   ├── home.html         # Landing page
│   └── support.html      # Support form page
├── static/
│   └── style.css         # Microsoft Fluent Design CSS
└── README.md
```

## 🚀 Local Development

### Prerequisites

- Python 3.7+
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/ismailmuhammad15g-code/Support-zetsu-preview-.git
cd Support-zetsu-preview-
```

2. Install Flask:
```bash
pip install flask
```

3. Run the application:
```bash
python flask_app.py
```

4. Open your browser and navigate to:
```
http://127.0.0.1:5000
```

## 🌐 PythonAnywhere Deployment

### Step 1: Upload Files

1. Log in to your PythonAnywhere account
2. Go to "Files" tab
3. Upload all files maintaining the directory structure

### Step 2: Create Web App

1. Go to "Web" tab
2. Click "Add a new web app"
3. Choose "Flask" and Python version
4. Set the path to `flask_app.py`

### Step 3: Configure WSGI

Edit the WSGI configuration file:

```python
import sys
path = '/home/yourusername/Support-zetsu-preview-'
if path not in sys.path:
    sys.path.append(path)

from flask_app import app as application
```

### Step 4: Set Environment Variables

**IMPORTANT**: Change the SECRET_KEY before deployment!

Generate a secure key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

In your `flask_app.py`, update line 15:
```python
app.config['SECRET_KEY'] = 'your-generated-secure-key-here'
```

### Step 5: Reload and Test

1. Click "Reload" on the Web tab
2. Visit your PythonAnywhere URL
3. Test the support form submission

## 📝 Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Landing page with hero section |
| `/support` | GET | Support form page |
| `/submit` | POST | Form submission handler |

## 🎨 Design System

### Colors
- **Primary Blue**: #0078D4 (Microsoft Blue)
- **Background**: #F3F3F3 (Light Gray)
- **Text**: #1F1F1F (Dark Gray)
- **Success**: #107C10 (Green)

### Typography
- **Font Family**: Segoe UI, Tahoma, Geneva, Verdana, sans-serif
- **Border Radius**: 4px-8px (rounded corners)

### Components
- Cards with subtle shadows
- Professional form inputs
- Responsive navigation bar
- Success/error alerts

## 🔒 Security Notes

### Current Implementation
- ✅ Server-side input validation
- ✅ Jinja2 auto-escaping (XSS protection)
- ✅ Input sanitization
- ⚠️ Debug mode enabled (development only)
- ⚠️ No database yet (prints to console)

### Production Recommendations
1. **Change SECRET_KEY** to a secure random value
2. **Disable debug mode** (automatic when using WSGI on PythonAnywhere)
3. **Add CSRF protection** (install Flask-WTF)
4. **Implement database** for ticket storage
5. **Add email notifications** for support team
6. **Enable HTTPS** (automatic on PythonAnywhere)
7. **Add rate limiting** to prevent abuse

## 📊 Form Submission Flow

1. User fills out the support form
2. Client-side validation (HTML5 required attributes)
3. Form submits via POST to `/submit`
4. Server-side validation checks all fields
5. Data printed to console (for debugging)
6. Success message displayed to user
7. Form ready for new submission

## 🧪 Testing

Test the application by:
1. Navigating to the home page
2. Clicking "Contact Support"
3. Filling out the form completely
4. Submitting the form
5. Verifying success message appears
6. Checking console output for printed data

## 📦 Dependencies

- **Flask** (3.1.2+) - Web framework
- **Werkzeug** (3.1.0+) - WSGI utilities
- **Jinja2** (3.1.2+) - Template engine

## 🤝 Contributing

This is a production-ready MVP. Future enhancements:
- Database integration (SQLite/PostgreSQL)
- Email notifications
- Admin dashboard
- Ticket tracking system
- CSRF protection
- Rate limiting

## 📄 License

All rights reserved © 2024 ZetsuServ

## 👨‍💻 Author

Created for ZetsuServ Support Portal project
