# Quick Deployment Guide for PythonAnywhere

This is a quick reference guide to deploy the bug fixes to PythonAnywhere.

## Step 1: Upload Files
Upload these updated files to PythonAnywhere:
- `flask_app.py` (main fixes)
- `db_migrate.py` (migration script)

## Step 2: Backup Existing Database
```bash
cd /home/Supportzetsu/Support-zetsu-preview-/instance
cp support_tickets.db support_tickets.db.backup
```

## Step 3: Run Database Migration
```bash
cd /home/Supportzetsu/Support-zetsu-preview-
python db_migrate.py
```
Select option **1** to fix missing columns.

## Step 4: Verify Database Schema
```bash
python -c "from flask_app import app, db; from sqlalchemy import inspect; with app.app_context(): print([col['name'] for col in inspect(db.engine).get_columns('users')])"
```

Expected output should include the `name` column:
```
['id', 'email', 'password_hash', 'is_admin', 'is_verified', 'name', 'newsletter_subscribed', 'newsletter_popup_shown', 'created_at']
```

## Step 5: Set Environment Variables (Optional but Recommended)
In PythonAnywhere Web tab, add these environment variables:
```bash
SECRET_KEY=your-unique-secret-key-here
SENDER_EMAIL=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

## Step 6: Reload Web App
In PythonAnywhere Web tab, click the **Reload** button.

## Step 7: Test OTP Verification
1. Go to registration page: `https://supportzetsu.pythonanywhere.com/register`
2. Enter email and password
3. Check email for OTP (or check logs if email not configured)
4. Enter OTP on verification page
5. Should successfully create user without 500 error

## Troubleshooting

If you get errors:

### Check Health Status
Visit: `https://supportzetsu.pythonanywhere.com/health`

Should show:
- ✅ Database connected
- ✅ All tables exist
- ✅ All columns present

### Check Database Schema
Visit: `https://supportzetsu.pythonanywhere.com/db-verify`

Should show users table with all required columns including `name`.

### Check Logs
```bash
tail -f /var/log/supportzetsu.pythonanywhere.com.error.log
tail -f /var/log/supportzetsu.pythonanywhere.com.server.log
```

## What Was Fixed?

1. **Database Schema** - Added missing `name` column to users table
2. **Timezone Issue** - Fixed OTP expiration check to handle SQLite's naive datetimes
3. **Database Path** - Configured absolute path for PythonAnywhere
4. **SECRET_KEY** - Hardcoded secure fallback value
5. **Instance Directory** - Auto-created if missing

## Success Indicators

✅ OTP verification completes without 500 errors
✅ Users can successfully register and log in
✅ No "no such column: users.name" errors
✅ No timezone comparison errors

## Need Help?

Review the detailed documentation in `BUGFIX_SUMMARY.md`.
