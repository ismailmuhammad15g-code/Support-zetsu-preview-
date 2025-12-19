# PythonAnywhere Deployment - API Key Setup Guide

## ⚠️ IMPORTANT SECURITY NOTICE

**NO API KEYS ARE HARDCODED IN THIS APPLICATION**

All API keys must be set as environment variables for security. This prevents:
- Accidental exposure in version control
- Security vulnerabilities from exposed keys
- Issues when keys need to be rotated

## Setting Up Your Gemini API Key on PythonAnywhere

### Step 1: Get Your API Key
Your Gemini API key is: `AIzaSyDbblEl-Rw3p3fM31KHkb2PrDzcTFhI-ak`

**Important:** Keep this key secure and never commit it to Git!

### Step 2: Set Environment Variable in WSGI File

1. Log in to your PythonAnywhere account
2. Go to the **Web** tab
3. Scroll down to the **Code** section
4. Click on the **WSGI configuration file** link (e.g., `/var/www/Supportzetsu_wsgi.py`)

### Step 3: Edit the WSGI File

Add the following lines **after the imports** and **before importing the Flask app**:

```python
import sys
import os

# Add your project directory to the sys.path
project_home = '/home/Supportzetsu/Support-zetsu-preview'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# ====================================
# SET ENVIRONMENT VARIABLES HERE
# ====================================
# REQUIRED: Set your Gemini API key
os.environ['GEMINI_API_KEY'] = 'AIzaSyDbblEl-Rw3p3fM31KHkb2PrDzcTFhI-ak'

# OPTIONAL: Set other environment variables as needed
# os.environ['SECRET_KEY'] = 'your-secret-key-here'
# os.environ['SMTP_SERVER'] = 'smtp.gmail.com'
# os.environ['SMTP_PORT'] = '587'
# os.environ['SENDER_EMAIL'] = 'your-email@gmail.com'
# os.environ['EMAIL_PASSWORD'] = 'your-app-password'

# Activate virtual environment (if using one)
activate_this = '/home/Supportzetsu/.virtualenvs/zetsu-env/bin/activate_this.py'
if os.path.exists(activate_this):
    with open(activate_this) as f:
        exec(f.read(), {'__file__': activate_this})

# Import Flask app
from flask_app import app as application
```

### Step 4: Save and Reload

1. Click **Save** at the top of the WSGI editor
2. Go back to the **Web** tab
3. Click the **Reload** button (green button at the top)
4. Wait for the reload to complete

### Step 5: Verify the Setup

1. Visit your application URL
2. Try creating a support ticket with AI-powered suggestions
3. Check the error logs if something doesn't work:
   - In PythonAnywhere, go to **Web** tab
   - Click on **Error log** link
   - Look for messages about the Gemini API

## Expected Behavior

### ✅ When API Key is Configured Correctly:
- You will see in logs: `Gemini API configured successfully`
- AI-powered responses will work in support tickets
- The application will function normally

### ❌ When API Key is Missing or Invalid:
- You will see in logs: `GEMINI_API_KEY environment variable is not set`
- AI features will be unavailable
- Manual support ticket handling will still work
- You'll see fallback message: "AI suggestion unavailable at the moment"

## Troubleshooting

### Issue: "Gemini API key not configured"
**Solution:** Make sure you've added the line in the WSGI file and reloaded the web app.

### Issue: "Failed to configure Gemini API"
**Solution:** 
- Check that the API key is correct (no extra spaces)
- Verify the API key is enabled in Google Cloud Console
- Make sure you have quota available

### Issue: Changes don't take effect
**Solution:** Always reload the web app after changing the WSGI file.

## Security Best Practices

1. **Never commit API keys to Git**
2. **Always use environment variables** for sensitive data
3. **Rotate API keys regularly** (every 90 days recommended)
4. **Monitor API usage** in Google Cloud Console
5. **Set up billing alerts** to avoid unexpected charges

## Alternative: Using .env File (Not Recommended for PythonAnywhere)

While you could use a `.env` file, PythonAnywhere's WSGI configuration is the recommended approach because:
- It's more secure (file isn't in your web-accessible directory)
- It's the standard PythonAnywhere practice
- It's easier to manage and update
- No additional dependencies needed (like `python-dotenv`)

## Need Help?

- Check error logs in PythonAnywhere Web tab
- Verify API key at: https://makersuite.google.com/app/apikey
- Review deployment documentation: `DEPLOYMENT.md`
- Check deployment checklist: `DEPLOYMENT_CHECKLIST.md`

---

**Last Updated:** December 19, 2024
**Application Version:** 3.4.0+
**Gemini API Model:** gemini-1.5-flash
