"""
ZetsuServ Support Portal - Flask Application
A professional support portal with Microsoft Fluent Design
Designed for deployment on PythonAnywhere
Features: Ticket Management, Database Storage, File Uploads, Admin Dashboard
"""

import os
import re
import csv
import io
import smtplib
import secrets
import requests
import logging
import google.generativeai as genai
from datetime import datetime, timezone
from html import escape
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template, request, redirect, url_for, flash, session, Response, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# Try to import PIL for image processing (optional dependency for vision features)
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logger_warning_shown = False  # Will show warning when needed

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

# Gemini AI Configuration
# IMPORTANT: Default API key is for DEMO/TESTING ONLY
# For production, set your own API key via environment variable:
# export GEMINI_API_KEY=your-api-key-here
# Get a free API key at: https://makersuite.google.com/app/apikey
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyBYpMnBd1UMuPDvskn9-ss3LpWkUBdWmR0')
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception as e:
        logger.warning(f"Failed to configure Gemini API: {e}")

# Gemini AI generation configuration
GEMINI_GENERATION_CONFIG = {
    'temperature': 0.7,
    'top_p': 0.9,
    'top_k': 40,
    'max_output_tokens': 500,
}

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

# ========================================
# DATABASE MODELS
# ========================================

class User(UserMixin, db.Model):
    """Database model for admin users"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    is_available = db.Column(db.Boolean, nullable=False, default=True)
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
    status = db.Column(db.String(20), nullable=False, default='pending_review')
    attachment_filename = db.Column(db.String(255), nullable=True)
    admin_reply = db.Column(db.Text, nullable=True)
    ai_responded = db.Column(db.Boolean, nullable=False, default=False)
    ai_suggestion = db.Column(db.Text, nullable=True)
    ai_draft = db.Column(db.Text, nullable=True)
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
            'ai_responded': self.ai_responded,
            'ai_suggestion': self.ai_suggestion,
            'ai_draft': self.ai_draft,
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
        logger.warning(error_msg)
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
        logger.error(error_msg)
        return False, error_msg
    except smtplib.SMTPException as e:
        error_msg = f"SMTP error occurred: {str(e)}"
        logger.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Error sending admin reply email: {str(e)}"
        logger.error(error_msg)
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
        logger.info("N8N_WEBHOOK_URL not configured. Skipping webhook send.")
        return False
    
    # Validate webhook URL to prevent SSRF attacks
    try:
        from urllib.parse import urlparse
        parsed_url = urlparse(N8N_WEBHOOK_URL)
        
        # Only allow HTTPS URLs for security
        if parsed_url.scheme not in ['https', 'http']:
            logger.warning(f"Invalid webhook URL scheme: {parsed_url.scheme}. Only HTTP/HTTPS allowed.")
            return False
        
        # Block localhost and private IP ranges to prevent SSRF
        if parsed_url.hostname in ['localhost', '127.0.0.1', '0.0.0.0']:
            logger.warning("Webhook URL cannot point to localhost (SSRF protection)")
            return False
            
        # Check for private IP ranges (basic check)
        if parsed_url.hostname and (
            parsed_url.hostname.startswith('10.') or
            parsed_url.hostname.startswith('192.168.') or
            parsed_url.hostname.startswith('172.16.')
        ):
            logger.warning("Webhook URL cannot point to private IP ranges (SSRF protection)")
            return False
            
    except Exception as e:
        logger.error(f"Error validating webhook URL: {e}")
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
            logger.info(f"Successfully sent ticket {ticket_data.get('ticket_id')} to webhook")
            return True
        else:
            logger.warning(f"Webhook returned status code {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        logger.warning("Webhook request timed out")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending to webhook: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in webhook send: {e}")
        return False


def get_faq_context():
    """
    Retrieve FAQ data to build context for AI responses
    Returns formatted FAQ context string
    """
    try:
        faqs = FAQ.query.all()
        if not faqs:
            return "No FAQ data available."
        
        faq_context = "Here are the frequently asked questions and answers for reference:\n\n"
        for faq in faqs:
            faq_context += f"Q: {faq.question}\nA: {faq.answer}\n\n"
        
        return faq_context
    except Exception as e:
        logger.error(f"Error retrieving FAQ context: {e}")
        return "FAQ data unavailable."


def detect_sentiment(message):
    """
    Detect if message contains urgent/angry keywords
    Returns tuple (is_urgent: bool, detected_keywords: list)
    """
    urgent_keywords = [
        'angry', 'urgent', 'critical', 'emergency', 'asap', 'immediately',
        'frustrated', 'furious', 'unacceptable', 'terrible', 'horrible',
        'worst', 'disappointed', 'outraged', 'serious', 'severe'
    ]
    
    message_lower = message.lower()
    detected = [keyword for keyword in urgent_keywords if keyword in message_lower]
    
    return len(detected) > 0, detected


def generate_ai_response(ticket_message, issue_type, user_name, attachment_filename=None):
    """
    Generate AI response using Gemini API with multimodal vision support
    
    Args:
        ticket_message: User's support ticket message
        issue_type: Type of issue submitted
        user_name: Name of the user
        attachment_filename: Optional filename of attached image for vision analysis
                           (must be already sanitized with secure_filename)
    
    Returns:
        AI-generated response string or None if failed
    """
    if not GEMINI_API_KEY:
        logger.warning("Gemini API key not configured")
        return None
    
    try:
        # Get FAQ context
        faq_context = get_faq_context()
        
        # Build system prompt
        system_prompt = f"""You are a professional customer support AI assistant for ZetsuServ Support Portal.

