# 🚀 ZetsuServ Support Portal - Deployment & Troubleshooting Guide

## Quick Deployment Checklist

Before deploying, ensure you have:

- [ ] Python 3.7+ installed
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] SECRET_KEY environment variable set
- [ ] Database file created and writable
- [ ] Uploads directory created and writable
- [ ] (Optional) Email credentials configured
- [ ] (Optional) Webhook URL configured

## Step-by-Step Deployment for PythonAnywhere

### 1. Upload Your Project

```bash
# Clone from GitHub
git clone https://github.com/ismailmuhammad15g-code/Support-zetsu-preview-.git
cd Support-zetsu-preview-
```

### 2. Install Dependencies

```bash
pip3 install --user -r requirements.txt
```

### 3. Configure WSGI File

Edit your WSGI configuration file (`/var/www/yourusername_pythonanywhere_com_wsgi.py`):

```python
import sys
import os

# Add your project directory to the sys.path
project_home = '/home/yourusername/Support-zetsu-preview-'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables
os.environ['SECRET_KEY'] = 'your-secret-key-here'  # IMPORTANT: Generate a new one!
os.environ['DATABASE_URL'] = f'sqlite:///{project_home}/support_tickets.db'

# Optional: Email configuration
# os.environ['SMTP_SERVER'] = 'smtp.gmail.com'
# os.environ['SMTP_PORT'] = '587'
# os.environ['SENDER_EMAIL'] = 'your-email@gmail.com'
# os.environ['EMAIL_PASSWORD'] = 'your-app-password'

# Optional: Webhook configuration
# os.environ['N8N_WEBHOOK_URL'] = 'https://your-webhook-url.com'

# Import Flask application
from flask_app import app as application
```

### 4. Set Static Files Mapping

In the PythonAnywhere Web tab:
- URL: `/static/`
- Directory: `/home/yourusername/Support-zetsu-preview-/static/`

### 5. Create Required Directories

```bash
mkdir -p uploads
chmod 755 uploads
```

### 6. Reload Web App

Click the "Reload" button on the Web tab.

### 7. Verify Deployment

Visit these endpoints to verify everything is working:

1. **Home Page**: `https://yourusername.pythonanywhere.com/`
2. **Health Check**: `https://yourusername.pythonanywhere.com/health`
3. **Database Verification**: `https://yourusername.pythonanywhere.com/db-verify`

## Troubleshooting Common Issues

### Issue 1: Internal Server Error (500) on Dashboard

**Symptoms:**
- Dashboard page shows "Internal Server Error"
- Other pages work fine
- Database might have schema issues

**Diagnosis:**
1. Check health endpoint: `/health`
2. Check database schema: `/db-verify`
3. Check error logs in PythonAnywhere Web tab

**Solution:**
```bash
# Run the migration utility
python db_migrate.py

# Choose option 1 to fix missing columns
# Or option 3 to re-run diagnostics
```

**Alternative Solution:**
If the migration utility shows `admin_reply` column is missing:
```python
from flask_app import app, db
from sqlalchemy import text

with app.app_context():
    db.session.execute(text('ALTER TABLE tickets ADD COLUMN admin_reply TEXT'))
    db.session.commit()
    print("✓ Column added successfully")
```

### Issue 2: Database Connection Errors

**Symptoms:**
- "database is locked" error
- "unable to open database file" error
- "no such table" error

**Diagnosis:**
Visit `/health` endpoint and check `database.connected` field.

**Solutions:**

**For "database is locked":**
```bash
# Stop all Python consoles
# Reload web app
# Check no other processes are using the database
```

**For "unable to open database file":**
```bash
# Check file permissions
chmod 644 support_tickets.db
chmod 755 /path/to/project/directory
```

**For "no such table":**
```bash
# Recreate database
python db_migrate.py
# Choose option 2 (WARNING: This deletes all data)
```

### Issue 3: Email Notifications Not Working

**Symptoms:**
- Tickets submitted but no emails received
- Admin replies save but user doesn't get notified
- Yellow warning banner on dashboard

**Diagnosis:**
Visit `/admin/settings` and check "Email" configuration status.

**Solution:**
```python
# In WSGI file, add:
os.environ['SMTP_SERVER'] = 'smtp.gmail.com'
os.environ['SMTP_PORT'] = '587'
os.environ['SENDER_EMAIL'] = 'your-email@gmail.com'
os.environ['EMAIL_PASSWORD'] = 'your-app-specific-password'
```

**For Gmail users:**
1. Enable 2-Factor Authentication
2. Generate App-Specific Password: https://myaccount.google.com/apppasswords
3. Use the app password in EMAIL_PASSWORD

**Test email configuration:**
1. Go to `/admin/settings`
2. Click "Send Test Email"
3. Check your inbox

### Issue 4: Static Files (CSS) Not Loading

**Symptoms:**
- Pages have no styling
- Plain white background
- Unstyled text

**Solution:**
1. Check static files mapping in PythonAnywhere Web tab
2. Verify path is correct: `/home/yourusername/Support-zetsu-preview-/static/`
3. Reload web app
4. Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)

### Issue 5: File Uploads Not Working

**Symptoms:**
- Upload fails silently
- "Permission denied" error
- Files not appearing in dashboard

**Solution:**
```bash
# Create uploads directory
mkdir -p uploads
chmod 755 uploads

# Verify it's writable
touch uploads/test.txt
rm uploads/test.txt
```

### Issue 6: Admin Can't Login

**Symptoms:**
- "Invalid email or password" error
- User exists but can't login
- Password doesn't work

