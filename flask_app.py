"""
ZetsuServ Support Portal - Flask Application v4.0.0
A professional support portal with Microsoft Fluent Design
Designed for deployment on PythonAnywhere with CPU Optimization
Features: Open Registration with OTP, Newsletter, Admin Broadcast, Web Push Notifications
CPU-Optimized for low resource usage on shared hosting
"""

import os
import re
import csv
import io
import smtplib
import secrets
import requests
import logging
import time
import json
from datetime import datetime, timezone, timedelta
from html import escape
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template, request, redirect, url_for, flash, session, Response, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask application
app = Flask(__name__)

# Configure Flask app
# IMPORTANT: Set SECRET_KEY via environment variable in production
# Generate with: python -c "import secrets; print(secrets.token_hex(32))"
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-only-insecure-key-change-in-production')

# CSRF Protection
csrf = CSRFProtect(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///support_tickets.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# File upload configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}
IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Email configuration
# IMPORTANT: Set these via environment variables in production
# For development/testing only, you can set these in your environment:
# export SMTP_SERVER=smtp.gmail.com
# export SMTP_PORT=587
# export SENDER_EMAIL=zetsuserv@gmail.com
# export EMAIL_PASSWORD=your-app-password
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', '')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')

# n8n Webhook configuration for automation
N8N_WEBHOOK_URL = os.environ.get('N8N_WEBHOOK_URL', '')

# Allowed issue types for validation
ALLOWED_ISSUE_TYPES = {
    "Technical Support",
    "Billing Inquiry",
    "Feature Request",
    "Bug Report",
    "General Question",
    "Account Issue",
    "Product Inquiry",
}

# Ticket priorities
TICKET_PRIORITIES = {
    "Low",
    "Medium",
    "High",
    "Urgent"
}

# CPU Optimization Constants
BATCH_SIZE = 5  # Process 5 users at a time for notifications/emails
BATCH_DELAY = 0.5  # Delay between batches in seconds to prevent CPU spikes
OTP_EXPIRY_MINUTES = 10  # OTP valid for 10 minutes
OTP_LENGTH = 6  # 6-digit OTP

# ========================================
# DATABASE MODELS
# ========================================

class User(UserMixin, db.Model):
    """Database model for users (now open registration with OTP verification)"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    is_verified = db.Column(db.Boolean, nullable=False, default=False)
    newsletter_subscribed = db.Column(db.Boolean, nullable=False, default=False)
    newsletter_popup_shown = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)


class Ticket(db.Model):
    """Database model for support tickets"""
    __tablename__ = 'tickets'
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(254), nullable=False)
    issue_type = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.String(20), nullable=False, default='Medium')
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Open')
    attachment_filename = db.Column(db.String(255), nullable=True)
    admin_reply = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<Ticket {self.ticket_id}>'
    
    def to_dict(self):
        """Convert ticket to dictionary"""
        return {
            'id': self.id,
            'ticket_id': self.ticket_id,
            'name': self.name,
            'email': self.email,
            'issue_type': self.issue_type,
            'priority': self.priority,
            'message': self.message,
            'status': self.status,
            'attachment_filename': self.attachment_filename,
            'admin_reply': self.admin_reply,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }


class FAQ(db.Model):
    """Database model for FAQ items"""
    __tablename__ = 'faqs'
    
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<FAQ {self.question[:50]}>'


class OTPVerification(db.Model):
    """Database model for OTP verification (CPU-optimized with expiry)"""
    __tablename__ = 'otp_verifications'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), nullable=False, index=True)
    otp_code = db.Column(db.String(6), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    verified = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<OTP {self.email}>'
    
    def is_expired(self):
        """Check if OTP is expired"""
        return datetime.now(timezone.utc) > self.expires_at


class NewsletterSubscription(db.Model):
    """Database model for newsletter subscriptions"""
    __tablename__ = 'newsletter_subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    subscribed_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<Newsletter {self.email}>'


class News(db.Model):
    """Database model for admin news broadcasts"""
    __tablename__ = 'news'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    published_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<News {self.title}>'


class PushSubscription(db.Model):
    """Database model for Web Push notification subscriptions"""
    __tablename__ = 'push_subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    endpoint = db.Column(db.String(500), unique=True, nullable=False)
    p256dh_key = db.Column(db.String(500), nullable=False)
    auth_key = db.Column(db.String(500), nullable=False)
    subscribed_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<PushSubscription {self.endpoint[:50]}>'


# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return db.session.get(User, int(user_id))


# Create all database tables
with app.app_context():
    db.create_all()
    
    # Add sample FAQ data if table is empty
    if FAQ.query.count() == 0:
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
            FAQ(question="What file types can I attach?",
                answer="You can attach documents (.pdf, .doc, .docx), images (.png, .jpg, .jpeg, .gif), and text files (.txt). Maximum file size is 5MB.",
                category="Technical", order=4),
            FAQ(question="How do I contact support urgently?",
                answer="For urgent issues, select 'Urgent' priority when submitting your ticket. Our team monitors urgent tickets 24/7.",
                category="Support", order=5),
        ]
        db.session.bulk_save_objects(sample_faqs)
        db.session.commit()

# ========================================
# UTILITY FUNCTIONS
# ========================================

def generate_ticket_id():
    """Generate a unique ticket ID"""
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%d')
    random_str = secrets.token_hex(4).upper()
    return f"ZS-{timestamp}-{random_str}"


def generate_otp():
    """Generate a 6-digit OTP code"""
    return ''.join([str(secrets.randbelow(10)) for _ in range(OTP_LENGTH)])


def send_otp_email(user_email, otp_code):
    """
    Send OTP verification email (CPU-optimized)
    Returns True if successful, False otherwise
    """
    if not SENDER_EMAIL or not EMAIL_PASSWORD:
        logger.info("Email credentials not configured. Skipping OTP email send.")
        return False
    
    safe_email = escape(user_email)
    safe_otp = escape(otp_code)
    
    try:
        msg = MIMEMultipart()
        msg['Subject'] = f"Your ZetsuServ Verification Code: {safe_otp}"
        msg['From'] = SENDER_EMAIL
        msg['To'] = user_email
        
        body = f"""
        <html>
        <body style="font-family: 'Segoe UI', Arial, sans-serif; color: #201F1E; background-color: #FAF9F8; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; padding: 32px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <h2 style="color: #0078D4; margin-bottom: 24px;">Welcome to ZetsuServ Support!</h2>
                <p style="color: #323130; line-height: 1.6;">Your verification code is:</p>
                
                <div style="background: #F3F2F1; border-radius: 4px; padding: 20px; margin: 24px 0; text-align: center;">
                    <h1 style="color: #0078D4; font-size: 48px; letter-spacing: 8px; margin: 0;">{safe_otp}</h1>
                </div>
                
                <p style="color: #323130; line-height: 1.6;">This code will expire in {OTP_EXPIRY_MINUTES} minutes.</p>
                <p style="color: #605E5C; line-height: 1.6; font-size: 14px;">If you didn't request this code, please ignore this email.</p>
                
                <hr style="border: none; border-top: 1px solid #E1DFDD; margin: 24px 0;">
                <p style="font-size: 12px; color: #A19F9D; text-align: center;">Powered by ZetsuServ Support Portal v4.0.0</p>
            </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))
        
        # Use context manager for automatic cleanup
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, EMAIL_PASSWORD)
            server.sendmail(SENDER_EMAIL, user_email, msg.as_string())
        
        return True
    except Exception as e:
        logger.error(f"Error sending OTP email: {e}")
        return False