Your role:
- Provide helpful, empathetic, and professional responses to customer inquiries
- Use the FAQ knowledge base to answer common questions accurately
- Keep responses concise but comprehensive (2-4 paragraphs)
- Be friendly and reassuring
- If you don't know something, acknowledge it and suggest contacting human support
- If an image is provided, analyze it to understand the user's technical problem or error screenshot

FAQ Knowledge Base:
{faq_context}

Guidelines:
- Address the customer by name
- Acknowledge their issue with empathy
- Provide clear, actionable solutions when possible
- End with an offer for further assistance
- Use professional but friendly tone
"""
        
        # Build user prompt
        user_prompt = f"""Customer Name: {user_name}
Issue Type: {issue_type}
Customer Message: {ticket_message}

Please provide a helpful support response."""
        
        # Initialize Gemini model (same model for both text and vision)
        # Updated to use gemini-1.5-flash (faster and currently supported)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Helper function to generate text-only response
        def generate_text_response():
            return model.generate_content(
                f"{system_prompt}\n\n{user_prompt}",
                generation_config=GEMINI_GENERATION_CONFIG
            )
        
        # Check if we have an image attachment for vision analysis
        has_image = attachment_filename and is_image_file(attachment_filename)
        
        # Generate response with or without image
        if has_image and PIL_AVAILABLE:
            # Additional security: ensure filename doesn't contain path separators
            # (should already be sanitized by secure_filename, but double-check)
            if '..' in attachment_filename or '/' in attachment_filename or '\\' in attachment_filename:
                logger.warning(f"Invalid attachment filename detected: {attachment_filename}")
                response = generate_text_response()
            else:
                # Construct secure file path
                image_path = os.path.join(UPLOAD_FOLDER, attachment_filename)
                
                # Verify path is within UPLOAD_FOLDER (additional security check)
                if not os.path.abspath(image_path).startswith(os.path.abspath(UPLOAD_FOLDER)):
                    logger.warning(f"Path traversal attempt detected: {attachment_filename}")
                    response = generate_text_response()
                elif os.path.exists(image_path):
                    try:
                        # Load and verify image file
                        img = Image.open(image_path)
                        
                        # Verify it's a valid image (prevents malicious files)
                        img.verify()
                        
                        # Reopen after verify (verify closes the file)
                        img = Image.open(image_path)
                        
                        # Optional: Check image dimensions for reasonable size
                        if img.width > 10000 or img.height > 10000:
                            logger.warning(f"Image dimensions too large: {img.width}x{img.height}")
                            response = generate_text_response()
                        else:
                            # Add instruction for image analysis
                            vision_prompt = f"{system_prompt}\n\n{user_prompt}\n\nIMPORTANT: Read the attached image to understand the user's technical problem or error screenshot, then provide a solution based on both the image and the text."
                            
                            # Generate response with image
                            response = model.generate_content(
                                [vision_prompt, img],
                                generation_config=GEMINI_GENERATION_CONFIG
                            )
                            
                            logger.info(f"AI response generated with image analysis for {attachment_filename}")
                    except Exception as img_error:
                        logger.error(f"Error processing image for AI: {img_error}")
                        # Fall back to text-only if image processing fails
                        response = generate_text_response()
                else:
                    # Image file not found, use text only
                    logger.warning(f"Image file not found: {image_path}")
                    response = generate_text_response()
        elif has_image and not PIL_AVAILABLE:
            # PIL not available, log warning and fall back to text-only
            logger.warning("PIL/Pillow not installed. Image analysis unavailable. Falling back to text-only response.")
            response = generate_text_response()
        else:
            # No image - use text-only
            response = generate_text_response()
        
        if response and response.text:
            return response.text.strip()
        else:
            logger.warning("Gemini API returned empty response")
            return None
            
    except Exception as e:
        # Enhanced error handling with specific messages for different error types
        error_msg = str(e).lower()
        # Check for specific error patterns to provide helpful debugging information
        if '404' in error_msg or ('not found' in error_msg and 'model' in error_msg) or 'model not found' in error_msg:
            logger.error(f"AI Model not found (404 error). Verify model name 'gemini-1.5-flash' is available: {e}")
        elif 'api key' in error_msg or 'authentication' in error_msg or 'unauthorized' in error_msg:
            logger.error(f"AI API authentication failed. Check GEMINI_API_KEY environment variable: {e}")
        elif 'quota' in error_msg or 'limit' in error_msg or 'exceeded' in error_msg:
            logger.error(f"AI API quota exceeded or rate limited. Try again later: {e}")
        else:
            logger.error(f"Error generating AI response: {e}")
        return None


def generate_ai_suggestion(ticket_message, issue_type, user_name, attachment_filename=None):
    """
    Generate AI suggestion for admin (non-auto-sent)
    This is always generated for admin to see as a draft
    
    Args:
        ticket_message: User's support ticket message
        issue_type: Type of issue submitted
        user_name: Name of the user
        attachment_filename: Optional filename of attached image for vision analysis
    
    Returns:
        AI-generated suggestion string or None if failed
    """
    # Use the same function with image support
    return generate_ai_response(ticket_message, issue_type, user_name, attachment_filename)

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
        logger.error(f"Error serving file: {e}", exc_info=True)
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
    
    # Check sentiment for urgent/angry keywords
    is_urgent_sentiment, detected_keywords = detect_sentiment(message)
    if is_urgent_sentiment:
        priority = 'High'  # Auto-escalate priority
        logger.info(f"Urgent sentiment detected. Keywords: {detected_keywords}. Priority escalated to High.")
    
    try:
        # Generate ticket ID
        ticket_id = generate_ticket_id()
        
        # Create new ticket with pending_review status
        new_ticket = Ticket(
            ticket_id=ticket_id,
            name=name,
            email=email,
            issue_type=issue_type,
            priority=priority,
            message=message,
            attachment_filename=attachment_filename,
            status='pending_review'
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
        
        # Generate AI draft for admin review (background task)
        try:
            ai_draft = generate_ai_response(message, issue_type, name, attachment_filename)
            if ai_draft:
                new_ticket.ai_draft = ai_draft
                # Keep ai_suggestion for backward compatibility
                new_ticket.ai_suggestion = ai_draft
                db.session.commit()
                logger.info(f"AI draft generated for ticket {ticket_id}")
            else:
                logger.warning(f"AI draft generation returned None for ticket {ticket_id}")
        except Exception as e:
            logger.error(f"Error generating AI draft: {e}")
        
        # Send email notifications (confirmation to user, notification to admin)
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
            logger.warning(f"Webhook integration error (non-critical): {webhook_error}")
        
        if email_sent:
            flash(f'Thank you, {name}! Your ticket {ticket_id} has been submitted successfully. We\'ve sent a confirmation to {email}.', 'success')
        else:
            flash(f'Thank you, {name}! Your ticket {ticket_id} has been submitted successfully.', 'success')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error saving ticket: {e}", exc_info=True)
        flash('An error occurred while submitting your ticket. Please try again.', 'error')
    
    # Redirect to support page with success message (POST-Redirect-GET pattern)
    return redirect(url_for('support'))


# ========================================
# AUTHENTICATION ROUTES
# ========================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    User registration route with whitelist validation
    Only zetsuserv@gmail.com can register as admin
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
        
        # Whitelist check - only zetsuserv@gmail.com can register
        # NOTE: This is hardcoded per security requirements to ensure only one specific
        # admin email can register. To add more admins, modify this list or use an
        # environment variable with comma-separated emails if needed in the future.
        ADMIN_WHITELIST = ['zetsuserv@gmail.com']
        if email not in ADMIN_WHITELIST:
            flash('Access Denied: Admin whitelist only.', 'error')
            return redirect(url_for('register'))
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('An account with this email already exists.', 'error')
            return redirect(url_for('register'))
        
        try:
            # Create new admin user
            new_user = User(email=email, is_admin=True)
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating user: {e}", exc_info=True)
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
    open_count = sum(1 for t in all_tickets if t.status in ['Open', 'pending_review'])
    resolved_count = sum(1 for t in all_tickets if t.status in ['Resolved', 'sent'])
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


@app.route('/admin/toggle-status', methods=['POST'])
@login_required
def toggle_admin_status():
    """
    Toggle admin availability status via AJAX
    Returns JSON response (NO REDIRECT to avoid loops)
    Admin only route
    """
    if not current_user.is_admin:
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    
    try:
        # Query the current admin user from database to ensure we have the latest state
        user = db.session.get(User, current_user.id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Toggle the availability status
        user.is_available = not user.is_available
        
        # Explicitly commit the change to database
        db.session.commit()
        
        logger.info(f"Admin availability toggled to: {user.is_available}")
        
        # Return JSON response with success status and current availability
        return jsonify({
            'success': True,
            'is_available': user.is_available,
            'message': f"Status updated to {'Available' if user.is_available else 'Unavailable'}"
        }), 200
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error toggling admin status: {e}")
        return jsonify({'success': False, 'error': 'Failed to update status'}), 500


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
        logger.error(f"Error replying to ticket: {e}", exc_info=True)
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


@app.route('/admin/draft_pulls')
@login_required
def draft_pulls():
    """
    Admin page to view and manage draft responses
    Shows tickets with pending_review status
    """
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    # Get all tickets with pending_review status
    pending_tickets = Ticket.query.filter_by(status='pending_review').order_by(Ticket.created_at.desc()).all()
    
    # Calculate statistics
    total_pending = len(pending_tickets)
    
    return render_template('draft_pulls.html', 
                         tickets=pending_tickets,
                         total_pending=total_pending,
                         is_image_file=is_image_file)


@app.route('/admin/review_and_send/<int:ticket_id>', methods=['POST'])
@login_required
def review_and_send(ticket_id):
    """
    Review and send the AI draft response to user
    Admin only route
    """
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    # Get the ticket
    ticket = db.session.get(Ticket, ticket_id)
    if not ticket:
        flash('Ticket not found.', 'error')
        return redirect(url_for('draft_pulls'))
    
    # Get edited response from form
    final_response = request.form.get('final_response', '').strip()
    
    if not final_response:
        flash('Response message cannot be empty.', 'error')
        return redirect(url_for('draft_pulls'))
    
    try:
        # Update ticket with final response and status
        ticket.admin_reply = final_response
        ticket.status = 'sent'
        ticket.updated_at = datetime.now(timezone.utc)
        
        db.session.commit()
        
        # Send email to user with final response
        email_sent, error_message = send_admin_reply_email(
            ticket.email,
            ticket.name,
            ticket.ticket_id,
            ticket.message,
            final_response
        )
        
        if email_sent:
            flash(f'Response sent successfully to {ticket.email}. Ticket {ticket.ticket_id} marked as Sent.', 'success')
        else:
            # Provide detailed error message to admin
            if error_message:
                flash(f'Response saved and ticket marked as Sent, but email notification failed: {error_message}', 'warning')
            else:
                flash(f'Response saved and ticket marked as Sent, but email notification failed.', 'warning')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error sending response: {e}")
        flash('An error occurred while sending the response. Please try again.', 'error')
    
    return redirect(url_for('draft_pulls'))


# Run the application
if __name__ == '__main__':
    # Debug mode is enabled for development only
    # IMPORTANT: Set debug=False for production deployment on PythonAnywhere
    # PythonAnywhere will use WSGI, so this block won't execute in production
    app.run(debug=True, host='0.0.0.0', port=5000)
