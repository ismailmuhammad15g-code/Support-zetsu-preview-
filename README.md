# ZetsuServ Support Portal

A professional, enterprise-grade Flask web application for comprehensive support ticket management, styled with Microsoft Fluent Design System.

![Version](https://img.shields.io/badge/version-3.0.0-blue)
![Python](https://img.shields.io/badge/python-3.7+-blue)
![Flask](https://img.shields.io/badge/flask-3.0.0-green)
![License](https://img.shields.io/badge/license-MIT-green)

## 🎯 Features

### Core Functionality
- **Professional Landing Page** - Hero section with call-to-action and feature highlights
- **Support Ticket System** - Complete ticket submission with validation and tracking
- **Admin Dashboard** - Secure admin panel for managing and responding to tickets
- **Authentication System** - Flask-Login based authentication with whitelist security
- **Database Integration** - SQLAlchemy ORM with SQLite/PostgreSQL support
- **Email Notifications** - Automated confirmation emails with ticket details and admin replies
- **File Attachments** - Support for documents, images, and text files (up to 5MB)
- **Ticket Tracking** - Search and view tickets by ID or email
- **FAQ System** - Comprehensive FAQ database with categories
- **About Page** - Company information and technology stack details

### Admin Features
- **Secure Login/Registration** - Whitelist-based admin registration (zetsuserv@gmail.com only)
- **Ticket Management** - View all tickets with real-time statistics
- **Reply System** - Respond to tickets and automatically mark as resolved
- **Email Notifications** - Send automated replies to users via email
- **Status Tracking** - Visual badges for Open (green) and Resolved (gray) tickets
- **Responsive Dashboard** - Data table on desktop, card layout on mobile

### Technical Features
- **Microsoft Fluent Design** - Clean, professional UI with Microsoft design principles
- **Responsive Design** - Optimized for desktop, tablet, and mobile devices
- **Server-side Validation** - Comprehensive input validation for security
- **Database Models** - User, Ticket, and FAQ models with relationships
- **Priority System** - Low, Medium, High, and Urgent priority levels
- **Status Tracking** - Open, In Progress, Resolved ticket statuses
- **Flash Messages** - User-friendly feedback for form submissions
- **Secure File Upload** - File type and size validation
- **Password Hashing** - Werkzeug password hashing for secure authentication
- **Session Management** - Flask-Login session handling with "Remember Me"
- **Console Logging** - Debug output for ticket submissions

## 📁 Project Structure

```
Support-zetsu-preview-/
├── flask_app.py              # Main Flask application with routes
├── requirements.txt          # Python dependencies
├── support_tickets.db        # SQLite database (auto-created)
├── templates/
│   ├── home.html            # Landing page
│   ├── support.html         # Support ticket form
│   ├── track.html           # Ticket tracking page
│   ├── faq.html             # FAQ page
│   ├── about.html           # About page
│   ├── login.html           # Admin login page
│   ├── register.html        # Admin registration page
│   └── dashboard.html       # Admin dashboard
├── static/
│   └── style.css            # Microsoft Fluent Design CSS
├── uploads/                 # File attachment storage (auto-created)
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Local Development

1. **Clone the repository:**
```bash
git clone https://github.com/ismailmuhammad15g-code/Support-zetsu-preview-.git
cd Support-zetsu-preview-
```

2. **Create and activate virtual environment:**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set environment variables (optional for email):**
```bash
# Windows
set SECRET_KEY=your-secret-key-here
set SMTP_SERVER=smtp.gmail.com
set SMTP_PORT=587
set SENDER_EMAIL=your-email@gmail.com
set EMAIL_PASSWORD=your-app-password

# macOS/Linux
export SECRET_KEY=your-secret-key-here
export SMTP_SERVER=smtp.gmail.com
export SMTP_PORT=587
export SENDER_EMAIL=your-email@gmail.com
export EMAIL_PASSWORD=your-app-password
```

5. **Run the application:**
```bash
python flask_app.py
```

6. **Open your browser:**
```
http://127.0.0.1:5000
```

## 🌐 Production Deployment

### PythonAnywhere Deployment

#### Step 1: Upload Files

1. Log in to your PythonAnywhere account
2. Go to "Files" tab
3. Upload all project files maintaining the directory structure
4. Ensure `uploads/` directory is created

#### Step 2: Install Dependencies

Open a Bash console and run:
```bash
cd ~/Support-zetsu-preview-
pip3 install --user -r requirements.txt
```

#### Step 3: Create Web App

1. Go to "Web" tab
2. Click "Add a new web app"
3. Choose "Manual configuration"
4. Select Python 3.10 or later
5. Set the source code directory to `/home/yourusername/Support-zetsu-preview-`

#### Step 4: Configure WSGI

Click on the WSGI configuration file link and replace its contents with:

```python
import sys
import os

# Add your project directory to sys.path
project_home = '/home/yourusername/Support-zetsu-preview-'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables
os.environ['SECRET_KEY'] = 'your-secure-secret-key-here'
os.environ['DATABASE_URL'] = 'sqlite:///support_tickets.db'

# Optional: Email configuration
# os.environ['SMTP_SERVER'] = 'smtp.gmail.com'
# os.environ['SMTP_PORT'] = '587'
# os.environ['SENDER_EMAIL'] = 'your-email@gmail.com'
# os.environ['EMAIL_PASSWORD'] = 'your-app-password'

# Import Flask app
from flask_app import app as application
```

#### Step 5: Configure Static Files

In the Web tab, add static file mappings:
- URL: `/static/`
- Directory: `/home/yourusername/Support-zetsu-preview-/static/`

#### Step 6: Reload and Test

1. Click "Reload" on the Web tab
2. Visit your PythonAnywhere URL
3. Test all features

### Environment Variables

**Required:**
- `SECRET_KEY` - Flask secret key for sessions (generate with `secrets.token_hex(32)`)

**Optional (for email notifications):**
- `SMTP_SERVER` - SMTP server address (default: smtp.gmail.com)
- `SMTP_PORT` - SMTP server port (default: 587)
- `SENDER_EMAIL` - Email address for sending notifications
- `EMAIL_PASSWORD` - Email password or app-specific password

**Database:**
- `DATABASE_URL` - Database connection string (default: sqlite:///support_tickets.db)

## 🔐 Admin Setup

### First-Time Admin Registration

1. **Navigate to Registration Page:**
   - Visit `/register` or click "Login" → "Register here"

2. **Whitelist Validation:**
   - Only the email `zetsuserv@gmail.com` is allowed to register as admin
   - Any other email will be rejected with: "Access Denied: Admin whitelist only."

3. **Create Admin Account:**
   - Enter the whitelisted email: `zetsuserv@gmail.com`
   - Create a strong password (minimum 8 characters)
   - Confirm your password
   - Click "Create Admin Account"

4. **Login:**
   - After successful registration, you'll be redirected to the login page
   - Enter your credentials and click "Sign In"
   - You'll be redirected to the admin dashboard

### Using the Admin Dashboard

**Dashboard Features:**
- **Statistics Cards:** View Open, Resolved, and Total ticket counts
- **Ticket Table (Desktop):** Full table view with all ticket details
- **Ticket Cards (Mobile):** Stacked card layout for mobile devices
- **Status Badges:** 
  - Green "Open" badge for unresolved tickets
  - Gray "Resolved" badge for resolved tickets
- **Priority Badges:** Color-coded for Low, Medium, High, and Urgent

**Responding to Tickets:**
1. Click "View" button on any Open ticket
2. Review the ticket message and details
3. Type your response in the reply textarea
4. Click "Send Reply & Mark as Resolved"
5. The system will:
   - Save your reply to the database
   - Update ticket status to "Resolved"
   - Send an email to the user with your response (if SMTP is configured)

**Logout:**
- Click "Logout" in the navigation to end your session

## 📝 Routes & Endpoints

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Landing page with hero section |
| `/support` | GET | Support form page |
| `/submit` | POST | Form submission handler |
| `/track` | GET | Ticket tracking page |
| `/search_ticket` | POST | Search tickets by ID or email |
| `/faq` | GET | FAQ page with categories |
| `/about` | GET | About page |
| `/login` | GET, POST | Admin login page |
| `/register` | GET, POST | Admin registration (whitelist only) |
| `/logout` | GET | Logout and end session |
| `/dashboard` | GET | Admin dashboard (protected) |
| `/reply_ticket/<id>` | POST | Reply to ticket and mark resolved (protected) |

## 🎨 Design System

### Microsoft Fluent Design

#### Colors
- **Primary Blue**: #0078D4 (Microsoft Blue)
- **Background**: #FFFFFF, #FAF9F8, #F3F2F1 (White/Light Gray)
- **Text**: #201F1E (Dark Gray), #323130 (Secondary)
- **Success**: #107C10 (Green)
- **Error**: #A80000 (Red)

#### Typography
- **Font Family**: Segoe UI, -apple-system, BlinkMacSystemFont
- **Weights**: Regular (400), Semibold (600), Bold (700)
- **Sizes**: 12px - 42px responsive scaling

#### Components
- Cards with depth shadows
- Fluent Design input fields
- Responsive navigation bar
- Success/error flash messages
- Status and priority badges

## 🗄️ Database Models

### User Model
```python
- id: Integer (Primary Key)
- email: String(254) (Unique)
- password_hash: String(256)
- is_admin: Boolean
- created_at: DateTime
```

### Ticket Model
```python
- id: Integer (Primary Key)
- ticket_id: String(20) (Unique, e.g., ZS-20241217-ABC123)
- name: String(100)
- email: String(254)
- issue_type: String(50)
- priority: String(20) [Low, Medium, High, Urgent]
- message: Text
- status: String(20) [Open, In Progress, Resolved]
- attachment_filename: String(255) (Optional)
- admin_reply: Text (Optional)
- created_at: DateTime
- updated_at: DateTime
```

### FAQ Model
```python
- id: Integer (Primary Key)
- question: String(500)
- answer: Text
- category: String(50)
- order: Integer
- created_at: DateTime
```

## 🔒 Security Features

### Current Implementation
- ✅ Server-side input validation
- ✅ Jinja2 auto-escaping (XSS protection)
- ✅ Input sanitization
- ✅ Secure file upload handling
- ✅ File type and size validation
- ✅ SQL injection protection (SQLAlchemy ORM)
- ✅ Email XSS prevention
- ✅ Password hashing (Werkzeug PBKDF2)
- ✅ Session management (Flask-Login)
- ✅ Admin whitelist (zetsuserv@gmail.com only)
- ✅ Protected routes (@login_required decorator)
- ⚠️ Debug mode enabled (development only)

### Production Recommendations
1. **SECRET_KEY** - Use strong random value (never commit to git)
2. **Debug Mode** - Set `debug=False` in production
3. **HTTPS** - Enable SSL/TLS (automatic on PythonAnywhere)
4. **CSRF Protection** - Implement Flask-WTF forms
5. **Rate Limiting** - Add Flask-Limiter
6. **Input Validation** - Already implemented
7. **Database Backups** - Regular automated backups
8. **Email Security** - Use app-specific passwords
9. **Session Security** - Configure secure session cookies in production

## 📊 Features Breakdown

### Ticket Priority Levels
- **Low** - General inquiries, non-urgent questions
- **Medium** - Standard support requests (default)
- **High** - Issues affecting operations
- **Urgent** - Critical issues requiring immediate attention

### Ticket Status Types
- **Open** - Newly submitted, awaiting review
- **In Progress** - Being worked on by support team
- **Resolved** - Issue has been resolved

### Supported File Types
- Documents: `.pdf`, `.doc`, `.docx`
- Images: `.png`, `.jpg`, `.jpeg`, `.gif`
- Text: `.txt`
- Maximum size: 5MB per file

## 🧪 Testing

### Manual Testing Checklist
- [x] Home page loads correctly
- [x] Navigation links work
- [x] Support form submission
- [x] Form validation (required fields)
- [x] Email format validation
- [x] File upload functionality
- [x] Ticket tracking by ID
- [x] Ticket tracking by email
- [x] FAQ page displays correctly
- [x] About page displays correctly
- [x] Responsive design on mobile
- [x] Admin registration (whitelist validation)
- [x] Admin login/logout
- [x] Admin dashboard access
- [x] Ticket reply functionality
- [x] Status update (Open to Resolved)
- [ ] Email notifications (if configured)

### Test Data
Sample tickets are automatically created when you submit forms. Use the Track Ticket page to view them.

## 📦 Dependencies

### Core
- **Flask** (3.0.0) - Web framework
- **Werkzeug** (3.0.1) - WSGI utilities
- **Jinja2** (3.1.2) - Template engine

### Database
- **Flask-SQLAlchemy** (3.1.1) - Database ORM
- **SQLAlchemy** (2.0.23) - SQL toolkit

### Authentication & Security
- **Flask-Login** (0.6.3) - User session management
- **Flask-WTF** (1.2.1) - Form handling
- **WTForms** (3.1.1) - Form validation
- **itsdangerous** (2.1.2) - Security helpers
- **email-validator** (2.1.1) - Email validation

### Additional
- **python-dateutil** (2.8.2) - Date utilities
- **python-dotenv** (1.0.0) - Environment variables
- **Pillow** (10.1.0) - Image processing
- **gunicorn** (21.2.0) - WSGI server

### Development (Optional)
- **pytest** (7.4.3) - Testing framework
- **pytest-flask** (1.3.0) - Flask testing utilities

## 🤝 Contributing

Contributions are welcome! This is a production-ready application with room for enhancements:

### Potential Enhancements
- ✅ Admin dashboard for ticket management (Implemented)
- ✅ User authentication system (Implemented)
- Advanced search and filtering
- Ticket assignment to team members
- Internal notes and comments
- Email templates customization
- Multi-language support
- Analytics and reporting
- Real-time notifications
- API endpoints for integrations

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

All rights reserved © 2024 ZetsuServ

## 👨‍💻 Author

Created for ZetsuServ Support Portal project by ismailmuhammad15g-code

## 📞 Support

For issues, questions, or contributions:
- GitHub Issues: [Report a bug](https://github.com/ismailmuhammad15g-code/Support-zetsu-preview-/issues)
- Submit a ticket through the application
- Email: Contact via support form

## 🔄 Changelog

### Version 3.0.0 (Current)
- ✨ **NEW:** Flask-Login authentication system
- ✨ **NEW:** Admin registration with whitelist security (zetsuserv@gmail.com only)
- ✨ **NEW:** Admin login/logout functionality
- ✨ **NEW:** Secure admin dashboard with @login_required protection
- ✨ **NEW:** User model with password hashing
- ✨ **NEW:** Reply system for responding to tickets
- ✨ **NEW:** Automatic status update (Open → Resolved)
- ✨ **NEW:** Admin reply email notifications
- ✨ **NEW:** Responsive dashboard (table on desktop, cards on mobile)
- ✨ **NEW:** Visual status badges (green for Open, gray for Resolved)
- ✨ **NEW:** Priority badges with color coding
- ✨ **NEW:** Dashboard statistics (Open, Resolved, Total)
- 🔧 Updated Ticket model with admin_reply column
- 🔧 Updated all templates with conditional Login/Dashboard/Logout links
- 🔧 Enhanced CSS with authentication and dashboard styles
- 📝 Comprehensive README update with admin setup guide

### Version 2.0.0
- ✨ Complete redesign with Microsoft Fluent Design System
- ✨ Added SQLAlchemy database integration
- ✨ Added file upload support
- ✨ Added ticket tracking system
- ✨ Added FAQ page with sample data
- ✨ Added About page
- ✨ Added priority levels for tickets
- ✨ Enhanced email templates
- ✨ Improved form validation
- ✨ Added flash message system
- ✨ Mobile responsive improvements
- 📝 Updated comprehensive documentation

### Version 1.0.0
- Initial release with Glassmorphism design
- Basic ticket submission
- Email notifications
- Simple console logging

---

**Built with ❤️ using Flask and Microsoft Fluent Design System**
