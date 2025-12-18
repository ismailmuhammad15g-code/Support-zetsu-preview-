# Critical Bug Fixes for Flask Application

## Summary
This document summarizes the critical bug fixes applied to resolve the "500 Internal Server Error" during OTP verification process on PythonAnywhere deployment.

## Issues Identified and Fixed

### 1. Missing `name` Column in Users Table ✅
**Problem**: The database schema was missing the `name` column in the `users` table, causing `sqlalchemy.exc.OperationalError: no such column: users.name`.

**Fix**: Added `name` column to the User model:
```python
name = db.Column(db.String(100), nullable=True)
```

**Location**: `flask_app.py`, User model definition

**Migration**: Run `python db_migrate.py` and select option 1 to add missing columns to existing databases.

---

### 2. Timezone Comparison Conflict ✅
**Problem**: The `is_expired` method in OTP model was comparing offset-naive and offset-aware datetimes, causing `TypeError: can't compare offset-naive and offset-aware datetimes`.

**Root Cause**: SQLite stores datetimes as naive (without timezone info), but the comparison used `datetime.now(timezone.utc)` which is timezone-aware.

**Fix**: Updated `is_expired` method to handle timezone-naive datetimes:
```python
def is_expired(self):
    """Check if OTP is expired"""
    # SQLite stores datetimes as naive, so we need to make expires_at timezone-aware
    # if it isn't already
    if self.expires_at.tzinfo is None:
        # Assume stored time is UTC
        expires_at_utc = self.expires_at.replace(tzinfo=timezone.utc)
    else:
        expires_at_utc = self.expires_at
    
    return datetime.now(timezone.utc) > expires_at_utc
```

**Location**: `flask_app.py`, lines 239-248

---

### 3. Database Path Configuration ✅
**Problem**: The SQLALCHEMY_DATABASE_URI was using a relative path that didn't work on PythonAnywhere.

**Fix**: Implemented automatic detection of deployment environment:
```python
# Database configuration
# Absolute path for PythonAnywhere deployment
# Check if we're on PythonAnywhere by looking for the directory
pythonwhere_db_path = '/home/Supportzetsu/Support-zetsu-preview-/instance/support_tickets.db'
if os.path.exists('/home/Supportzetsu/Support-zetsu-preview-'):
    default_db_uri = f'sqlite:///{pythonwhere_db_path}'
    # Ensure instance directory exists on PythonAnywhere
    os.makedirs('/home/Supportzetsu/Support-zetsu-preview-/instance', exist_ok=True)
else:
    # Local development - use relative path
    instance_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
    os.makedirs(instance_dir, exist_ok=True)
    default_db_uri = f'sqlite:///{instance_dir}/support_tickets.db'

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', default_db_uri)
```

**Location**: `flask_app.py`, lines 57-70

**Benefits**:
- Automatically uses absolute path on PythonAnywhere
- Falls back to relative path for local development
- Creates instance directory if it doesn't exist

---

### 4. SECRET_KEY Configuration ✅
**Problem**: The SECRET_KEY was using a weak default value ('dev-only-insecure-key-change-in-production').

**Fix**: Updated to use a secure hardcoded production key:
```python
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a7f8d6e5c4b3a2f1e0d9c8b7a6f5e4d3c2b1a0f9e8d7c6b5a4f3e2d1c0b9a8f7')
```

**Location**: `flask_app.py`, line 44

**Note**: This provides a secure fallback per the deployment requirements. For maximum security in production, it's strongly recommended to set the SECRET_KEY environment variable on PythonAnywhere to override this default.

---

### 5. Instance Directory Creation ✅
**Problem**: The instance directory didn't exist, causing database file creation failures.

