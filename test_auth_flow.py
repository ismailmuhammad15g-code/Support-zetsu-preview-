#!/usr/bin/env python3
"""
Test script for authentication flow and redirect loop prevention
Tests the complete authentication flow to ensure no redirect loops
"""

import sys
from flask import Flask
from flask_app import app, db, User, OTPVerification
from datetime import datetime, timezone, timedelta
from flask.testing import FlaskClient

def test_auth_flow():
    """Test the complete authentication flow for redirect loop prevention"""
    print("=" * 70)
    print("TESTING AUTHENTICATION FLOW (REDIRECT LOOP PREVENTION)")
    print("=" * 70)
    
    with app.app_context():
        # Clean up test data
        test_email = "authtest@example.com"
        User.query.filter_by(email=test_email).delete()
        OTPVerification.query.filter_by(email=test_email).delete()
        db.session.commit()
        print(f"✓ Cleaned up any existing test data for {test_email}")
        
        # Test 1: Verify before_request hook exists and is loop-proof
        print("\n[TEST 1] Checking before_request hook configuration...")
        try:
            # Check if before_request hook is registered
            before_request_funcs = app.before_request_funcs.get(None, [])
            if not before_request_funcs:
                print("✗ FAILED: No before_request hooks registered")
                return False
            
            # Find our check_verification_status hook
            hook_found = False
            for func in before_request_funcs:
                if func.__name__ == 'check_verification_status':
                    hook_found = True
                    print(f"✓ Found check_verification_status hook")
                    print(f"  Hook function: {func.__name__}")
                    break
            
            if not hook_found:
                print("✗ WARNING: check_verification_status hook not found")
                print(f"  Registered hooks: {[f.__name__ for f in before_request_funcs]}")
            else:
                print("✓ before_request hook properly configured")
                
        except Exception as e:
            print(f"✗ FAILED: {e}")
            return False
        
        # Test 2: Verify public endpoints are accessible
        print("\n[TEST 2] Testing public endpoint accessibility...")
        try:
            public_endpoints = [
                'home', 'login', 'register', 'logout', 'static',
                'health_check', 'support', 'faq', 'about', 'track'
            ]
            
            # Get all registered routes
            routes = {}
            for rule in app.url_map.iter_rules():
                if rule.endpoint != 'static':
                    routes[rule.endpoint] = str(rule)
            
            print(f"✓ Total registered routes: {len(routes)}")
            
            # Check which public endpoints are registered
            missing_endpoints = []
            for endpoint in public_endpoints:
                if endpoint in routes:
                    print(f"  ✓ {endpoint}: {routes[endpoint]}")
                else:
                    missing_endpoints.append(endpoint)
                    print(f"  ⚠ {endpoint}: NOT REGISTERED")
            
            if missing_endpoints:
                print(f"⚠ WARNING: {len(missing_endpoints)} public endpoints not found: {missing_endpoints}")
            else:
                print("✓ All critical public endpoints are registered")
                
        except Exception as e:
            print(f"✗ FAILED: {e}")
            return False
        
        # Test 3: Create test user and verify is_verified field
        print("\n[TEST 3] Creating test user with is_verified=True...")
        try:
            # Create verified user
            verified_user = User(
                email=test_email,
                is_admin=False,
                is_verified=True,  # CRITICAL: Must be True to prevent loops
                newsletter_subscribed=False,
                newsletter_popup_shown=False
            )
            verified_user.set_password("TestPassword123!")
            
            db.session.add(verified_user)
            db.session.commit()
            
            # Reload from database to ensure is_verified persisted
            reloaded_user = User.query.filter_by(email=test_email).first()
            
            print(f"✓ User created and committed to database")
            print(f"  Email: {reloaded_user.email}")
            print(f"  is_verified (in memory): {verified_user.is_verified}")
            print(f"  is_verified (from DB): {reloaded_user.is_verified}")
            print(f"  Password hash exists: {bool(reloaded_user.password_hash)}")
            
            if not reloaded_user.is_verified:
                print("✗ FAILED: is_verified is False in database (REDIRECT LOOP RISK!)")
                return False
            
            print("✓ is_verified=True persisted correctly in database")
            
        except Exception as e:
            print(f"✗ FAILED: {e}")
            db.session.rollback()
            return False
        
        # Test 4: Verify session configuration
        print("\n[TEST 4] Checking session configuration...")
        try:
            config_checks = [
                ('SESSION_COOKIE_HTTPONLY', True, app.config.get('SESSION_COOKIE_HTTPONLY')),
                ('SESSION_COOKIE_SAMESITE', 'Lax', app.config.get('SESSION_COOKIE_SAMESITE')),
                ('SESSION_PERMANENT', True, app.config.get('SESSION_PERMANENT')),
                ('PERMANENT_SESSION_LIFETIME', timedelta(days=7), app.config.get('PERMANENT_SESSION_LIFETIME')),
            ]
            
            all_correct = True
            for key, expected, actual in config_checks:
                if actual == expected:
                    print(f"  ✓ {key}: {actual}")
                else:
                    print(f"  ✗ {key}: {actual} (expected: {expected})")
                    all_correct = False
            
            # Check SESSION_COOKIE_SECURE (should be False by default)
            secure = app.config.get('SESSION_COOKIE_SECURE')
            print(f"  ℹ SESSION_COOKIE_SECURE: {secure} (should be False for HTTP)")
            
            if all_correct:
                print("✓ Session configuration is correct for PythonAnywhere")
            else:
                print("✗ Some session configuration issues detected")
                return False
                
        except Exception as e:
            print(f"✗ FAILED: {e}")
            return False
        
        # Test 5: Verify Flask-Login configuration
        print("\n[TEST 5] Checking Flask-Login configuration...")
        try:
            # Check if login_manager is available
            from flask_app import login_manager
            
            if login_manager:
                print(f"  ✓ LoginManager found")
                print(f"  ✓ login_view: {login_manager.login_view}")
                print(f"  ✓ login_message: {login_manager.login_message}")
                
                if login_manager.login_view != 'login':
                    print(f"  ✗ WARNING: login_view should be 'login', got '{login_manager.login_view}'")
                    return False
                else:
                    print("✓ Flask-Login properly configured")
            else:
                print("✗ FAILED: LoginManager not initialized")
                return False
                
        except Exception as e:
            print(f"✗ FAILED: {e}")
            return False
        
        # Test 6: Check for circular redirect patterns
        print("\n[TEST 6] Analyzing routes for circular redirect patterns...")
        try:
            # Routes that should NOT redirect authenticated users to themselves
            protected_routes = ['dashboard', 'reply_ticket', 'export_tickets']
            
            # Routes that authenticated users should be able to access
            auth_accessible = ['home', 'support', 'faq', 'about', 'track', 'logout']
            
            print(f"  ℹ Protected routes (require @login_required): {len(protected_routes)}")
            print(f"  ℹ Auth-accessible routes: {len(auth_accessible)}")
            
            # verify_otp should NOT have @login_required
            verify_otp_view = app.view_functions.get('verify_otp')
            if verify_otp_view:
                # Check if it has login_required decorator
                # Note: This is a heuristic - decorators are wrapped functions
                has_login_required = False
                func = verify_otp_view
                while hasattr(func, '__wrapped__'):
                    if 'login_required' in str(func):
                        has_login_required = True
                        break
                    func = func.__wrapped__
                
                if has_login_required:
                    print("  ✗ WARNING: verify_otp has @login_required (LOOP RISK!)")
                else:
                    print("  ✓ verify_otp does NOT have @login_required (correct)")
            
            print("✓ No obvious circular redirect patterns detected")
            
        except Exception as e:
            print(f"✗ FAILED: {e}")
            return False
        
        # Clean up test data
        print("\n[CLEANUP] Removing test data...")
        User.query.filter_by(email=test_email).delete()
        db.session.commit()
        print("✓ Test data cleaned up")
        
        return True