**Solution:**
```python
# Register new admin user
# Visit: https://yourusername.pythonanywhere.com/register
# Use email: zetsuserv@gmail.com (automatically gets admin privileges)
# Or any other email for regular user account
```

**Reset password via console:**
```python
from flask_app import app, db, User

with app.app_context():
    user = User.query.filter_by(email='admin@example.com').first()
    if user:
        user.set_password('new-password')
        db.session.commit()
        print("✓ Password updated")
    else:
        print("✗ User not found")
```

## Using Diagnostic Tools

### Health Check Endpoint

**URL:** `/health`

**Returns:**
```json
{
  "status": "healthy",
  "database": {
    "connected": true,
    "tables_exist": true,
    "admin_reply_column_exists": true,
    "ticket_count": 10
  },
  "email": {
    "configured": false
  },
  "file_system": {
    "uploads_dir_exists": true,
    "uploads_dir_writable": true
  }
}
```

**Usage:**
```bash
# Check system health
curl https://yourusername.pythonanywhere.com/health

# Pretty print
curl https://yourusername.pythonanywhere.com/health | python -m json.tool
```

### Database Verification Endpoint

**URL:** `/db-verify`

**Returns:**
```json
{
  "database_url": "sqlite:///support_tickets.db",
  "tables": {
    "tickets": {
      "columns": [...],
      "row_count": 10
    }
  }
}
```

**Usage:**
```bash
# Verify database schema
curl https://yourusername.pythonanywhere.com/db-verify

# Check specific table
curl https://yourusername.pythonanywhere.com/db-verify | jq '.tables.tickets'
```

### Database Migration Utility

**Run from command line:**
```bash
python db_migrate.py
```

**Options:**
1. **Fix missing columns** - Safe, no data loss
2. **Recreate database** - WARNING: Deletes all data
3. **Re-run diagnostics** - Check current status
4. **Exit** - Quit the utility

**Example session:**
```
============================================================
CHECKING DATABASE CONNECTION
============================================================
✓ Database connection: OK

============================================================
VERIFYING DATABASE SCHEMA
============================================================
✓ Table 'tickets' exists
  ✓ All columns present and correct
  Records: 10

============================================================
MIGRATION OPTIONS
============================================================
1. Fix missing columns (safe - no data loss)
2. Recreate database (WARNING: deletes all data)
3. Re-run diagnostics
4. Exit
============================================================
Enter your choice (1-4): 1

============================================================
FIXING MISSING COLUMNS
============================================================
✓ Column 'admin_reply' already exists
```

## Best Practices

### Security

1. **Always set a unique SECRET_KEY**
   ```python
   import secrets
   print(secrets.token_hex(32))
   ```

2. **Use environment variables** (never commit secrets)
   ```python
   # In WSGI file
   os.environ['SECRET_KEY'] = os.getenv('SECRET_KEY')
   ```

3. **Use app-specific passwords** for email (not your main password)

4. **Enable HTTPS** (automatic on PythonAnywhere)

### Performance

1. **Use PostgreSQL** for production (instead of SQLite)
2. **Enable caching** for static files
3. **Monitor CPU usage** in PythonAnywhere dashboard
4. **Batch email notifications** (already implemented in v4.0.0)

### Maintenance

1. **Backup database regularly**
   ```bash
   # Download support_tickets.db from Files tab
   # Or use scheduled tasks
   ```

2. **Monitor error logs**
   ```bash
   # Check Web tab → Error log daily
   ```

3. **Update dependencies**
   ```bash
   pip3 install --user --upgrade -r requirements.txt
   ```

4. **Clean up old OTP records**
   ```python
   from flask_app import app, db, OTPVerification
   from datetime import datetime, timezone
   
   with app.app_context():
       expired = OTPVerification.query.filter(
           OTPVerification.expires_at < datetime.now(timezone.utc)
       ).all()
       for otp in expired:
           db.session.delete(otp)
       db.session.commit()
   ```

## Quick Reference

### Important URLs
- Health Check: `/health`
- Database Verification: `/db-verify`
- Admin Dashboard: `/dashboard`
- Analytics: `/admin/analytics`
- Settings: `/admin/settings`
- Broadcast: `/admin/broadcast`
- Login: `/login`
- Register: `/register`

### Important Files
- Application: `flask_app.py`
- Database: `support_tickets.db`
- Migration Utility: `db_migrate.py`
- Configuration: WSGI file
- Logs: PythonAnywhere Web tab → Log files

### Important Commands
```bash
# Install dependencies
pip3 install --user -r requirements.txt

# Run migration utility
python db_migrate.py

# Test database connection
python3 -c "from flask_app import app, db; app.app_context().push(); db.session.execute(db.text('SELECT 1')); print('✓ Connected')"

# Generate secret key
python3 -c "import secrets; print(secrets.token_hex(32))"
```

## Getting Help

If you're still experiencing issues:

1. **Check error logs** in PythonAnywhere Web tab
2. **Visit health endpoint** to see what's wrong
3. **Run migration utility** to fix database issues
4. **Check the README** for detailed documentation
5. **Submit an issue** on GitHub with:
   - Output from `/health` endpoint
   - Output from `/db-verify` endpoint
   - Error log traceback
   - Steps to reproduce

## Additional Resources

- [PythonAnywhere Help](https://help.pythonanywhere.com/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [GitHub Repository](https://github.com/ismailmuhammad15g-code/Support-zetsu-preview-)

---

**Built with ❤️ using Flask and Microsoft Fluent Design System**

Version: 4.1.0
Last Updated: December 2024
