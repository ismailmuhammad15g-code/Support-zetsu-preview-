# PythonAnywhere Deployment Checklist

## Pre-Deployment Checklist ✓

- [x] Flask-WTF dependency is in requirements.txt
- [x] google-generativeai dependency is in requirements.txt
- [x] Gemini model updated to 'gemini-1.5-flash'
- [x] AI error handling implemented
- [x] WSGI configuration file created
- [x] requirements.txt optimized (9 lines, no comments)
- [x] .gitignore includes __pycache__ and *.log

## Deployment Steps (Follow in Order)

### Step 1: Upload Files to PythonAnywhere
```bash
# Upload these files to /home/Supportzetsu/Support-zetsu-preview:
- flask_app.py
- requirements.txt
- var_www_Supportzetsu_wsgi.py
- templates/ (directory)
- static/ (directory)
- uploads/ (directory)
- DEPLOYMENT.md
- deploy.sh
```

### Step 2: Run Deployment Script
```bash
# In PythonAnywhere console:
cd /home/Supportzetsu/Support-zetsu-preview
chmod +x deploy.sh
./deploy.sh
```

**Expected Output:**
```
✓ Flask imported successfully
✓ Flask-WTF imported successfully
✓ Google GenerativeAI imported successfully
✓ Flask app imported successfully

✅ All imports successful!
✅ Deployment Complete!
```

### Step 3: Configure WSGI File
1. Go to PythonAnywhere **Web** tab
2. Click on **WSGI configuration file** link
3. **Delete all existing content**
4. Copy content from `var_www_Supportzetsu_wsgi.py`
5. **Important:** Add your environment variables:
   ```python
   # After the imports, add:
   os.environ['SECRET_KEY'] = 'paste-your-secret-key-here'
   os.environ['GEMINI_API_KEY'] = 'paste-your-api-key-here'
   ```
6. Save the file (Ctrl+S)

### Step 4: Configure Web App Settings
In PythonAnywhere **Web** tab:
- **Source code:** `/home/Supportzetsu/Support-zetsu-preview`
- **Working directory:** `/home/Supportzetsu/Support-zetsu-preview`
- **Virtualenv:** `/home/Supportzetsu/.virtualenvs/zetsu-env`

### Step 5: Reload Web App
Click the green **"Reload"** button at the top of the Web tab

### Step 6: Test Your Application
1. Visit your PythonAnywhere URL (e.g., supportzetsu.pythonanywhere.com)
2. You should see the home page
3. Try submitting a test ticket
4. Check that no errors appear

## Post-Deployment Verification

### Test 1: Check Error Logs
```bash
# In PythonAnywhere console:
cd /var/log/
cat Supportzetsu.pythonanywhere.com.error.log | tail -50
```
**Expected:** No ModuleNotFoundError for flask_wtf

### Test 2: Check Server Logs
```bash
cat Supportzetsu.pythonanywhere.com.server.log | tail -50
```
**Expected:** Flask app loaded successfully

### Test 3: Test AI Functionality
1. Submit a support ticket via the web interface
2. Login to admin dashboard
3. Check if AI draft is generated
**Expected:** No "404 model not found" errors

## Troubleshooting

### Issue: ModuleNotFoundError: No module named 'flask_wtf'
**Solution:**
```bash
workon zetsu-env
pip install Flask-WTF
```

### Issue: 404 models/gemini-pro is not found
**Solution:** Already fixed! The code uses 'gemini-1.5-flash' now.
Check your GEMINI_API_KEY is correct in WSGI file.

### Issue: ImportError after deployment
**Solution:**
```bash
workon zetsu-env
cd /home/Supportzetsu/Support-zetsu-preview
pip install -r requirements.txt --force-reinstall
```

### Issue: Web app shows 502 Bad Gateway
**Solution:**
1. Check WSGI file syntax
2. Check error logs
3. Ensure virtualenv path is correct
4. Click Reload button again

## Maintenance Tasks

### Weekly Cleanup (Recommended)
```bash
cd /home/Supportzetsu/Support-zetsu-preview

# Clean Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete

# Clean logs (keep last 7 days)
find . -name "*.log" -mtime +7 -delete

# Check disk usage
du -sh .
```

### Monthly Cleanup
```bash
# In admin dashboard:
1. Go to dashboard
2. Click "Clear Attachments" button to remove orphaned files
3. Export tickets if needed (before deleting old ones)
```

## Environment Variables Needed

**Required:**
- `SECRET_KEY` - Generate with: `python -c "import secrets; print(secrets.token_hex(32))"`
- `GEMINI_API_KEY` - Get from: https://makersuite.google.com/app/apikey

**Optional (for email notifications):**
- `SMTP_SERVER` - Default: smtp.gmail.com
- `SMTP_PORT` - Default: 587
- `SENDER_EMAIL` - Your Gmail address
- `EMAIL_PASSWORD` - Gmail App Password (not regular password!)

## Success Indicators

✅ Website loads without errors
✅ Can submit support tickets
✅ No "flask_wtf" import errors in logs
✅ No "gemini-pro" 404 errors in logs
✅ AI drafts are generated for new tickets
✅ Admin dashboard is accessible
✅ Email notifications work (if configured)

## Support Resources

- **Deployment Guide:** DEPLOYMENT.md
- **Fix Summary:** FIX_SUMMARY.md
- **PythonAnywhere Help:** https://help.pythonanywhere.com/
- **Flask Documentation:** https://flask.palletsprojects.com/

---

## Quick Reference Commands

```bash
# Activate virtual environment
workon zetsu-env

# Install dependencies
pip install -r requirements.txt

# Check what's installed
pip list | grep -i "flask\|gemini"

# Test imports
python3 -c "from flask_app import app; print('OK')"

# Clean cache
find . -type d -name "__pycache__" -exec rm -rf {} +

# Check disk usage
du -sh /home/Supportzetsu/Support-zetsu-preview
du -sh /home/Supportzetsu/.virtualenvs/zetsu-env
```

---

**ALL FIXES COMPLETE! Ready for deployment. ✅**