**Fix**: Added automatic directory creation in database configuration (see fix #3 above).

---

## Database Migration

To apply these fixes to an existing database:

1. **Backup your current database**:
   ```bash
   cp instance/support_tickets.db instance/support_tickets.db.backup
   ```

2. **Run the migration script**:
   ```bash
   python db_migrate.py
   ```

3. **Select option 1** to fix missing columns

4. **Verify the schema**:
   ```bash
   python -c "from flask_app import app, db; from sqlalchemy import inspect; 
   with app.app_context(): 
       inspector = inspect(db.engine); 
       print([col['name'] for col in inspector.get_columns('users')])"
   ```

Expected output should include: `['id', 'email', 'password_hash', 'is_admin', 'is_verified', 'name', 'newsletter_subscribed', 'newsletter_popup_shown', 'created_at']`

---

## Testing

All fixes have been validated with comprehensive tests:

### Test 1: User Creation with All Fields ✅
- Creates a user with all required fields including `name`
- Verifies `is_verified` is properly set
- Confirms password hashing works correctly

### Test 2: OTP Creation and Expiration ✅
- Creates valid and expired OTPs
- Verifies `is_expired()` method works correctly
- Confirms timezone handling is correct

### Test 3: Full Registration Flow ✅
- Simulates complete OTP verification process
- Creates OTP → Verifies OTP → Creates User
- Validates all user fields are properly set

### Test 4: Database Migration ✅
- Tests adding missing columns to existing tables
- Verifies SQLite ALTER TABLE functionality

---

## Deployment Checklist for PythonAnywhere

1. ✅ Upload updated `flask_app.py` to PythonAnywhere
2. ✅ Upload updated `db_migrate.py` to PythonAnywhere
3. ✅ Run migration script: `python db_migrate.py` and select option 1
4. ✅ Verify database path is correct: `/home/Supportzetsu/Support-zetsu-preview-/instance/support_tickets.db`
5. ✅ Set environment variables (optional but recommended):
   - `SECRET_KEY` - for enhanced security
   - `SMTP_SERVER`, `SMTP_PORT`, `SENDER_EMAIL`, `EMAIL_PASSWORD` - for OTP email delivery
6. ✅ Reload the web app in PythonAnywhere console
7. ✅ Test registration and OTP verification

---

## Verification Steps

After deployment, verify the fixes:

1. **Check Health Endpoint**:
   ```
   https://supportzetsu.pythonanywhere.com/health
   ```
   Should show all database columns exist.

2. **Test Registration**:
   - Go to registration page
   - Enter email and password
   - Verify OTP is generated (check logs or email)
   - Enter OTP on verification page
   - Should successfully create user without 500 error

3. **Check Database Schema**:
   ```
   https://supportzetsu.pythonanywhere.com/db-verify
   ```
   Should show `users` table with `name` column.

---

## Summary of Changes

**Files Modified**:
1. `flask_app.py` - Core fixes for User model, OTP timezone handling, database configuration
2. `db_migrate.py` - Enhanced to handle missing `name` column and other user fields
3. `BUGFIX_SUMMARY.md` - Comprehensive documentation of all fixes

**Key Improvements**:
- ✅ Fixed database schema mismatch (added `name` column)
- ✅ Fixed timezone comparison issue in OTP expiration check
- ✅ Configured absolute database path for PythonAnywhere
- ✅ Hardcoded secure SECRET_KEY with environment variable fallback
- ✅ Automatic instance directory creation
- ✅ Enhanced database migration script

**Security Note**: 
While the SECRET_KEY is hardcoded per deployment requirements, it's highly recommended to:
1. Set a unique SECRET_KEY via environment variable on PythonAnywhere
2. Change the default key if deploying to a public-facing server
3. Keep the repository private to protect the hardcoded key

**Result**: OTP verification process should now work without 500 errors! 🎉

---

## Support

If you encounter any issues after applying these fixes, check:
1. Flask application logs on PythonAnywhere
2. `/health` endpoint for database connection status
3. `/db-verify` endpoint for schema verification

For additional help, review the error logs at `/var/log/` on PythonAnywhere.