def batch_process_users(user_emails, callback_fn, *args, **kwargs):
    """
    CPU-optimized batch processing for sending emails/notifications
    Processes users in batches with delays to prevent CPU spikes
    
    Args:
        user_emails: List of email addresses
        callback_fn: Function to call for each email
        *args, **kwargs: Additional arguments for callback
    
    Returns:
        Dictionary with success/failure counts
    """
    results = {'success': 0, 'failed': 0}
    
    for i in range(0, len(user_emails), BATCH_SIZE):
        batch = user_emails[i:i + BATCH_SIZE]
        
        for email in batch:
            try:
                if callback_fn(email, *args, **kwargs):
                    results['success'] += 1
                else:
                    results['failed'] += 1
            except Exception as e:
                logger.error(f"Error processing {email}: {e}")
                results['failed'] += 1
        
        # Delay between batches to prevent CPU spikes
        if i + BATCH_SIZE < len(user_emails):
            time.sleep(BATCH_DELAY)
    
    return results

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def is_image_file(filename):
    """Check if file is an image based on extension"""
    if not filename:
        return False
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in IMAGE_EXTENSIONS


def validate_email(email):
    """
    Validate email format using regex
    Returns True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def send_email(user_email, user_name, user_message, issue_type, ticket_id=None, priority='Medium'):
    """
    Send email notifications for support ticket
    Sends confirmation to user and notification to admin
    Returns True if successful, False otherwise
    """
    # Check if email credentials are configured
    if not SENDER_EMAIL or not EMAIL_PASSWORD:
        logger.info("Email credentials not configured. Skipping email send.")
        return False
    
    # Escape user input to prevent XSS in emails
    safe_name = escape(user_name)
    safe_email = escape(user_email)
    safe_type = escape(issue_type)
    safe_message = escape(user_message)
    safe_ticket_id = escape(ticket_id) if ticket_id else "N/A"
    safe_priority = escape(priority)
    
    try:
        # Email to Admin (Notification)
        msg_admin = MIMEMultipart()
        msg_admin['Subject'] = f"[{safe_priority}] New Ticket: {safe_type} - {safe_ticket_id}"
        msg_admin['From'] = SENDER_EMAIL
        msg_admin['To'] = SENDER_EMAIL
        
        admin_body = f"""
        <html>
        <body style="font-family: 'Segoe UI', Arial, sans-serif; color: #201F1E; background-color: #FAF9F8; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; padding: 32px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <h2 style="color: #0078D4; margin-bottom: 24px;">New Support Request</h2>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="border-bottom: 1px solid #E1DFDD;">
                        <td style="padding: 12px 0; font-weight: 600; color: #323130;">Ticket ID:</td>
                        <td style="padding: 12px 0; color: #605E5C;">{safe_ticket_id}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #E1DFDD;">
                        <td style="padding: 12px 0; font-weight: 600; color: #323130;">Priority:</td>
                        <td style="padding: 12px 0; color: #605E5C;"><strong>{safe_priority}</strong></td>
                    </tr>
                    <tr style="border-bottom: 1px solid #E1DFDD;">
                        <td style="padding: 12px 0; font-weight: 600; color: #323130;">Name:</td>
                        <td style="padding: 12px 0; color: #605E5C;">{safe_name}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #E1DFDD;">
                        <td style="padding: 12px 0; font-weight: 600; color: #323130;">Email:</td>
                        <td style="padding: 12px 0; color: #605E5C;">{safe_email}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #E1DFDD;">
                        <td style="padding: 12px 0; font-weight: 600; color: #323130;">Type:</td>
                        <td style="padding: 12px 0; color: #605E5C;">{safe_type}</td>
                    </tr>
                </table>
                <div style="margin-top: 24px;">
                    <p style="font-weight: 600; color: #323130; margin-bottom: 8px;">Message:</p>
                    <p style="color: #605E5C; line-height: 1.6; white-space: pre-wrap;">{safe_message}</p>
                </div>
                <hr style="border: none; border-top: 1px solid #E1DFDD; margin: 24px 0;">
                <p style="font-size: 12px; color: #A19F9D; text-align: center;">Powered by ZetsuServ AI Support Portal</p>
            </div>
        </body>
        </html>
        """
        msg_admin.attach(MIMEText(admin_body, 'html'))
        
        # Email to User (Confirmation)
        msg_user = MIMEMultipart()
        msg_user['Subject'] = f"Ticket Received - {safe_ticket_id}"
        msg_user['From'] = SENDER_EMAIL
        msg_user['To'] = user_email
        
        user_body = f"""
        <html>
        <body style="font-family: 'Segoe UI', Arial, sans-serif; color: #201F1E; background-color: #FAF9F8; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; padding: 32px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <h2 style="color: #0078D4; margin-bottom: 24px;">Thank You for Contacting ZetsuServ Support</h2>
                <p style="color: #323130; line-height: 1.6;">Dear {safe_name},</p>
                <p style="color: #323130; line-height: 1.6;">We have received your support ticket and our team will get back to you shortly.</p>
                
                <div style="background: #F3F2F1; border-radius: 4px; padding: 20px; margin: 24px 0;">
                    <h3 style="color: #0078D4; margin-bottom: 16px;">Your Ticket Details</h3>
                    <table style="width: 100%;">
                        <tr>
                            <td style="padding: 8px 0; font-weight: 600; color: #323130;">Ticket ID:</td>
                            <td style="padding: 8px 0; color: #605E5C;"><strong>{safe_ticket_id}</strong></td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; font-weight: 600; color: #323130;">Issue Type:</td>
                            <td style="padding: 8px 0; color: #605E5C;">{safe_type}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; font-weight: 600; color: #323130;">Priority:</td>
                            <td style="padding: 8px 0; color: #605E5C;">{safe_priority}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; font-weight: 600; color: #323130;">Status:</td>
                            <td style="padding: 8px 0; color: #605E5C;">Open</td>
                        </tr>
                    </table>
                </div>
                
                <p style="color: #323130; line-height: 1.6;"><strong>Your Message:</strong></p>
                <p style="color: #605E5C; line-height: 1.6; white-space: pre-wrap;">{safe_message}</p>
                
                <div style="margin-top: 24px; padding: 16px; background: #DFF6DD; border-left: 4px solid #107C10; border-radius: 4px;">
                    <p style="color: #107C10; margin: 0; font-weight: 600;">💡 Tip: Save your ticket ID for tracking</p>
                </div>
                
                <hr style="border: none; border-top: 1px solid #E1DFDD; margin: 24px 0;">
                <p style="font-size: 12px; color: #A19F9D; text-align: center;">Powered by ZetsuServ AI Support Portal</p>
            </div>
        </body>
        </html>
        """
        msg_user.attach(MIMEText(user_body, 'html'))
        
        # Connect to SMTP server and send emails
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        try:
            server.starttls()
            server.login(SENDER_EMAIL, EMAIL_PASSWORD)
            
            # Send admin notification
            server.sendmail(SENDER_EMAIL, SENDER_EMAIL, msg_admin.as_string())
            
            # Send user confirmation
            server.sendmail(SENDER_EMAIL, user_email, msg_user.as_string())
            
            return True
        finally:
            # Always close the server connection
            server.quit()
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return False


def send_admin_reply_email(user_email, user_name, ticket_id, original_message, admin_reply):
    """
    Send email to user with admin's reply
    Returns tuple (success: bool, error_message: str or None)
    """
    # Check if email credentials are configured
    if not SENDER_EMAIL or not EMAIL_PASSWORD:
        error_msg = "Email credentials not configured. Please set SENDER_EMAIL and EMAIL_PASSWORD environment variables."
        print(error_msg)
        return False, error_msg
    
    # Escape user input to prevent XSS in emails
    safe_name = escape(user_name)
    safe_email = escape(user_email)
    safe_ticket_id = escape(ticket_id)
    safe_original = escape(original_message)
    safe_reply = escape(admin_reply)
    
    try:
        msg = MIMEMultipart()
        msg['Subject'] = f"Response to Your Ticket - {safe_ticket_id}"
        msg['From'] = SENDER_EMAIL
        msg['To'] = user_email
        
        body = f"""
        <html>
        <body style="font-family: 'Segoe UI', Arial, sans-serif; color: #201F1E; background-color: #FAF9F8; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; padding: 32px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <h2 style="color: #0078D4; margin-bottom: 24px;">We've Responded to Your Support Ticket</h2>
                <p style="color: #323130; line-height: 1.6;">Dear {safe_name},</p>
                <p style="color: #323130; line-height: 1.6;">Our support team has reviewed your ticket and provided a response.</p>
                
                <div style="background: #F3F2F1; border-radius: 4px; padding: 20px; margin: 24px 0;">
                    <h3 style="color: #0078D4; margin-bottom: 16px;">Ticket Information</h3>
                    <table style="width: 100%;">
                        <tr>
                            <td style="padding: 8px 0; font-weight: 600; color: #323130;">Ticket ID:</td>
                            <td style="padding: 8px 0; color: #605E5C;"><strong>{safe_ticket_id}</strong></td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; font-weight: 600; color: #323130;">Status:</td>
                            <td style="padding: 8px 0; color: #605E5C;"><strong>Resolved</strong></td>
                        </tr>
                    </table>
                </div>
                
                <div style="margin-bottom: 24px;">
                    <p style="font-weight: 600; color: #323130; margin-bottom: 8px;">Your Original Message:</p>
                    <p style="color: #605E5C; line-height: 1.6; white-space: pre-wrap; background: #FAF9F8; padding: 12px; border-radius: 4px;">{safe_original}</p>
                </div>
                
                <div style="margin-bottom: 24px;">
                    <p style="font-weight: 600; color: #323130; margin-bottom: 8px;">Admin Response:</p>
                    <div style="background: #E3F2FD; border-left: 4px solid #0078D4; padding: 16px; border-radius: 4px;">
                        <p style="color: #323130; line-height: 1.6; white-space: pre-wrap; margin: 0;">{safe_reply}</p>
                    </div>
                </div>
                
                <div style="margin-top: 24px; padding: 16px; background: #DFF6DD; border-left: 4px solid #107C10; border-radius: 4px;">
                    <p style="color: #107C10; margin: 0; font-weight: 600;">✓ This ticket has been marked as Resolved</p>
                </div>
                
                <p style="color: #605E5C; line-height: 1.6; margin-top: 24px;">If you need further assistance, please feel free to submit a new support ticket.</p>
                
                <hr style="border: none; border-top: 1px solid #E1DFDD; margin: 24px 0;">
                <p style="font-size: 12px; color: #A19F9D; text-align: center;">Powered by ZetsuServ AI Support Portal</p>
            </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))
        
        # Connect to SMTP server and send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        try:
            server.starttls()
            server.login(SENDER_EMAIL, EMAIL_PASSWORD)
            server.sendmail(SENDER_EMAIL, user_email, msg.as_string())
            return True, None
        finally:
            server.quit()
    except smtplib.SMTPAuthenticationError as e:
        error_msg = f"SMTP Authentication failed. Please check SENDER_EMAIL and EMAIL_PASSWORD. Error: {str(e)}"
        print(error_msg)
        return False, error_msg
    except smtplib.SMTPException as e:
        error_msg = f"SMTP error occurred: {str(e)}"
        print(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Error sending admin reply email: {str(e)}"
        print(error_msg)
        return False, error_msg


def send_to_webhook(ticket_data):
    """
    Send ticket data to n8n webhook for automation
    
    Args:
        ticket_data: Dictionary containing ticket information with keys:
                    - name: User's name
                    - email: User's email
                    - issue_type: Type of issue
                    - priority: Ticket priority
                    - message: Issue description
                    - ticket_id: Generated ticket ID
                    - timestamp: ISO format timestamp
    
    Returns:
        True if successful, False otherwise
        
    Raises:
        No exceptions raised - all errors are caught and logged
    """
    # Check if webhook URL is configured
    if not N8N_WEBHOOK_URL:
        print("N8N_WEBHOOK_URL not configured. Skipping webhook send.")
        return False
    
    # Validate webhook URL to prevent SSRF attacks
    try:
        from urllib.parse import urlparse
        parsed_url = urlparse(N8N_WEBHOOK_URL)
        
        # Only allow HTTPS URLs for security
        if parsed_url.scheme not in ['https', 'http']:
            print(f"Invalid webhook URL scheme: {parsed_url.scheme}. Only HTTP/HTTPS allowed.")
            return False
        
        # Block localhost and private IP ranges to prevent SSRF
        if parsed_url.hostname in ['localhost', '127.0.0.1', '0.0.0.0']:
            print("Webhook URL cannot point to localhost (SSRF protection)")
            return False
            
        # Check for private IP ranges (basic check)
        if parsed_url.hostname and (
            parsed_url.hostname.startswith('10.') or
            parsed_url.hostname.startswith('192.168.') or
            parsed_url.hostname.startswith('172.16.')
        ):
            print("Webhook URL cannot point to private IP ranges (SSRF protection)")
            return False
            
    except Exception as e:
        print(f"Error validating webhook URL: {e}")
        return False
    
    try:
        # Prepare payload for webhook
        payload = {
            'name': ticket_data.get('name'),
            'email': ticket_data.get('email'),
            'issue_type': ticket_data.get('issue_type'),
            'priority': ticket_data.get('priority'),
            'message': ticket_data.get('message'),
            'ticket_id': ticket_data.get('ticket_id'),
            'timestamp': ticket_data.get('timestamp')
        }
        
        # Send POST request to webhook with timeout
        response = requests.post(
            N8N_WEBHOOK_URL,
            json=payload,
            timeout=5  # 5 second timeout to prevent hanging
        )
        
        # Check if request was successful
        if response.status_code in [200, 201, 202]:
            print(f"Successfully sent ticket {ticket_data.get('ticket_id')} to webhook")
            return True
        else:
            print(f"Webhook returned status code {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("Webhook request timed out")
        return False
    except requests.exceptions.RequestException as e:
        print(f"Error sending to webhook: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error in webhook send: {e}")
        return False

# ========================================
# ROUTES
# ========================================

@app.route('/')
def home():
    """
    Home page route
    Renders the landing page with hero section and call-to-action
    """
    return render_template('home.html')


@app.route('/support')
def support():
    """
    Support page route
    Renders the support form where users can submit tickets
    """
    return render_template('support.html')


@app.route('/faq')
def faq():
    """
    FAQ page route
    Displays frequently asked questions grouped by category
    """
    faqs = FAQ.query.order_by(FAQ.category, FAQ.order).all()
    
    # Group FAQs by category
    faq_dict = {}
    for faq_item in faqs:
        if faq_item.category not in faq_dict:
            faq_dict[faq_item.category] = []
        faq_dict[faq_item.category].append(faq_item)
    
    return render_template('faq.html', faq_dict=faq_dict)


@app.route('/about')
def about():
    """
    About page route
    Displays information about ZetsuServ
    """
    return render_template('about.html')


@app.route('/track')
def track():
    """
    Track ticket page route
    Allows users to search for their tickets
    """
    return render_template('track.html')


@app.route('/search_ticket', methods=['POST'])
def search_ticket():
    """
    Search for a ticket by ID or email
    """
    search_query = request.form.get('search_query', '').strip()
    
    if not search_query:
        flash('Please enter a ticket ID or email address', 'error')
        return redirect(url_for('track'))
    
    # Search by ticket ID or email
    if search_query.startswith('ZS-'):
        tickets = Ticket.query.filter_by(ticket_id=search_query).all()
    else:
        tickets = Ticket.query.filter_by(email=search_query).order_by(Ticket.created_at.desc()).all()
    
    if not tickets:
        flash('No tickets found matching your search', 'error')
        return redirect(url_for('track'))
    
    return render_template('track.html', tickets=tickets, search_query=search_query)

@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    """
    Serve uploaded files to authenticated admin users only
    Security: Only admin users can view uploaded files
    Path traversal protection: secure_filename is already applied during upload
    """
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    # Additional security: validate filename doesn't contain path traversal attempts
    if '..' in filename or '/' in filename or '\\' in filename:
        flash('Invalid filename.', 'error')
        return redirect(url_for('dashboard'))
    
    # Check if file exists
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.isfile(file_path):
        flash('File not found.', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        print(f"Error serving file: {e}")
        flash('Error accessing file.', 'error')
        return redirect(url_for('dashboard'))


@app.route('/submit', methods=['POST'])
def submit():
    """
    Form submission handler
    Accepts POST requests from the support form
    Validates data, saves to database, sends emails, and redirects with message
    Returns redirect to support page (POST-Redirect-GET pattern)
    """
    # Extract form data with validation
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    issue_type = request.form.get('issue_type', '').strip()
    priority = request.form.get('priority', 'Medium').strip()
    message = request.form.get('message', '').strip()
    
    # Handle file upload
    attachment_filename = None
    if 'attachment' in request.files:
        file = request.files['attachment']
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add timestamp to filename to prevent collisions
            timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
            attachment_filename = f"{timestamp}_{filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], attachment_filename))
    
    # Basic server-side validation - check all fields present
    if not all([name, email, issue_type, message]):
        flash('All fields are required. Please fill out the form completely.', 'error')
        return redirect(url_for('support'))
    
    # Validate field lengths
    if len(name) > 100:
        flash('Name must be less than 100 characters.', 'error')
        return redirect(url_for('support'))
    
    if len(email) > 254:
        flash('Email must be less than 254 characters.', 'error')
        return redirect(url_for('support'))
    
    if len(message) > 2000:
        flash('Message must be less than 2000 characters.', 'error')
        return redirect(url_for('support'))
    
    # Validate email format
    if not validate_email(email):
        flash('Please enter a valid email address.', 'error')
        return redirect(url_for('support'))
    
    # Validate that issue_type is one of the allowed values
    if issue_type not in ALLOWED_ISSUE_TYPES:
        flash('Invalid issue type selected.', 'error')
        return redirect(url_for('support'))
    
    # Validate priority
    if priority not in TICKET_PRIORITIES:
        priority = 'Medium'  # Default to Medium if invalid
    
    try:
        # Generate ticket ID
        ticket_id = generate_ticket_id()
        
        # Create new ticket
        new_ticket = Ticket(
            ticket_id=ticket_id,
            name=name,
            email=email,
            issue_type=issue_type,
            priority=priority,
            message=message,
            attachment_filename=attachment_filename,
            status='Open'
        )
        
        # Save to database
        db.session.add(new_ticket)
        db.session.commit()
        
        # Print to console for debugging
        # Log ticket creation for monitoring
        logger.info("=" * 50)
        logger.info("NEW SUPPORT TICKET RECEIVED")
        logger.info("=" * 50)
        logger.info(f"Ticket ID: {ticket_id}")
        logger.info(f"Name: {name}")
        logger.info(f"Email: {email}")
        logger.info(f"Issue Type: {issue_type}")
        logger.info(f"Priority: {priority}")
        logger.info(f"Message: {message[:100]}...")  # Truncate long messages
        logger.info(f"Attachment: {attachment_filename}")
        logger.info("=" * 50)
        
        # Send email notifications
        email_sent = send_email(email, name, message, issue_type, ticket_id, priority)
        
        # Send to n8n webhook (non-blocking, won't crash app on failure)
        try:
            webhook_data = {
                'ticket_id': ticket_id,
                'name': name,
                'email': email,
                'issue_type': issue_type,
                'priority': priority,
                'message': message,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            send_to_webhook(webhook_data)
        except Exception as webhook_error:
            # Log error but don't crash the app
            print(f"Webhook integration error (non-critical): {webhook_error}")
        
        if email_sent:
            flash(f'Thank you, {name}! Your ticket {ticket_id} has been submitted successfully. We\'ve sent a confirmation to {email}.', 'success')
        else:
            flash(f'Thank you, {name}! Your ticket {ticket_id} has been submitted successfully.', 'success')
        
    except Exception as e:
        db.session.rollback()
        print(f"Error saving ticket: {e}")
        flash('An error occurred while submitting your ticket. Please try again.', 'error')
    
    # Redirect to support page with success message (POST-Redirect-GET pattern)
    return redirect(url_for('support'))


# ========================================
# AUTHENTICATION ROUTES
# ========================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    User registration route with OTP verification (v4.0.0)
    Open registration - no whitelist required
    """
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        # Validate inputs
        if not all([email, password, confirm_password]):
            flash('All fields are required.', 'error')
            return redirect(url_for('register'))
        
        # Validate email format
        if not validate_email(email):
            flash('Please enter a valid email address.', 'error')
            return redirect(url_for('register'))
        
        # Check password match
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('register'))
        
        # Check password strength (minimum 8 characters)
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'error')
            return redirect(url_for('register'))
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('An account with this email already exists.', 'error')
            return redirect(url_for('register'))
        
        try:
            # Generate OTP
            otp_code = generate_otp()
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRY_MINUTES)
            
            # Clean up old OTPs for this email (CPU-optimized)
            OTPVerification.query.filter_by(email=email).delete()
            
            # Create OTP record
            otp_record = OTPVerification(
                email=email,
                otp_code=otp_code,
                expires_at=expires_at
            )
            db.session.add(otp_record)
            
            # Store user data temporarily in session
            session['pending_registration'] = {
                'email': email,
                'password': password
            }
            
            db.session.commit()
            
            # Send OTP email
            if send_otp_email(email, otp_code):
                flash(f'Verification code sent to {email}. Please check your inbox.', 'success')
            else:
                flash(f'Verification code: {otp_code} (Email not configured)', 'info')
            
            return redirect(url_for('verify_otp'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error during registration: {e}")
            flash('An error occurred during registration. Please try again.', 'error')
            return redirect(url_for('register'))
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login route
    """
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        remember = request.form.get('remember', False) == 'on'
        
        # Validate inputs
        if not all([email, password]):
            flash('Email and password are required.', 'error')
            return redirect(url_for('login'))
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        # Check credentials
        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash(f'Welcome back, {user.email}!', 'success')
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')
            return redirect(url_for('login'))
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """
    User logout route
    """
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('home'))


@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    """
    OTP verification route (v4.0.0)
    """
    # Check if there's pending registration
    if 'pending_registration' not in session:
        flash('No pending registration found. Please register first.', 'error')
        return redirect(url_for('register'))
    
    if request.method == 'POST':
        otp_input = request.form.get('otp', '').strip()
        
        if not otp_input:
            flash('Please enter the verification code.', 'error')
            return redirect(url_for('verify_otp'))
        
        email = session['pending_registration']['email']
        password = session['pending_registration']['password']
        
        # Find OTP record (CPU-optimized query)
        otp_record = OTPVerification.query.filter_by(
            email=email,
            verified=False
        ).order_by(OTPVerification.created_at.desc()).first()
        
        if not otp_record:
            flash('Verification code not found. Please register again.', 'error')
            session.pop('pending_registration', None)
            return redirect(url_for('register'))
        
        # Check expiry
        if otp_record.is_expired():
            flash('Verification code has expired. Please register again.', 'error')
            session.pop('pending_registration', None)
            db.session.delete(otp_record)
            db.session.commit()
            return redirect(url_for('register'))
        
        # Verify OTP
        if otp_record.otp_code != otp_input:
            flash('Invalid verification code. Please try again.', 'error')
            return redirect(url_for('verify_otp'))
        
        try:
            # Mark OTP as verified
            otp_record.verified = True
            
            # Check if zetsuserv@gmail.com for admin privileges
            is_admin = (email == 'zetsuserv@gmail.com')
            
            # Create user account
            new_user = User(
                email=email,
                is_admin=is_admin,
                is_verified=True
            )
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            
            # Clean up session
            session.pop('pending_registration', None)
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error completing registration: {e}")
            flash('An error occurred during verification. Please try again.', 'error')
            return redirect(url_for('verify_otp'))
    
    return render_template('verify_otp.html', email=session['pending_registration']['email'])


@app.route('/subscribe_newsletter', methods=['POST'])
@csrf.exempt  # CSRF exempt for AJAX requests with CSRF token in body
def subscribe_newsletter():
    """
    Newsletter subscription endpoint (v4.0.0)
    """
    email = request.form.get('email', '').strip().lower()
    
    if not email or not validate_email(email):
        return jsonify({'success': False, 'message': 'Invalid email address'}), 400
    
    # Validate email length
    if len(email) > 254:
        return jsonify({'success': False, 'message': 'Email too long'}), 400
    
    try:
        # Check if already subscribed
        existing = NewsletterSubscription.query.filter_by(email=email).first()
        if existing:
            return jsonify({'success': True, 'message': 'Already subscribed'}), 200
        
        # Create subscription
        user_id = current_user.id if current_user.is_authenticated else None
        subscription = NewsletterSubscription(email=email, user_id=user_id)
        db.session.add(subscription)
        
        # Update user record if logged in
        if current_user.is_authenticated:
            current_user.newsletter_subscribed = True
            current_user.newsletter_popup_shown = True
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Subscribed successfully!'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error subscribing to newsletter: {e}")
        return jsonify({'success': False, 'message': 'Subscription failed'}), 500


@app.route('/dismiss_newsletter', methods=['POST'])
@login_required
def dismiss_newsletter():
    """
    Dismiss newsletter popup (v4.0.0)
    """
    try:
        current_user.newsletter_popup_shown = True
        db.session.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error dismissing newsletter popup: {e}")
        return jsonify({'success': False}), 500


@app.route('/subscribe_push', methods=['POST'])
@csrf.exempt  # CSRF exempt for JSON API with CORS
def subscribe_push():
    """
    Web Push subscription endpoint (v4.0.0)
    """
    try:
        data = request.get_json()
        endpoint = data.get('endpoint', '')
        keys = data.get('keys', {})
        p256dh = keys.get('p256dh', '')
        auth = keys.get('auth', '')
        
        if not all([endpoint, p256dh, auth]):
            return jsonify({'success': False, 'message': 'Missing subscription data'}), 400
        
        # Validate lengths to prevent database issues
        if len(endpoint) > 500:
            return jsonify({'success': False, 'message': 'Endpoint URL too long'}), 400
        if len(p256dh) > 500:
            return jsonify({'success': False, 'message': 'p256dh key too long'}), 400
        if len(auth) > 500:
            return jsonify({'success': False, 'message': 'Auth key too long'}), 400
        
        # Check if subscription already exists
        existing = PushSubscription.query.filter_by(endpoint=endpoint).first()
        if existing:
            return jsonify({'success': True, 'message': 'Already subscribed'}), 200
        
        # Create new subscription
        user_id = current_user.id if current_user.is_authenticated else None
        subscription = PushSubscription(
            user_id=user_id,
            endpoint=endpoint,
            p256dh_key=p256dh,
            auth_key=auth
        )
        db.session.add(subscription)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Push notifications enabled'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error subscribing to push: {e}")
        return jsonify({'success': False, 'message': 'Subscription failed'}), 500


# ========================================
# ADMIN DASHBOARD ROUTES
# ========================================

@app.route('/dashboard')
@login_required
def dashboard():
    """
    Admin dashboard - view all tickets with filtering
    Protected route requiring authentication
    """
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    # Get filter parameters from query string
    status_filter = request.args.get('status', 'all')
    priority_filter = request.args.get('priority', 'all')
    issue_type_filter = request.args.get('issue_type', 'all')
    
    # Build query with filters
    query = Ticket.query
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    if priority_filter != 'all':
        query = query.filter_by(priority=priority_filter)
    
    if issue_type_filter != 'all':
        query = query.filter_by(issue_type=issue_type_filter)
    
    # Get filtered tickets
    tickets = query.order_by(Ticket.created_at.desc()).all()
    
    # Calculate statistics (from all tickets, not filtered)
    all_tickets = Ticket.query.all()
    open_count = sum(1 for t in all_tickets if t.status == 'Open')
    resolved_count = sum(1 for t in all_tickets if t.status == 'Resolved')
    total_count = len(all_tickets)
    
    # Calculate priority statistics
    urgent_count = sum(1 for t in all_tickets if t.priority == 'Urgent')
    high_count = sum(1 for t in all_tickets if t.priority == 'High')
    
    # Check email configuration status
    email_configured = bool(SENDER_EMAIL and EMAIL_PASSWORD)
    
    return render_template('dashboard.html', 
                         tickets=tickets,
                         open_count=open_count,
                         resolved_count=resolved_count,
                         total_count=total_count,
                         urgent_count=urgent_count,
                         high_count=high_count,
                         status_filter=status_filter,
                         priority_filter=priority_filter,
                         issue_type_filter=issue_type_filter,
                         allowed_issue_types=ALLOWED_ISSUE_TYPES,
                         ticket_priorities=TICKET_PRIORITIES,
                         is_image_file=is_image_file,
                         email_configured=email_configured)


@app.route('/reply_ticket/<int:ticket_id>', methods=['POST'])
@login_required
def reply_ticket(ticket_id):
    """
    Reply to a ticket and mark it as resolved
    Admin only route
    """
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    # Get the ticket
    ticket = db.session.get(Ticket, ticket_id)
    if not ticket:
        flash('Ticket not found.', 'error')
        return redirect(url_for('dashboard'))
    
    # Get admin reply from form
    admin_reply = request.form.get('admin_reply', '').strip()
    
    if not admin_reply:
        flash('Reply message cannot be empty.', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        # Update ticket with reply and status
        ticket.admin_reply = admin_reply
        ticket.status = 'Resolved'
        ticket.updated_at = datetime.now(timezone.utc)
        
        db.session.commit()
        
        # Send email to user with admin reply
        email_sent, error_message = send_admin_reply_email(
            ticket.email,
            ticket.name,
            ticket.ticket_id,
            ticket.message,
            admin_reply
        )
        
        if email_sent:
            flash(f'Reply sent successfully to {ticket.email}. Ticket {ticket.ticket_id} marked as Resolved.', 'success')
        else:
            # Provide detailed error message to admin
            if error_message:
                flash(f'Reply saved and ticket marked as Resolved, but email notification failed: {error_message}', 'warning')
            else:
                flash(f'Reply saved and ticket marked as Resolved, but email notification failed.', 'warning')
        
    except Exception as e:
        db.session.rollback()
        print(f"Error replying to ticket: {e}")
        flash('An error occurred while sending the reply. Please try again.', 'error')
    
    return redirect(url_for('dashboard'))


@app.route('/export_tickets')
@login_required
def export_tickets():
    """
    Export all tickets to CSV format
    Admin only route
    """
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    # Get all tickets
    tickets = Ticket.query.order_by(Ticket.created_at.desc()).all()
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Ticket ID', 'Name', 'Email', 'Issue Type', 'Priority', 
        'Status', 'Message', 'Admin Reply', 'Attachment', 
        'Created At', 'Updated At'
    ])
    
    # Write ticket data
    for ticket in tickets:
        writer.writerow([
            ticket.ticket_id,
            ticket.name,
            ticket.email,
            ticket.issue_type,
            ticket.priority,
            ticket.status,
            ticket.message,
            ticket.admin_reply or '',
            ticket.attachment_filename or '',
            ticket.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            ticket.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    # Create response
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename=tickets_{datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")}.csv'
        }
    )


@app.route('/bulk_resolve', methods=['POST'])
@login_required
def bulk_resolve():
    """
    Mark multiple tickets as resolved
    Admin only route
    """
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    # Get selected ticket IDs from form
    ticket_ids = request.form.getlist('ticket_ids[]')
    
    if not ticket_ids:
        flash('No tickets selected.', 'warning')
        return redirect(url_for('dashboard'))
    
    # Validate ticket IDs are integers
    valid_ticket_ids = []
    for ticket_id in ticket_ids:
        try:
            valid_ticket_ids.append(int(ticket_id))
        except (ValueError, TypeError):
            # Skip invalid ticket IDs
            continue
    
    if not valid_ticket_ids:
        flash('No valid tickets selected.', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        # Update all selected tickets
        count = 0
        for ticket_id in valid_ticket_ids:
            ticket = db.session.get(Ticket, ticket_id)
            if ticket and ticket.status == 'Open':
                ticket.status = 'Resolved'
                ticket.updated_at = datetime.now(timezone.utc)
                count += 1
        
        db.session.commit()
        flash(f'Successfully resolved {count} ticket(s).', 'success')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in bulk resolve: {e}")
        flash('An error occurred while resolving tickets.', 'error')
    
    return redirect(url_for('dashboard'))


@app.route('/clear_attachments', methods=['POST'])
@login_required
def clear_attachments():
    """
    Clear unused/orphaned attachment files from the uploads directory
    Admin only route
    This removes files that are no longer referenced by any tickets
    """
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    try:
        # Get all attachment filenames from database (efficient query)
        db_filenames = set()
        attachment_results = db.session.query(Ticket.attachment_filename).filter(
            Ticket.attachment_filename.isnot(None)
        ).all()
        for result in attachment_results:
            db_filenames.add(result[0])
        
        # Get all files in uploads directory
        uploads_dir = app.config['UPLOAD_FOLDER']
        if not os.path.exists(uploads_dir):
            flash('Uploads directory does not exist.', 'warning')
            return redirect(url_for('dashboard'))
        
        files_in_directory = set(os.listdir(uploads_dir))
        
        # Find orphaned files (files not referenced in database)
        orphaned_files = files_in_directory - db_filenames
        
        if not orphaned_files:
            flash('No unused attachments found. All files are in use.', 'info')
            return redirect(url_for('dashboard'))
        
        # Delete orphaned files
        deleted_count = 0
        for filename in orphaned_files:
            file_path = os.path.join(uploads_dir, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    deleted_count += 1
            except Exception as e:
                logger.error(f"Error deleting file {filename}: {e}")
        
        if deleted_count > 0:
            flash(f'Successfully deleted {deleted_count} unused attachment(s).', 'success')
        else:
            flash('No files were deleted.', 'info')
            
    except Exception as e:
        logger.error(f"Error clearing attachments: {e}")
        flash('An error occurred while clearing attachments.', 'error')
    
    return redirect(url_for('dashboard'))


@app.route('/delete_ticket/<int:ticket_id>', methods=['POST'])
@login_required
def delete_ticket(ticket_id):
    """
    Delete a specific ticket and its associated attachment
    Admin only route
    """
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    try:
        # Get the ticket
        ticket = db.session.get(Ticket, ticket_id)
        if not ticket:
            flash('Ticket not found.', 'error')
            return redirect(url_for('dashboard'))
        
        # Delete associated attachment file if exists
        if ticket.attachment_filename:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], ticket.attachment_filename)
            if os.path.isfile(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    logger.error(f"Error deleting attachment file: {e}")
        
        # Delete ticket from database
        ticket_id_str = ticket.ticket_id
        db.session.delete(ticket)
        db.session.commit()
        
        flash(f'Ticket {ticket_id_str} and its attachment have been deleted successfully.', 'success')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting ticket: {e}")
        flash('An error occurred while deleting the ticket.', 'error')
    
    return redirect(url_for('dashboard'))


@app.route('/admin/broadcast', methods=['GET', 'POST'])
@login_required
def admin_broadcast():
    """
    Admin broadcast news route (v4.0.0)
    CPU-optimized batch processing for notifications
    """
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        
        if not all([title, content]):
            flash('Title and content are required.', 'error')
            return redirect(url_for('admin_broadcast'))
        
        # Validate lengths
        if len(title) > 200:
            flash('Title must be 200 characters or less.', 'error')
            return redirect(url_for('admin_broadcast'))
        
        if len(content) > 10000:
            flash('Content must be 10,000 characters or less.', 'error')
            return redirect(url_for('admin_broadcast'))
        
        try:
            # Create news item
            news = News(
                title=title,
                content=content,
                author_id=current_user.id
            )
            db.session.add(news)
            db.session.commit()
            
            # Get all newsletter subscribers (CPU-optimized query)
            subscribers = db.session.query(NewsletterSubscription.email).all()
            subscriber_emails = [s[0] for s in subscribers]
            
            # Send notifications in batches (CPU-safe)
            if subscriber_emails:
                results = batch_process_users(
                    subscriber_emails,
                    send_news_email,
                    title,
                    content
                )
                
                flash(f'News broadcast created! Notifications sent: {results["success"]} success, {results["failed"]} failed.', 'success')
            else:
                flash('News broadcast created! No subscribers to notify yet.', 'info')
            
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error broadcasting news: {e}")
            flash('An error occurred while broadcasting news.', 'error')
            return redirect(url_for('admin_broadcast'))
    
    # Get recent news
    recent_news = News.query.order_by(News.published_at.desc()).limit(10).all()
    subscriber_count = NewsletterSubscription.query.count()
    push_subscriber_count = PushSubscription.query.count()
    
    return render_template('admin/broadcast.html',
                         recent_news=recent_news,
                         subscriber_count=subscriber_count,
                         push_subscriber_count=push_subscriber_count)


def send_news_email(user_email, title, content):
    """
    Send news broadcast email (CPU-optimized)
    Returns True if successful, False otherwise
    """
    if not SENDER_EMAIL or not EMAIL_PASSWORD:
        return False
    
    safe_email = escape(user_email)
    safe_title = escape(title)
    safe_content = escape(content)
    
    try:
        msg = MIMEMultipart()
        msg['Subject'] = f"ZetsuServ News: {safe_title}"
        msg['From'] = SENDER_EMAIL
        msg['To'] = user_email
        
        body = f"""
        <html>
        <body style="font-family: 'Segoe UI', Arial, sans-serif; color: #201F1E; background-color: #FAF9F8; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 8px; padding: 32px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <h2 style="color: #0078D4; margin-bottom: 24px;">{safe_title}</h2>
                <p style="color: #323130; line-height: 1.6; white-space: pre-wrap;">{safe_content}</p>
                
                <hr style="border: none; border-top: 1px solid #E1DFDD; margin: 24px 0;">
                <p style="font-size: 12px; color: #A19F9D; text-align: center;">Powered by ZetsuServ Support Portal v4.0.0</p>
            </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, EMAIL_PASSWORD)
            server.sendmail(SENDER_EMAIL, user_email, msg.as_string())
        
        return True
    except Exception as e:
        logger.error(f"Error sending news email to {user_email}: {e}")
        return False


# Run the application
if __name__ == '__main__':
    # Debug mode is enabled for development only
    # IMPORTANT: Set debug=False for production deployment on PythonAnywhere
    # PythonAnywhere will use WSGI, so this block won't execute in production
    app.run(debug=True, host='0.0.0.0', port=5000)