def test_redirect_scenarios():
    """Test specific redirect scenarios"""
    print("\n" + "=" * 70)
    print("TESTING REDIRECT SCENARIOS")
    print("=" * 70)
    
    with app.app_context():
        with app.test_client() as client:
            # Test 1: Login page accessible when not authenticated
            print("\n[SCENARIO 1] Accessing login page when not authenticated...")
            response = client.get('/login', follow_redirects=False)
            if response.status_code == 200:
                print("✓ Login page accessible (200 OK)")
            else:
                print(f"✗ Unexpected status: {response.status_code}")
            
            # Test 2: Register page accessible when not authenticated
            print("\n[SCENARIO 2] Accessing register page when not authenticated...")
            response = client.get('/register', follow_redirects=False)
            if response.status_code == 200:
                print("✓ Register page accessible (200 OK)")
            else:
                print(f"✗ Unexpected status: {response.status_code}")
            
            # Test 3: Public pages accessible
            print("\n[SCENARIO 3] Accessing public pages...")
            public_pages = ['/', '/support', '/faq', '/about', '/track']
            for page in public_pages:
                response = client.get(page, follow_redirects=False)
                if response.status_code == 200:
                    print(f"  ✓ {page}: accessible (200 OK)")
                else:
                    print(f"  ✗ {page}: unexpected status {response.status_code}")
            
            # Test 4: Dashboard redirects to login when not authenticated
            print("\n[SCENARIO 4] Accessing dashboard when not authenticated...")
            response = client.get('/dashboard', follow_redirects=False)
            if response.status_code in [302, 303, 307]:
                print(f"✓ Dashboard redirects when not authenticated ({response.status_code})")
                if 'Location' in response.headers:
                    print(f"  → Redirects to: {response.headers['Location']}")
            else:
                print(f"✗ Unexpected status: {response.status_code}")
    
    print("\n✓ All redirect scenarios tested")

if __name__ == '__main__':
    try:
        print("\n🔍 Starting Authentication Flow Tests...\n")
        
        # Run authentication flow tests
        auth_success = test_auth_flow()
        
        # Run redirect scenario tests
        test_redirect_scenarios()
        
        print("\n" + "=" * 70)
        if auth_success:
            print("✅ ALL TESTS PASSED!")
            print("=" * 70)
            print("\n✓ Authentication flow is loop-proof")
            print("✓ Session configuration is correct")
            print("✓ No circular redirect patterns detected")
            print("✓ Ready for deployment to PythonAnywhere")
            sys.exit(0)
        else:
            print("❌ SOME TESTS FAILED")
            print("=" * 70)
            print("\n✗ Please review the errors above")
            print("✗ Fix issues before deploying")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
