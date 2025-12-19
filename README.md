# ZetsuServ Support Portal

A professional, enterprise-grade Flask web application for comprehensive support ticket management with **Hybrid Human-AI Support System**, styled with Microsoft Fluent Design System.

![Version](https://img.shields.io/badge/version-3.5.0-blue)
![Python](https://img.shields.io/badge/python-3.7+-blue)
![Flask](https://img.shields.io/badge/flask-3.0.0-green)
![AI](https://img.shields.io/badge/AI-Gemini%201.5%20Flash-orange)
![License](https://img.shields.io/badge/license-MIT-green)

## 🎯 Features

### 🆕 Latest Updates (v3.5.0) - Multimodal AI Vision Support 🖼️

#### 🎨 Multimodal Vision Features
- **👁️ AI Image Analysis** - AI can now read and analyze image attachments (screenshots, error messages, diagrams)
- **🖼️ Vision-Powered Support** - Gemini 1.5 Flash analyzes images alongside text for comprehensive problem understanding
- **📸 Smart Error Detection** - AI reads error screenshots to provide accurate technical solutions
- **🔄 Automatic Image Processing** - Seamlessly handles .jpg, .png, .jpeg, .gif files with vision AI
- **💡 Enhanced AI Drafts** - Every ticket gets an AI-drafted response, whether admin is available or not
- **⚡ Model Upgrade** - Switched to Gemini 1.5 Flash for better free-tier stability and faster responses

#### 🤖 AI Logic Improvements
- **✅ Fixed Auto-Response** - AI now correctly responds when `is_available=False`
- **🎯 Universal AI Drafts** - AI suggestions generated for ALL tickets regardless of admin status
- **🛡️ Enhanced Error Handling** - Comprehensive try/except blocks prevent API failures from crashing the app
- **📊 Better Logging** - Improved logging for AI operations and troubleshooting
- **🔐 Secure Image Handling** - Proper file path validation and error recovery

### Previous Updates (v3.4.0) - Hybrid Human-AI Support System 🤖

#### 🧠 AI-Powered Features
- **🤖 Gemini AI Integration** - Powered by Google's Gemini for intelligent responses
- **🎯 Hybrid Support Logic** - AI automatically handles tickets when admin is unavailable
- **💡 AI Response Suggestions** - Get AI-drafted responses for every ticket
- **📊 Sentiment Analysis** - Auto-detects urgent/angry keywords and escalates priority
- **✨ Smart Auto-Response** - AI replies to users when admin is offline
- **🔄 Availability Toggle** - Modern switch to control when AI takes over

#### 🎛️ Admin Dashboard Enhancements
- **🟢 Availability Switch** - Toggle your availability status with no-redirect design
- **📝 AI Suggested Responses** - See AI-generated drafts for every open ticket
- **🚀 One-Click AI Use** - Copy AI suggestions into reply field instantly
- **🎨 Modern Toggle UI** - Fluent Design toggle with smooth animations
- **📈 Smart Priority Escalation** - Keywords like "urgent" auto-promote to High Priority

#### 🛡️ Safety & Reliability
- **✅ No Redirect Loops** - AJAX-based toggle prevents ERR_TOO_MANY_REDIRECTS
- **🔐 Secure API Integration** - Environment-based API key configuration
- **📊 Comprehensive Logging** - Track AI responses and admin availability changes
- **🎯 FAQ Context Integration** - AI uses your FAQ database for accurate answers
- **⚠️ Sentiment Detection** - Detects: angry, urgent, critical, emergency, ASAP, and more

### Previous Updates (v3.3.0)

- **📤 File Upload Progress** - Microsoft-style upload progress with real-time visual feedback
- **⏳ Submit Button Loading** - Loading spinner when submitting forms
- **🗑️ Admin File Management** - Clear unused attachments and delete individual tickets
- **🔒 CSRF Protection** - Complete Cross-Site Request Forgery protection on all forms
- **✅ Enhanced Validation** - Client-side file size and type validation
- **🎨 Improved UX** - Success indicators for file uploads with visual feedback
- **🛡️ Security Hardening** - Additional security measures throughout the application

### Previous Updates (v3.2.0)

- **🔗 Webhook Integration** - Automated ticket submission to n8n or other automation platforms
- **🌅 Dynamic Greetings** - Time-aware greetings that change throughout the day
- **✨ Glassmorphism Toasts** - Modern notification system with smooth animations
- **🎨 Interactive Animations** - Shimmer effects and enhanced button interactions
- **📱 Mobile FAB Button** - Floating action button for easy mobile access
- **⚡ Skeleton Loaders** - Professional loading states for better UX

### 🎫 Ticket Management System

#### For Users (Public Access)
- **Submit Support Tickets** - Easy-to-use form with validation
- **File Upload with Progress** - Real-time upload progress indicator for attachments
- **Multiple Issue Types** - Technical Support, Billing, Bug Reports, Feature Requests, etc.
- **Priority Levels** - Mark tickets as Low, Medium, High, or Urgent
- **🤖 AI Auto-Response** - Get instant AI-powered responses when admin is unavailable
- **📊 Smart Escalation** - Urgent keywords automatically escalate your ticket
- **File Attachments** - Upload documents, images, or text files (up to 5MB)
- **Client-side Validation** - Instant feedback on file size and type before upload
- **Ticket Tracking** - Search and view your tickets by ID or email
- **Email Confirmations** - Receive automatic confirmation emails with ticket details
- **Unique Ticket IDs** - Every ticket gets a unique ID (format: ZS-YYYYMMDD-XXXXXX)

#### For Admins (Protected Access)
- **Secure Dashboard** - Login-protected admin panel
- **🟢 Availability Toggle** - Control when AI handles tickets vs. human response
- **💡 AI Draft Suggestions** - See AI-generated response drafts for every ticket
- **View All Tickets** - See all submitted tickets in one place
- **Advanced Filtering** - Filter tickets by status, priority, and issue type
- **Real-time Statistics** - View counts for Open, Resolved, Urgent, and High Priority tickets
- **Reply to Tickets** - Respond directly to users and auto-mark as resolved
- **Bulk Operations** - Select and resolve multiple tickets at once
- **Delete Tickets** - Remove individual tickets with their attachments
- **Clear Unused Files** - One-click cleanup of orphaned attachment files
- **CSV Export** - Export all ticket data to CSV for reporting
- **Email Notifications** - Automated email replies to users with your responses (optional)
- **Email Status Indicator** - Dashboard shows if email is configured with helpful setup instructions
- **Image Attachments Preview** - View uploaded images inline in the dashboard
- **Secure File Access** - Admin-only access to uploaded files with download option
- **Detailed Error Messages** - Clear feedback when email or other features fail

### 🔐 Authentication & Security

- **CSRF Protection** - Cross-Site Request Forgery protection on all forms
- **Whitelist-Based Registration** - Only authorized emails can create admin accounts
- **Secure Login System** - Password hashing with Werkzeug PBKDF2
- **Session Management** - Flask-Login with "Remember Me" option
- **Protected Routes** - Admin pages require authentication
- **Hidden Login Access** - Login page accessible only via direct URL (no navigation links)
- **Input Validation** - Server-side validation for all forms
- **SQL Injection Protection** - SQLAlchemy ORM prevents SQL injection
- **XSS Protection** - Automatic Jinja2 escaping for all outputs

### 📊 Dashboard Features (Admin Only)

- **Statistics Cards** - Quick overview of ticket metrics
  - Open Tickets count
  - Resolved Tickets count
  - Total Tickets count
  - Urgent Priority count
  - High Priority count

- **Filter & Search**
  - Filter by Status (All, Open, Resolved)
  - Filter by Priority (All, Low, Medium, High, Urgent)
  - Filter by Issue Type (All types)
  - Apply and clear filters easily

- **Bulk Actions**
  - Select multiple tickets with checkboxes
  - "Select All" option
  - Bulk resolve selected tickets
  - Confirmation dialogs for safety

- **Export Capabilities**
  - Download all tickets as CSV
  - Timestamped filenames
  - Complete ticket data included

- **Responsive Design**
  - Desktop: Full data table view
  - Mobile: Card-based layout
  - Touch-friendly controls

### 🎨 Design & User Experience

- **Microsoft Fluent Design System** - Professional, modern interface
- **Responsive Layout** - Works on desktop, tablet, and mobile
- **Color-Coded Badges** - Visual status and priority indicators
- **Flash Messages** - User-friendly feedback for all actions
- **Navigation Bar** - Easy access to all pages
- **Professional Typography** - Segoe UI font family

### 🗄️ Data Management

- **SQLAlchemy ORM** - Modern database integration
- **SQLite Database** - Default local database (can use PostgreSQL)
- **Automatic Migrations** - Database tables created automatically
- **Sample FAQ Data** - Pre-populated FAQ content
- **File Upload Storage** - Organized uploads directory

### 📧 Email Integration (Optional)

- **SMTP Support** - Send emails via Gmail or other SMTP servers
- **Ticket Confirmations** - Users receive confirmation emails
- **Admin Notifications** - Admins notified of new tickets
- **Reply Notifications** - Users notified when admin responds
- **HTML Email Templates** - Beautiful, branded email design

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

4. **Set environment variables (optional for email and webhook):**
```bash
# Windows
set SECRET_KEY=your-secret-key-here
set N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/your-id
set SMTP_SERVER=smtp.gmail.com
set SMTP_PORT=587
set SENDER_EMAIL=your-email@gmail.com
set EMAIL_PASSWORD=your-app-password

# macOS/Linux
export SECRET_KEY=your-secret-key-here
export N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/your-id
export SMTP_SERVER=smtp.gmail.com
export SMTP_PORT=587
export SENDER_EMAIL=your-email@gmail.com
export EMAIL_PASSWORD=your-app-password
```

**Note:** The `N8N_WEBHOOK_URL` is optional (new in v3.2.0). The app works perfectly without it.

5. **Run the application:**
```bash
python flask_app.py
```

6. **Open your browser:**
```
http://127.0.0.1:5000
```

## 🌐 Hosting & Deployment

### Option 1: PythonAnywhere (Recommended - Free Tier Available)

PythonAnywhere is the easiest way to host this Flask application with a free tier perfect for testing and small projects.

#### Prerequisites
- PythonAnywhere account (sign up at [pythonanywhere.com](https://www.pythonanywhere.com))
- Your project files ready for upload

#### Step-by-Step Deployment

**1. Upload Your Project**
1. Log in to your PythonAnywhere account
2. Go to the **"Files"** tab
3. Click **"Upload a file"** and upload your project as a ZIP file, OR
4. Clone from GitHub:
   - Open a **Bash console**
   - Run: `git clone https://github.com/ismailmuhammad15g-code/Support-zetsu-preview-.git`
   - Navigate: `cd Support-zetsu-preview-`

**2. Install Dependencies**
1. Open a **Bash console** from the Consoles tab
2. Navigate to your project directory:
   ```bash
   cd ~/Support-zetsu-preview-
   ```
3. Install required packages:
   ```bash
   pip3 install --user -r requirements.txt
   ```
4. Wait for installation to complete (may take 2-3 minutes)

**3. Create the Web App**
1. Go to the **"Web"** tab
2. Click **"Add a new web app"**
3. Choose your domain (e.g., `yourusername.pythonanywhere.com`)
4. Select **"Manual configuration"** (do NOT choose Flask)
5. Select **Python 3.10** or later
6. Click through to complete setup

**4. Configure WSGI File**
1. On the Web tab, find the **"Code"** section
2. Click on the WSGI configuration file link (e.g., `/var/www/yourusername_pythonanywhere_com_wsgi.py`)
3. Delete all existing content
4. Paste the following configuration:

```python
import sys
import os

# Add your project directory to sys.path
project_home = '/home/yourusername/Support-zetsu-preview-'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# IMPORTANT: Set your SECRET_KEY - Generate a new one for production!
# Run in Python console: import secrets; print(secrets.token_hex(32))
os.environ['SECRET_KEY'] = 'REPLACE-WITH-YOUR-SECRET-KEY-HERE'

# Database configuration (SQLite will be created automatically)
os.environ['DATABASE_URL'] = 'sqlite:///support_tickets.db'

# Optional: Webhook integration for n8n automation (New in v3.2.0)
# Uncomment and configure if you want webhook automation
# os.environ['N8N_WEBHOOK_URL'] = 'https://your-n8n-instance.com/webhook/your-webhook-id'

# Optional: Email configuration for notifications
# Uncomment and configure if you want email features
# os.environ['SMTP_SERVER'] = 'smtp.gmail.com'
# os.environ['SMTP_PORT'] = '587'
# os.environ['SENDER_EMAIL'] = 'your-email@gmail.com'
# os.environ['EMAIL_PASSWORD'] = 'your-app-password'

# Import Flask app
from flask_app import app as application
```

5. **Replace** `yourusername` with your actual PythonAnywhere username
6. **Generate and set** a secure SECRET_KEY:
   - Open a Python console
   - Run: `import secrets; print(secrets.token_hex(32))`
   - Copy the output and paste it as your SECRET_KEY
7. Click **"Save"** at the top

**5. Configure Static Files**
1. On the Web tab, scroll to the **"Static files"** section
2. Click **"Enter path"** and add:
   - **URL:** `/static/`
   - **Directory:** `/home/yourusername/Support-zetsu-preview-/static/`
3. Replace `yourusername` with your actual username

**6. Create Uploads Directory**
1. Go back to the **"Files"** tab
2. Navigate to your project directory
3. Create a new directory called `uploads`
4. This will store user file attachments

**7. Launch Your Application**
1. Go back to the **"Web"** tab
2. Click the green **"Reload"** button
3. Wait 10-20 seconds for the reload to complete
4. Click on your domain link at the top (e.g., `yourusername.pythonanywhere.com`)
5. Your support portal should now be live! 🎉

**8. Access Admin Panel**
1. Visit `yourusername.pythonanywhere.com/register`
2. Register with the whitelisted email: `zetsuserv@gmail.com`
3. Create a strong password
4. Go to `yourusername.pythonanywhere.com/login`
5. Login with your credentials
6. Access the dashboard to manage tickets

#### Common PythonAnywhere Issues & Solutions

**Issue: Application shows "Something went wrong" or blank page**
- **Cause:** Usually WSGI configuration error or missing dependencies
- **Solution:**
  1. Check the **Error log** on the Web tab (look for Python tracebacks)
  2. Verify WSGI file paths match your actual username
  3. Ensure all dependencies are installed: `pip3 install --user -r requirements.txt`
  4. Check that `flask_app.py` has no syntax errors: `python3 -m py_compile flask_app.py`
  5. Verify SECRET_KEY is set in WSGI file (not "REPLACE-WITH-YOUR-SECRET-KEY-HERE")

**Issue: Static files (CSS) not loading - page has no styling**
- **Cause:** Static files mapping is incorrect or missing
- **Solution:**
  1. Go to Web tab → Static files section
  2. Verify mapping is exactly: `/static/` → `/home/yourusername/Support-zetsu-preview-/static/`
  3. Replace `yourusername` with your actual PythonAnywhere username
  4. Click "Reload" button after fixing
  5. Hard refresh your browser (Ctrl+Shift+R or Cmd+Shift+R)

**Issue: Database errors or "no such table" errors**
- **Cause:** Database not initialized or permissions issue
- **Solution:**
  1. Delete old database: `rm ~/Support-zetsu-preview-/support_tickets.db`
  2. Reload web app (database will auto-create)
  3. Ensure uploads directory exists: `mkdir -p ~/Support-zetsu-preview-/uploads`
  4. Check file permissions: `chmod 755 ~/Support-zetsu-preview-`

**Issue: 504 Gateway Timeout**
- **Cause:** Python syntax error or infinite loop in code
- **Solution:**
  1. Check error logs for Python tracebacks
  2. Validate syntax: `python3 -m py_compile flask_app.py`
  3. Check WSGI file for typos or incorrect indentation
  4. Ensure no infinite loops or blocking operations in code

**Issue: ModuleNotFoundError for 'requests' or other packages (New in v3.2.0)**
- **Cause:** New dependency not installed
- **Solution:**
  1. Open Bash console
  2. Navigate to project: `cd ~/Support-zetsu-preview-`
  3. Install: `pip3 install --user requests==2.31.0`
  4. Or reinstall all: `pip3 install --user -r requirements.txt`
  5. Reload web app

**Issue: Flash messages not showing as toasts (New in v3.2.0)**
- **Cause:** JavaScript not loading or browser caching old CSS
- **Solution:**
  1. Hard refresh browser (Ctrl+Shift+R)
  2. Check browser console for JavaScript errors (F12)
  3. Verify static files are loading correctly
  4. Clear browser cache completely

**Issue: Webhook not sending data (New in v3.2.0)**
- **Cause:** N8N_WEBHOOK_URL not configured or invalid URL
- **Solution:**
  1. This is optional - app works without webhook
  2. If needed, add to WSGI file: `os.environ['N8N_WEBHOOK_URL'] = 'https://your-url'`
  3. Check error log for webhook-related messages
  4. Verify webhook URL is accessible and accepts POST requests
  5. PythonAnywhere free tier has limited outbound internet access

#### PythonAnywhere Tips

- **Free tier limitations:** 
  - 512MB storage space
  - One web app at a time
  - Restricted outbound internet (some external services may not work)
  - CPU seconds limit per day
  - Note: Webhook integration requires outbound access (may need paid tier)

- **Error logs:** Always check error logs when debugging (Web tab → Log files)
- **Console access:** Use Bash consoles to run commands, test code, and debug
- **Database backups:** Download your `.db` file regularly from the Files tab
- **Custom domain:** Upgrade to paid plan for custom domain support
- **Performance:** Free tier is suitable for testing; upgrade for production use
- **Dependencies:** Always use `pip3 install --user` for user-level packages
- **Reload required:** Click "Reload" button after ANY code or config changes

#### Pre-Deployment Checklist for PythonAnywhere

Before deploying, ensure:

- [ ] All files are uploaded or cloned from GitHub
- [ ] `requirements.txt` is present in project root
- [ ] Dependencies installed with `pip3 install --user -r requirements.txt`
- [ ] WSGI file configured with correct paths and username
- [ ] SECRET_KEY is set to a secure random value (not default)
- [ ] Static files mapping configured correctly
- [ ] `uploads` directory created in project folder
- [ ] Web app reloaded after configuration
- [ ] Error logs checked for any issues
- [ ] Test the homepage loads without errors
- [ ] Test form submission works
- [ ] Test admin login works
- [ ] Test dashboard accessible

---

### Option 2: Heroku Deployment

Heroku is a popular Platform-as-a-Service (PaaS) with Git-based deployment.

#### Prerequisites
- Heroku account (sign up at [heroku.com](https://www.heroku.com))
- Heroku CLI installed
- Git installed

#### Deployment Steps

**1. Prepare Your Application**

Create a `Procfile` in your project root:
```
web: gunicorn flask_app:app
```

Create or update `requirements.txt` (already included):
```bash
pip freeze > requirements.txt
```

**2. Create Heroku App**
```bash
heroku login
heroku create your-app-name
```

**3. Set Environment Variables**
```bash
heroku config:set SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
heroku config:set SMTP_SERVER=smtp.gmail.com
heroku config:set SMTP_PORT=587
heroku config:set SENDER_EMAIL=your-email@gmail.com
heroku config:set EMAIL_PASSWORD=your-app-password
```

**4. Deploy**
```bash
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

**5. Access Your App**
```bash
heroku open
```

---

### Option 3: DigitalOcean / AWS / Google Cloud

For production deployments with full control, use a VPS or cloud platform.

#### General Steps (Ubuntu Server)

**1. Server Setup**
```bash
sudo apt update
sudo apt upgrade -y
sudo apt install python3 python3-pip nginx supervisor -y
```

**2. Clone and Setup**
```bash
cd /var/www
sudo git clone https://github.com/ismailmuhammad15g-code/Support-zetsu-preview-.git
cd Support-zetsu-preview-
sudo pip3 install -r requirements.txt
```

**3. Configure Environment**
Create `/var/www/Support-zetsu-preview-/.env`:
```bash
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///support_tickets.db
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
```

**4. Setup Gunicorn with Supervisor**
Create `/etc/supervisor/conf.d/support-portal.conf`:
```ini
[program:support-portal]
directory=/var/www/Support-zetsu-preview-
command=/usr/local/bin/gunicorn -w 4 -b 127.0.0.1:8000 flask_app:app
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/support-portal.err.log
stdout_logfile=/var/log/support-portal.out.log
```

**5. Configure Nginx**
Create `/etc/nginx/sites-available/support-portal`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /var/www/Support-zetsu-preview-/static/;
    }
}
```

**6. Enable and Start**
```bash
sudo ln -s /etc/nginx/sites-available/support-portal /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start support-portal
```

---

### Option 4: Docker Deployment (Advanced)

Create a `Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=flask_app.py
ENV SECRET_KEY=change-this-in-production

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "flask_app:app"]
```

Build and run:
```bash
docker build -t support-portal .
docker run -p 5000:5000 -e SECRET_KEY=your-secret-key support-portal
```

---

### Post-Deployment Checklist

After deploying to any platform, verify:

- [ ] Home page loads correctly
- [ ] All navigation links work
- [ ] Can submit a support ticket
- [ ] Can track tickets by ID and email
- [ ] Login page accessible at `/login`
- [ ] Can register admin account (if first time)
- [ ] Can login and access dashboard
- [ ] Dashboard shows statistics correctly
- [ ] Can reply to tickets
- [ ] Can filter tickets
- [ ] Can export tickets to CSV
- [ ] Can bulk resolve tickets
- [ ] Email notifications working (if configured)
- [ ] Static files (CSS) loading properly
- [ ] File uploads working
- [ ] Mobile responsive design works
- [ ] No error messages in logs

---

### Security Checklist for Production

Before going live, ensure:

- [ ] `SECRET_KEY` is set to a secure random value
- [ ] `debug=False` in production (automatic with WSGI)
- [ ] HTTPS/SSL enabled (automatic on PythonAnywhere)
- [ ] Change default admin email in whitelist if needed
- [ ] Strong admin password created
- [ ] Email credentials secured (use app-specific passwords)
- [ ] Database file has proper permissions
- [ ] Regular backups configured
- [ ] Error logging enabled
- [ ] Update all dependencies regularly

---

### Accessing Admin Panel

**Login URL:** `your-domain.com/login`

**Note:** The login link is hidden from navigation for security. Users must know the direct URL to access the admin panel.

**First-Time Setup:**
1. Visit `/register` to create admin account
2. Use whitelisted email: `zetsuserv@gmail.com` (or modify whitelist in code)
3. Create strong password (minimum 8 characters)
4. Login at `/login`
5. Access dashboard to manage tickets

### Environment Variables

**Required:**
- `SECRET_KEY` - Flask secret key for sessions (generate with `secrets.token_hex(32)`)

**AI Integration (New in v3.4.0):**
- `GEMINI_API_KEY` - Google Gemini API key for AI-powered responses
  - Default: `AIzaSyBYpMnBd1UMuPDvskn9-ss3LpWkUBdWmR0` (included for demo)
  - Get your own key at: https://makersuite.google.com/app/apikey
  - Set via environment variable for production use

**Optional (for webhook automation):**
- `N8N_WEBHOOK_URL` - n8n or other webhook URL for automated ticket processing (v3.2.0)

**Optional (for email notifications):**
- `SMTP_SERVER` - SMTP server address (default: smtp.gmail.com)
- `SMTP_PORT` - SMTP server port (default: 587)
- `SENDER_EMAIL` - Email address for sending notifications
- `EMAIL_PASSWORD` - Email password or app-specific password

**Database:**
- `DATABASE_URL` - Database connection string (default: sqlite:///support_tickets.db)

### 🤖 AI Setup (v3.4.0)

The Hybrid AI Support System uses Google's Gemini Pro model for intelligent responses.

**Quick Start:**
- The application includes a demo API key for testing
- For production use, get your own free API key from Google AI Studio

**Getting Your Own API Key:**
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your key and set it as an environment variable:
   ```bash
   export GEMINI_API_KEY=your-key-here
   ```

**How It Works:**
- When admin toggle is set to "Unavailable", AI auto-responds to new tickets
- AI always generates draft suggestions for admins, regardless of availability
- Sentiment analysis automatically escalates urgent tickets
- AI uses your FAQ database as context for accurate, relevant responses

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

### Public Routes (No Authentication Required)

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Landing page with hero section and features |
| `/support` | GET | Support ticket submission form |
| `/submit` | POST | Handle ticket form submission |
| `/track` | GET | Ticket tracking page |
| `/search_ticket` | POST | Search tickets by ticket ID or email address |
| `/faq` | GET | FAQ page with categorized questions |
| `/about` | GET | About page with company information |

### Authentication Routes (Public Access)

| Route | Method | Description |
|-------|--------|-------------|
| `/login` | GET, POST | Admin login page (hidden from navigation) |
| `/register` | GET, POST | Admin registration (whitelist only: zetsuserv@gmail.com) |
| `/logout` | GET | Logout and end admin session |

### Protected Routes (Admin Only - Requires Login)

| Route | Method | Description |
|-------|--------|-------------|
| `/dashboard` | GET | Admin dashboard with all tickets and statistics |
| `/dashboard?status=Open` | GET | Dashboard filtered by status |
| `/dashboard?priority=Urgent` | GET | Dashboard filtered by priority |
| `/dashboard?issue_type=Bug` | GET | Dashboard filtered by issue type |
| `/reply_ticket/<id>` | POST | Reply to a ticket and mark as resolved |
| `/export_tickets` | GET | Export all tickets to CSV file |
| `/bulk_resolve` | POST | Mark multiple selected tickets as resolved |

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
- ✅ **CSRF Protection** - Flask-WTF CSRF tokens on all forms (New in v3.3.0)
- ✅ **Client-side Validation** - File size and type validation before upload (New in v3.3.0)
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
4. **CSRF Protection** - ✅ Already implemented with Flask-WTF (v3.3.0)
5. **Rate Limiting** - Add Flask-Limiter for additional DDoS protection (optional)
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

## 🔧 Troubleshooting

### Email Notification Issues

**Problem:** Admin receives message "Reply saved and ticket marked as Resolved, but email notification failed."

**Solution:**

1. **Check Email Configuration Status:**
   - The dashboard now displays a warning banner if email is not configured
   - Look for the yellow warning banner at the top of the dashboard

2. **Configure Email Credentials:**
   Set the following environment variables:
   ```bash
   # For Gmail (recommended)
   export SENDER_EMAIL=your-email@gmail.com
   export EMAIL_PASSWORD=your-app-specific-password
   export SMTP_SERVER=smtp.gmail.com
   export SMTP_PORT=587
   ```

3. **Generate Gmail App-Specific Password:**
   - Go to Google Account Settings → Security → 2-Step Verification → App passwords
   - Generate a new app password for "Mail"
   - Use this password (not your regular Gmail password)

4. **For Other Email Providers:**
   - **Outlook/Office365:**
     - SMTP_SERVER: smtp.office365.com
     - SMTP_PORT: 587
   - **Yahoo:**
     - SMTP_SERVER: smtp.mail.yahoo.com
     - SMTP_PORT: 587

5. **Test Email Configuration:**
   - Submit a test ticket as a user
   - Reply to the ticket as admin
   - Check if email notification was sent successfully

**Note:** Email is optional. The system works perfectly without email configuration - tickets are still saved and managed normally, but users won't receive email notifications.

### Image Attachments Not Displaying

**Problem:** Admin can see filename but not the actual image.

**Solution:** This has been fixed in the latest version. Images now display inline in the admin dashboard with:
- Full image preview for image files (.png, .jpg, .jpeg, .gif)
- Download link for all attachments
- Secure admin-only access to uploaded files

**To verify the fix:**
1. Submit a ticket with an image attachment
2. Login to admin dashboard
3. Click "View" on the ticket
4. The image should display inline with a download link below it

### Common Deployment Issues

**Issue:** Database errors on PythonAnywhere

**Solution:**
```bash
# Delete old database and let it recreate
rm ~/Support-zetsu-preview-/support_tickets.db
# Reload web app - database will auto-create with fresh schema
```

**Issue:** Uploaded files not accessible

**Solution:**
```bash
# Ensure uploads directory exists with proper permissions
mkdir -p ~/Support-zetsu-preview-/uploads
chmod 755 ~/Support-zetsu-preview-/uploads
```

**Issue:** Import errors for new dependencies

**Solution:**
```bash
# Reinstall all dependencies
pip3 install --user -r requirements.txt
# Reload web app
```

### AI Integration Issues (New in v3.4.0)

**Issue:** AI not responding when admin is unavailable

**Solution:**
1. **Check API Key Configuration:**
   - Verify `GEMINI_API_KEY` is set (default demo key is included)
   - For production, get your own key from Google AI Studio
   - Set via environment variable: `export GEMINI_API_KEY=your-key`

2. **Check Admin Availability Status:**
   - Login to admin dashboard
   - Look for the availability toggle in the header
   - Ensure it's set to "Unavailable" to trigger AI responses
   - Try toggling it and check the toast notification

3. **Check Logs:**
   - Look for AI-related log messages in console
   - Errors will be logged with details
   - Common issues: API rate limits, network errors

**Issue:** Availability toggle not working / redirect loops

**Solution:**
- This should NOT happen as we use AJAX/JSON responses
- Check browser console for JavaScript errors (F12)
- Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)
- Verify CSRF token is present in forms
- Check network tab for failed requests

**Issue:** AI suggestions not appearing

**Solution:**
1. Verify ticket was created after v3.4.0 implementation
2. Check ticket has `ai_suggestion` column in database
3. If migrating from old database:
   ```bash
   # Delete old database (backup first!)
   cp support_tickets.db support_tickets.db.backup
   rm support_tickets.db
   # Restart app - new schema will be created
   ```

**Issue:** Sentiment analysis not escalating priority

**Solution:**
- Sentiment analysis runs during ticket submission
- Keywords checked: urgent, angry, critical, emergency, ASAP, immediately, etc.
- Verify message contains these keywords
- Priority auto-escalates to "High" only during initial submission
- Existing tickets are not retroactively updated

**Issue:** Gemini API errors or empty responses

**Solution:**
1. **Rate Limiting:**
   - Free tier has limits (60 requests/minute)
   - Wait a moment and try again
   - For production, upgrade to paid tier

2. **Network Issues:**
   - Check internet connectivity
   - Verify firewall allows HTTPS to googleapis.com
   - PythonAnywhere free tier may have restrictions

3. **Invalid API Key:**
   - Verify key is correct and active
   - Check for extra spaces or quotes
   - Get new key if needed from Google AI Studio

4. **Model Unavailable:**
   - Application uses gemini-1.5-flash model (updated from deprecated gemini-pro)
   - If unavailable, check Google AI Studio status
   - Try again later if service is down

**Best Practices:**
- Test AI features in development first
- Monitor API usage to stay within limits
- Set up error logging for production
- Consider caching AI responses
- Have human fallback for critical issues

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
- **requests** (2.31.0) - HTTP library for webhook integration (New in v3.2.0)
- **python-dateutil** (2.8.2) - Date utilities
- **python-dotenv** (1.0.0) - Environment variables
- **Pillow** (10.1.0) - Image processing
- **gunicorn** (21.2.0) - WSGI server
- **google-generativeai** (0.3.2) - Google Gemini AI SDK (New in v3.4.0)

### Development (Optional)
- **pytest** (7.4.3) - Testing framework
- **pytest-flask** (1.3.0) - Flask testing utilities

## 🚀 Quick Start Guide: AI Features (v3.4.0)

### For Admins

**Setting Your Availability:**
1. Login to admin dashboard
2. Look for the toggle switch in the top-right header
3. Toggle to "Unavailable" when you're offline/busy
4. AI will automatically handle new tickets
5. Toggle back to "Available" when you return

**Using AI Suggestions:**
1. Open any ticket in the dashboard
2. Look for the "🤖 AI Suggested Response" section
3. Review the AI-generated draft
4. Click "✨ Use AI Suggestion" to load it
5. Edit as needed and send

**Understanding AI Indicators:**
- **Blue box with robot icon** = AI suggestion available
- **Green box with checkmark** = AI already auto-responded
- **"[AI Assistant Response]" prefix** = Response was AI-generated

### For Users

**Getting Instant Help:**
- Submit a ticket when admin is unavailable
- AI responds automatically with helpful information
- Response is based on FAQ knowledge base
- Receive email with AI response (if configured)

**Urgent Issues:**
- Use keywords: urgent, critical, emergency, ASAP
- Ticket is automatically escalated to High Priority
- Admin is notified regardless of availability status

### How It Works

**Hybrid Logic:**
```
New Ticket Submitted
    ↓
Check Admin Availability
    ↓
├─ Admin Available → Notification Only
│                    (AI suggestion generated for admin)
│
└─ Admin Unavailable → AI Auto-Response
                        (Ticket marked resolved with AI reply)
```

**Sentiment Analysis:**
```
Ticket Message
    ↓
Scan for Keywords
    ↓
├─ Urgent Keywords Found → Escalate to High Priority
│                           Notify admin immediately
│
└─ Normal Message → Regular Priority
                     Follow availability logic
```

### Configuration

**Minimal Setup (Demo):**
```bash
# Just run the app - demo API key is included
python3 flask_app.py
```

**Production Setup:**
```bash
# Get your own API key from Google AI Studio
export GEMINI_API_KEY=your-api-key-here

# Optional: Configure email for notifications
export SENDER_EMAIL=your-email@gmail.com
export EMAIL_PASSWORD=your-app-password

# Run the app
python3 flask_app.py
```

### Testing AI Features

**Test Availability Toggle:**
1. Login as admin
2. Toggle availability switch
3. Check toast notification appears
4. Verify no redirect/refresh occurs
5. Status should persist across page loads

**Test AI Auto-Response:**
1. Set admin to "Unavailable"
2. Submit a test ticket (from incognito/different browser)
3. Check ticket in dashboard
4. Should show green "AI Already Responded" indicator
5. Check email for AI response (if configured)

**Test AI Suggestions:**
1. Set admin to "Available"
2. Submit a test ticket
3. Login to dashboard
4. Open ticket details
5. Should see blue "AI Suggested Response" box
6. Click "Use AI Suggestion" to test

**Test Sentiment Analysis:**
1. Submit ticket with "URGENT! Critical issue!"
2. Check dashboard
3. Ticket should show "High" priority badge
4. Works regardless of admin availability

## 🤝 Contributing

Contributions are welcome! This is a production-ready application with room for enhancements:

### Implemented Features ✅
- ✅ Admin dashboard for ticket management
- ✅ User authentication system
- ✅ Advanced search and filtering (status, priority, issue type)
- ✅ CSV export for reporting
- ✅ Bulk operations (resolve multiple tickets)
- ✅ Hidden admin login for security
- ✅ Real-time statistics dashboard

### Potential Enhancements 💡
- 📋 Ticket assignment to team members
- 💬 Internal notes and comments
- 🎨 Email templates customization
- 🌐 Multi-language support (i18n)
- 📊 Advanced analytics and charts
- 🔔 Real-time notifications (WebSockets)
- 🔌 REST API endpoints for integrations
- 🗂️ Ticket categories and tags
- ⏱️ SLA (Service Level Agreement) tracking
- 📱 Mobile app integration
- 🤖 AI-powered response suggestions
- 📎 Multiple file attachments per ticket
- 🔍 Full-text search
- 📅 Calendar view for tickets
- 👥 Customer portal for ticket history

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

### Version 3.4.0 (Latest - December 2024) 🤖🎉

#### 🧠 AI-Powered Features
- ✨ **NEW:** **Gemini AI Integration** - Powered by Google's Gemini Pro model
  - Intelligent, context-aware responses to support tickets
  - Trained on FAQ knowledge base for accurate answers
  - Professional, empathetic tone matching your brand
  - Configurable via `GEMINI_API_KEY` environment variable
  
- ✨ **NEW:** **Hybrid Human-AI Support System** - Smart ticket handling
  - AI auto-responds when admin is unavailable
  - Admin notifications when available
  - Seamless handoff between AI and human support
  - Configurable availability status per admin
  
- ✨ **NEW:** **AI Draft Suggestions** - Intelligent assistance for admins
  - AI generates draft responses for every ticket
  - Always available regardless of admin status
  - One-click copy to reply field
  - Review and edit before sending
  
- ✨ **NEW:** **Sentiment Analysis** - Smart priority escalation
  - Detects urgent/angry keywords in messages
  - Auto-escalates to "High Priority"
  - Keywords: urgent, angry, critical, emergency, ASAP, etc.
  - Ensures urgent issues get immediate attention

#### 🎛️ Admin Dashboard Enhancements
- ✨ **NEW:** **Availability Toggle Switch** - Control AI behavior
  - Modern Fluent Design toggle in dashboard header
  - AJAX-based (no redirects, no loops)
  - Visual status: "Available" / "Unavailable"
  - Smooth animations and transitions
  - Real-time status updates
  
- ✨ **NEW:** **AI Response Indicators** - Track AI activity
  - Visual badges for AI-responded tickets
  - See which tickets got AI assistance
  - Distinguish human vs AI replies
  - Audit trail for support quality

#### 🗄️ Database Updates
- 📊 **NEW:** `is_available` column in User model
  - Tracks admin availability status
  - Default: True (available)
  - Persists across sessions
  
- 📊 **NEW:** `ai_responded` column in Ticket model
  - Tracks if AI auto-responded
  - Default: False
  - Used for reporting and analytics
  
- 📊 **NEW:** `ai_suggestion` column in Ticket model
  - Stores AI-generated draft responses
  - Always populated for admin reference
  - Cached for performance

#### 🔒 Security & Safety
- 🔐 **SECURITY:** No redirect loops in availability toggle
  - JSON-only responses from toggle endpoint
  - AJAX/Fetch API implementation
  - CSRF protection on all AJAX requests
  - Proper error handling and rollback
  
- 🔐 **SECURITY:** API key protection
  - Environment variable configuration
  - No hardcoded secrets in code
  - Fallback to demo key for testing
  - Production guidance in documentation

#### 📦 Dependencies
- ➕ Added `google-generativeai==0.3.2` - Google Gemini AI SDK
- ➕ Updated requirements.txt with AI dependencies

#### 🎨 UI/UX Improvements
- 🎨 Modern toggle switch with Fluent Design
- 🎨 AI suggestion cards with blue accent
- 🎨 Status indicators for AI responses
- 🎨 Responsive layout for mobile toggle
- 🎨 Smooth hover effects and transitions
- 🎨 Professional loading states

#### 📝 Documentation
- 📝 Comprehensive README update with AI features
- 📝 API key setup instructions
- 📝 Hybrid logic explanation
- 📝 Sentiment analysis keyword list
- 📝 Troubleshooting section for AI
- 📝 Best practices for availability toggle

#### 🛠️ Technical Improvements
- ⚡ FAQ context integration for AI
  - AI reads FAQ database dynamically
  - Provides contextually accurate answers
  - Auto-updates when FAQs change
  
- ⚡ Efficient AI suggestion caching
  - Generated once, stored in database
  - No repeated API calls
  - Fast dashboard loading
  
- ⚡ Comprehensive logging
  - All AI interactions logged
  - Availability changes tracked
  - Error handling and recovery
  - Debug-friendly output

---

### Version 3.3.0 (December 2024) 🎉

#### 🚀 New Features
- ✨ **NEW:** **File Upload Progress Indicator** - Microsoft-style upload experience
  - Real-time progress bar during file upload
  - Animated loading spinner
  - File name display with upload status
  - Success confirmation with checkmark icon
  - Smooth animations and transitions
  
- ✨ **NEW:** **Submit Button Loading State** - Better form submission feedback
  - Loading spinner appears when form is submitted
  - Button disabled during submission to prevent double-submit
  - Clear visual feedback that form is processing
  
- ✨ **NEW:** **Admin File Management** - Clean up and manage attachments
  - **Clear Unused Files** button to remove orphaned attachments
  - Identifies files not referenced by any tickets
  - One-click cleanup with confirmation dialog
  - Helps maintain disk space and organization
  
- ✨ **NEW:** **Delete Individual Tickets** - Complete ticket removal
  - Delete button for each ticket in dashboard
  - Removes ticket and associated attachment file
  - Confirmation dialog prevents accidental deletion
  - Admin-only access for security

#### 🔒 Security Enhancements
- 🔐 **SECURITY:** **CSRF Protection** - Complete Cross-Site Request Forgery protection
  - Flask-WTF CSRF tokens on all forms
  - Support form, login, register, track ticket forms
  - Dashboard reply, bulk resolve, and delete operations
  - Dynamic CSRF token injection for JavaScript-created forms
  
- 🔐 **SECURITY:** **Client-Side Validation** - Enhanced file upload security
  - File size validation (5MB limit) before upload
  - File type validation against allowed extensions
  - Immediate user feedback on invalid files
  - Prevents unnecessary server requests

#### 🎨 UI/UX Improvements
- 🎨 Upload progress bar with gradient animation
- 🎨 Success state for completed uploads
- 🎨 Danger button styling for delete operations
- 🎨 Consistent loading spinners across the application
- 🎨 Better visual hierarchy in admin dashboard

#### 📝 Documentation
- 📝 Updated README with v3.3.0 features
- 📝 Added file management documentation
- 📝 Enhanced security section with new protections
- 📝 Updated feature list with new capabilities

---

### Version 3.2.0 (December 2024) 🎉

#### 🚀 New Features
- ✨ **NEW:** **n8n Webhook Integration** - Automated ticket data submission to external automation platforms
  - POST ticket data (Name, Email, Issue, Priority) to configurable webhook URL
  - Configured via `N8N_WEBHOOK_URL` environment variable
  - Non-blocking with 5-second timeout
  - Comprehensive error handling (won't crash app if webhook fails)
  
- ✨ **NEW:** **Dynamic Time-Based Greeting** - Personalized user experience
  - 🌅 "Good Morning" (5 AM - 11:59 AM)
  - ☀️ "Good Afternoon" (12 PM - 5:59 PM)
  - 🌆 "Good Evening" (6 PM - 9:59 PM)
  - 🌙 "Good Night" (10 PM - 4:59 AM)
  - Auto-updates based on user's local time
  
- ✨ **NEW:** **Glassmorphism Toast Notifications** - Modern notification system
  - Replaced traditional Flask flash messages
  - Beautiful slide-in/slide-out animations
  - Backdrop blur effect for premium look
  - Auto-dismiss after 5 seconds with manual close option
  - Success, error, warning, and info variants
  
- ✨ **NEW:** **Interactive Button Animations** - Enhanced UX
  - Shimmer effect on hover for Submit and Dashboard buttons
  - Smooth glow animations using CSS keyframes
  - Enhanced visual feedback throughout the app
  
- ✨ **NEW:** **Dashboard Skeleton Loader** - Better perceived performance
  - CSS-animated loading placeholders
  - Shows while data is loading
  - Professional loading state
  
- ✨ **NEW:** **Mobile Floating Action Button (FAB)** - Mobile-first design
  - Persistent support button on mobile devices (≤768px)
  - Smooth scale animations
  - Quick access to support form

#### 🔒 Security Enhancements
- 🔐 **SECURITY:** XSS protection in toast notifications (using `textContent` instead of `innerHTML`)
- 🔐 **SECURITY:** SSRF protection for webhook URLs
  - Validates URL format (HTTP/HTTPS only)
  - Blocks localhost and private IP ranges (10.x, 192.168.x, 172.16.x)
  - Prevents internal network access
- 🔐 **SECURITY:** CodeQL scan passed with **0 vulnerabilities**

#### 🎨 UI/UX Improvements
- 🎨 Enhanced glassmorphism effects with backdrop-filter blur on cards
- 🎨 Fluent Design emoji icons for time-based greetings
- 🎨 Smooth animations and transitions throughout
- 🎨 Professional loading states

#### 📦 Dependencies
- ➕ Added `requests==2.31.0` for webhook integration

#### 📝 Documentation
- 📝 **DOCS:** Updated README with Version 3.2.0 changelog
- 📝 **DOCS:** Added webhook configuration instructions
- 📝 **DOCS:** Enhanced PythonAnywhere deployment guide with error prevention

### Version 3.1.0
- ✨ **NEW:** Advanced ticket filtering (status, priority, issue type)
- ✨ **NEW:** CSV export functionality for all tickets
- ✨ **NEW:** Bulk resolve operations for multiple tickets
- ✨ **NEW:** Enhanced statistics (Urgent and High Priority counts)
- ✨ **NEW:** Checkbox selection system for tickets
- ✨ **NEW:** Filter form with Apply/Clear functionality
- 🔧 **FIXED:** SQLAlchemy 2.0 compatibility issues (login/dashboard crashes)
- 🔧 **FIXED:** Updated deprecated query methods (User.query.get → db.session.get)
- 🔐 **SECURITY:** Hidden login links from navigation (accessible via URL only)
- 🔐 **SECURITY:** Input validation for bulk operations
- 📝 **DOCS:** Comprehensive README update with deployment guides
- 📝 **DOCS:** Added hosting instructions for multiple platforms

### Version 3.0.0
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
