# Quick Deployment Guide for PythonAnywhere

## Critical Fixes Deployed ✅

This update resolves three critical issues:
1. **Redirect Loops (ERR_TOO_MANY_REDIRECTS)** - Fixed with proper before_request hook
2. **Registration Failures (500 Errors)** - Fixed password_hash timing issue
3. **Session/Cookie Issues** - Verified correct configuration

---

## Deployment Steps

### 1. Pull Latest Code

SSH into your PythonAnywhere console or use the Bash console:

```bash
cd /home/yourusername/your-project-directory
git pull origin copilot/fix-redirect-loop-registration-error
```

### 2. Reload Web App

- Go to **Web** tab in PythonAnywhere
- Click the green **"Reload"** button
- Wait for reload to complete (about 5-10 seconds)

### 3. Verify Deployment

Test the health endpoint:

```bash
curl https://yourusername.pythonanywhere.com/health
```

You should see:
```json
{
  "status": "healthy",
  "database": {
    "connected": true,
    "ticket_count": X
  }
}
```

---

## Testing Your Fixes

### Test 1: Registration Flow

1. Open your app: `https://yourusername.pythonanywhere.com/register`
2. Enter a new email and password
3. Check your email for OTP (or see it on screen if email not configured)
4. Enter the OTP code
5. ✅ Should successfully create account without 500 error

### Test 2: Login Flow

1. Go to `/login`
2. Enter your credentials
3. ✅ Should log in and redirect to:
   - `/home` if regular user
   - `/dashboard` if admin (zetsuserv@gmail.com)

### Test 3: No Redirect Loops

1. After logging in, try visiting `/login` or `/register`
2. ✅ Should redirect you away without loops
3. Clear cookies and try accessing `/dashboard`
4. ✅ Should redirect to `/login` (not loop)

---

## Environment Variables (Optional)

### For HTTPS Deployments

If your PythonAnywhere app uses HTTPS, set this environment variable:

1. Go to **Web** tab
2. Scroll to **Environment variables**
3. Add:
   - Variable: `SESSION_COOKIE_SECURE`
   - Value: `true`

### For HTTP Deployments

No action needed - defaults work fine.

---

## Monitoring and Debugging

### View Detailed Logs

1. Go to **Web** tab
2. Click **Error log** or **Server log**
3. Look for registration logs like:

```
============================================================
NEW USER REGISTRATION ATTEMPT
============================================================
Email: user@example.com
Password length: 12
OTP generated: 123456
```

### Check Health Status

Visit `/health` endpoint any time:
```
https://yourusername.pythonanywhere.com/health
```

### Database Verification

Visit `/db-verify` endpoint:
```
https://yourusername.pythonanywhere.com/db-verify
```

---

## Troubleshooting

### Issue: Still Getting 500 Errors

**Check:**
1. Error log shows the detailed error with stack trace
2. Database file has write permissions
3. No disk space issues

**Solution:**
- The new logging will show exactly what's wrong
- Check error log for lines starting with "REGISTRATION ERROR"

### Issue: Redirect Loop Still Happening

**Check:**
1. Clear ALL browser cookies for your domain
2. Try in incognito/private browsing mode
3. Check if you have any browser extensions blocking redirects

**Solution:**
- The before_request hook should prevent this
- Check server log to see which endpoints are being accessed

### Issue: OTP Email Not Received

**Check:**
1. Environment variables set correctly:
   - `SMTP_SERVER`
   - `SMTP_PORT`
   - `SENDER_EMAIL`
   - `EMAIL_PASSWORD`

**Solution:**
- OTP code will be shown on screen if email not configured
- Set up app-specific password for Gmail
- Check spam folder

---

## Rollback Plan (If Needed)

If something goes wrong:

```bash
cd /home/yourusername/your-project-directory
git log --oneline -5  # See recent commits
git checkout <previous-commit-hash>
```

Then reload the web app.

---

## Expected Behavior After Deployment

### ✅ Registration Works
- New users can sign up
- OTP verification succeeds
- Account created without errors
- Redirects to login page

### ✅ Login Works
- Users can log in
- Proper redirect based on role
- Session persists correctly

### ✅ No Redirect Loops
- Public pages accessible
- Protected pages require auth
- No circular redirects

### ✅ Detailed Logging
- All registration attempts logged
- Errors show full context
- Easy to debug issues

---

## Success Indicators

After deployment, you should see:

1. **Registration Success:** Users can create accounts
2. **Login Success:** Users can log in
3. **No 500 Errors:** All pages load correctly
4. **No Redirect Loops:** Navigation works smoothly
5. **Health Check:** Returns "healthy" status

---

## Need Help?

1. **Check logs first:**
   - Error log has detailed information
   - Look for "REGISTRATION ERROR" or similar

2. **Review documentation:**
   - CRITICAL_ISSUES_RESOLVED.md - Full technical details
   - README.md - General information

3. **Test locally:**
   ```bash
   python test_registration.py
   ```

---

## Post-Deployment Checklist

- [ ] Code pulled from GitHub
- [ ] Web app reloaded
- [ ] Health endpoint returns "healthy"
- [ ] Test registration with new email
- [ ] Test login with credentials
- [ ] Check error log for issues
- [ ] Verify no redirect loops
- [ ] Monitor for a few hours

---

## Summary

**Time to Deploy:** < 5 minutes  
**Risk Level:** Low (only fixes, no breaking changes)  
**Testing Required:** Minimal (pre-tested)  
**Rollback Available:** Yes (git checkout)

**The fixes are production-ready and thoroughly tested!**

---

Last Updated: December 18, 2024  
Version: 4.0.1  
Status: ✅ Ready for Production
