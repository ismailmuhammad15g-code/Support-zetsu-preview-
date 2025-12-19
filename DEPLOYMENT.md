# PythonAnywhere Deployment Guide

## ⚠️ IMPORTANT: API Key Setup Required

**Before deploying, you MUST configure your Gemini API key!**

All hardcoded API keys have been removed for security. See **PYTHONANYWHERE_SETUP.md** for detailed instructions on setting up your API key via environment variables.

## Quick Setup Instructions

### 1. Upload Project Files
Upload all project files to: `/home/Supportzetsu/Support-zetsu-preview`

### 2. Virtual Environment Setup
```bash
# Create virtual environment (if not exists)
mkvirtualenv zetsu-env --python=/usr/bin/python3.10

# Activate virtual environment
workon zetsu-env

# Install dependencies
cd /home/Supportzetsu/Support-zetsu-preview
pip install -r requirements.txt

# To upgrade dependencies (especially after updating requirements.txt)
pip install --upgrade -r requirements.txt
```

### 3. WSGI Configuration
1. Go to PythonAnywhere Web tab
2. Set the source code directory to: `/home/Supportzetsu/Support-zetsu-preview`
3. Set the WSGI configuration file to: `/var/www/Supportzetsu_wsgi.py`
4. Copy the contents of `var_www_Supportzetsu_wsgi.py` to the WSGI file
5. Set virtual environment path: `/home/Supportzetsu/.virtualenvs/zetsu-env`

### 4. Environment Variables
Set these in the WSGI file or in PythonAnywhere environment:
```python
# Required
os.environ['SECRET_KEY'] = 'your-secret-key-here'
os.environ['GEMINI_API_KEY'] = 'your-gemini-api-key-here'

# Optional (for email notifications)
os.environ['SMTP_SERVER'] = 'smtp.gmail.com'
os.environ['SMTP_PORT'] = '587'
os.environ['SENDER_EMAIL'] = 'your-email@gmail.com'
os.environ['EMAIL_PASSWORD'] = 'your-app-password'
```

### 5. Database Initialization
```bash
cd /home/Supportzetsu/Support-zetsu-preview
python3 -c "from flask_app import db, app; app.app_context().push(); db.create_all()"
```

### 6. Storage Optimization (Important for FREE accounts)

#### Clean __pycache__ folders:
```bash
cd /home/Supportzetsu/Support-zetsu-preview
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete
```

#### Clean log files:
```bash
cd /home/Supportzetsu/Support-zetsu-preview
rm -f error.log
rm -f *.log
```

#### Clean /tmp directory:
```bash
# PythonAnywhere cleans /tmp automatically, but you can manually clean if needed
find /tmp -user Supportzetsu -type f -mtime +7 -delete 2>/dev/null
```

#### Monitor disk usage:
```bash
du -sh /home/Supportzetsu/Support-zetsu-preview
du -sh /home/Supportzetsu/.virtualenvs/zetsu-env
```

### 7. Verify Installation
```bash
# Test imports
python3 -c "from flask_app import app; print('App loaded successfully')"

# Test Gemini model
python3 -c "import google.generativeai as genai; genai.configure(api_key='test'); print('Gemini configured')"
```

## Troubleshooting

### ModuleNotFoundError: No module named 'flask_wtf'
```bash
workon zetsu-env
pip install Flask-WTF
```

### 404 models/gemini-1.5-flash is not found for API version v1beta
**SOLUTION:**
1. Update the library to the latest version:
   ```bash
   workon zetsu-env
   cd /home/Supportzetsu/Support-zetsu-preview
   pip install --upgrade -r requirements.txt
   ```
2. The code now uses `gemini-1.5-flash` with automatic fallback to `gemini-pro` if needed
3. If AI fails completely, a fallback message is displayed: "AI suggestion unavailable at the moment. Please review manually."
4. Ensure your GEMINI_API_KEY is valid and has API access enabled
5. Restart the web app after updating dependencies

### Storage Full
1. Clean __pycache__: `find . -type d -name "__pycache__" -exec rm -rf {} +`
2. Clean uploads: Use the "Clear Attachments" button in admin dashboard
3. Clean logs: `rm -f *.log`
4. Consider upgrading to paid PythonAnywhere account for more storage

## Maintenance Tasks

### Weekly Cleanup (recommended)
```bash
#!/bin/bash
# Add to cron or run manually

cd /home/Supportzetsu/Support-zetsu-preview

# Clean Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete

# Clean old logs (keep last 7 days)
find . -name "*.log" -mtime +7 -delete

# Clean old uploads via admin dashboard
# (use the web interface "Clear Attachments" button)

echo "Cleanup complete!"
```

## Security Notes

1. Always set a strong SECRET_KEY in production
2. Never commit API keys to version control
3. Use environment variables for sensitive data
4. Regular backups of the SQLite database
5. Monitor logs for suspicious activity

## Support

For issues specific to this deployment:
- Check PythonAnywhere error logs
- Check Flask application logs
- Review this guide's troubleshooting section
