"""
Database Migration Utility for ZetsuServ Support Portal
This script helps diagnose and fix database schema issues
"""

import os
import sys
from flask_app import app, db, User, Ticket, FAQ, OTPVerification, NewsletterSubscription, News, PushSubscription
from sqlalchemy import inspect, text

def check_database_connection():
    """Check if database connection is working"""
    print("=" * 60)
    print("CHECKING DATABASE CONNECTION")
    print("=" * 60)
    
    try:
        with app.app_context():
            # Try a simple query
            result = db.session.execute(text('SELECT 1')).scalar()
            if result == 1:
                print("✓ Database connection: OK")
                print(f"  Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
                return True
            else:
                print("✗ Database connection: FAILED")
                return False
    except Exception as e:
        print(f"✗ Database connection: ERROR - {e}")
        return False


def check_table_exists(table_name):
    """Check if a specific table exists"""
    try:
        with app.app_context():
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            return table_name in tables
    except Exception as e:
        print(f"Error checking table {table_name}: {e}")
        return False


def verify_schema():
    """Verify all tables and columns exist"""
    print("\n" + "=" * 60)
    print("VERIFYING DATABASE SCHEMA")
    print("=" * 60)
    
    expected_tables = {
        'users': ['id', 'email', 'password_hash', 'is_admin', 'is_verified', 
                  'newsletter_subscribed', 'newsletter_popup_shown', 'created_at'],
        'tickets': ['id', 'ticket_id', 'name', 'email', 'issue_type', 'priority', 
                   'message', 'status', 'attachment_filename', 'admin_reply', 
                   'created_at', 'updated_at'],
        'faqs': ['id', 'question', 'answer', 'category', 'order', 'created_at'],
        'otp_verifications': ['id', 'email', 'otp_code', 'expires_at', 'verified', 'created_at'],
        'newsletter_subscriptions': ['id', 'email', 'user_id', 'subscribed_at'],
        'news': ['id', 'title', 'content', 'author_id', 'published_at'],
        'push_subscriptions': ['id', 'user_id', 'endpoint', 'p256dh_key', 'auth_key', 'subscribed_at']
    }
    
    try:
        with app.app_context():
            inspector = inspect(db.engine)
            
            for table_name, expected_columns in expected_tables.items():
                if check_table_exists(table_name):
                    print(f"\n✓ Table '{table_name}' exists")
                    
                    # Check columns
                    actual_columns = [col['name'] for col in inspector.get_columns(table_name)]
                    
                    missing_columns = set(expected_columns) - set(actual_columns)
                    extra_columns = set(actual_columns) - set(expected_columns)
                    
                    if not missing_columns and not extra_columns:
                        print(f"  ✓ All columns present and correct")
                    else:
                        if missing_columns:
                            print(f"  ⚠ Missing columns: {', '.join(missing_columns)}")
                        if extra_columns:
                            print(f"  ℹ Extra columns: {', '.join(extra_columns)}")
                    
                    # Show row count
                    count = db.session.execute(text(f'SELECT COUNT(*) FROM {table_name}')).scalar()
                    print(f"  Records: {count}")
                else:
                    print(f"\n✗ Table '{table_name}' DOES NOT EXIST")
            
            return True
            
    except Exception as e:
        print(f"\n✗ Schema verification failed: {e}")
        return False


def fix_missing_column():
    """Add missing admin_reply column if it doesn't exist"""
    print("\n" + "=" * 60)
    print("FIXING MISSING COLUMNS")
    print("=" * 60)
    
    try:
        with app.app_context():
            inspector = inspect(db.engine)
            
            if check_table_exists('tickets'):
                columns = [col['name'] for col in inspector.get_columns('tickets')]
                
                if 'admin_reply' not in columns:
                    print("⚠ 'admin_reply' column missing from 'tickets' table")
                    print("  Adding column...")
                    
                    # Add the column
                    db.session.execute(text('ALTER TABLE tickets ADD COLUMN admin_reply TEXT'))
                    db.session.commit()
                    
                    print("✓ Column 'admin_reply' added successfully")
                    return True
                else:
                    print("✓ Column 'admin_reply' already exists")
                    return True
            else:
                print("✗ Table 'tickets' does not exist. Run create_all() first.")
                return False
                
    except Exception as e:
        print(f"✗ Error fixing columns: {e}")
        db.session.rollback()
        return False


def recreate_database():
    """Recreate all database tables (WARNING: This will delete all data!)"""
    print("\n" + "=" * 60)
    print("RECREATING DATABASE (ALL DATA WILL BE LOST!)")
    print("=" * 60)
    
    response = input("Are you sure you want to recreate the database? (yes/no): ")
    
    if response.lower() != 'yes':
        print("Operation cancelled.")
        return False
    
    try:
        with app.app_context():
            print("Dropping all tables...")
            db.drop_all()
            
            print("Creating all tables...")
            db.create_all()
            
            print("✓ Database recreated successfully")
            
            # Add sample FAQ data
            print("Adding sample FAQ data...")
            sample_faqs = [
                FAQ(question="How do I submit a support ticket?",
                    answer="Click on 'Support' in the navigation menu, fill out the form with your details, and click 'Submit Ticket'. You'll receive a confirmation email with your ticket ID.",
                    category="General", order=1),
                FAQ(question="What is the expected response time?",
                    answer="We aim to respond to all tickets within 24 hours during business days. Urgent issues are prioritized and typically receive a response within 4 hours.",
                    category="Support", order=2),
                FAQ(question="Can I track my ticket status?",
                    answer="Yes! You can track your ticket status on the 'Track Ticket' page using your ticket ID or email address.",
                    category="Support", order=3),
            ]
            db.session.bulk_save_objects(sample_faqs)
            db.session.commit()
            
            print("✓ Sample data added")
            return True
            
    except Exception as e:
        print(f"✗ Error recreating database: {e}")
        db.session.rollback()
        return False


def show_statistics():
    """Show database statistics"""
    print("\n" + "=" * 60)
    print("DATABASE STATISTICS")
    print("=" * 60)
    
    try:
        with app.app_context():
            stats = {
                'Users': User.query.count(),
                'Tickets': Ticket.query.count(),
                'FAQs': FAQ.query.count(),
                'OTP Verifications': OTPVerification.query.count(),
                'Newsletter Subscriptions': NewsletterSubscription.query.count(),
                'News Items': News.query.count(),
                'Push Subscriptions': PushSubscription.query.count(),
            }
            
            for name, count in stats.items():
                print(f"  {name}: {count}")
            
            # Show admin users
            admins = User.query.filter_by(is_admin=True).all()
            if admins:
                print(f"\n  Admin users:")
                for admin in admins:
                    print(f"    - {admin.email} (verified: {admin.is_verified})")
            else:
                print("\n  ⚠ No admin users found")
            
            return True
            
    except Exception as e:
        print(f"✗ Error getting statistics: {e}")
        return False


def main():
    """Main migration script"""
    print("\n" + "=" * 60)
    print("ZETSUSERV SUPPORT PORTAL - DATABASE MIGRATION UTILITY")
    print("=" * 60)
    
    # Check connection
    if not check_database_connection():
        print("\n✗ Cannot proceed without database connection.")
        sys.exit(1)
    
    # Verify schema
    verify_schema()
    
    # Show statistics
    show_statistics()
    
    # Interactive menu
    while True:
        print("\n" + "=" * 60)
        print("MIGRATION OPTIONS")
        print("=" * 60)
        print("1. Fix missing columns (safe - no data loss)")
        print("2. Recreate database (WARNING: deletes all data)")
        print("3. Re-run diagnostics")
        print("4. Exit")
        print("=" * 60)
        
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == '1':
            fix_missing_column()
        elif choice == '2':
            recreate_database()
        elif choice == '3':
            check_database_connection()
            verify_schema()
            show_statistics()
        elif choice == '4':
            print("\nExiting...")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == '__main__':
    main()
