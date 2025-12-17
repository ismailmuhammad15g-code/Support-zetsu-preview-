"""
ZetsuServ Support Portal - Flask Application
A professional support portal with Microsoft Fluent Design
Designed for deployment on PythonAnywhere
Features: Ticket Management, Database Storage, File Uploads, Admin Dashboard
"""

import os
import re
import smtplib
import secrets
from datetime import datetime, timezone
from html import escape
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# Initialize Flask application
app = Flask(__name__)

# Configure Flask app
# IMPORTANT: Set SECRET_KEY via environment variable in production
# Generate with: python -c "import secrets; print(secrets.token_hex(32))"
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-only-insecure-key-change-in-production')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///support_tickets.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# File upload configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}
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


# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))


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
        print("Email credentials not configured. Skipping email send.")
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
        print(f"Error sending email: {e}")
        return False


def send_admin_reply_email(user_email, user_name, ticket_id, original_message, admin_reply):
    """
    Send email to user with admin's reply
    Returns True if successful, False otherwise
    """
    # Check if email credentials are configured
    if not SENDER_EMAIL or not EMAIL_PASSWORD:
        print("Email credentials not configured. Skipping email send.")
        return False
    
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
            return True
        finally:
            server.quit()
    except Exception as e:
        print(f"Error sending admin reply email: {e}")
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
        print("=" * 50)
        print("NEW SUPPORT TICKET RECEIVED")
        print("=" * 50)
        print(f"Ticket ID: {ticket_id}")
        print(f"Name: {name}")
        print(f"Email: {email}")
        print(f"Issue Type: {issue_type}")
        print(f"Priority: {priority}")
        print(f"Message: {message}")
        print(f"Attachment: {attachment_filename}")
        print("=" * 50)
        
        # Send email notifications
        email_sent = send_email(email, name, message, issue_type, ticket_id, priority)
        
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
            print(f"Error creating user: {e}")
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
    Admin dashboard - view all tickets
    Protected route requiring authentication
    """
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    # Get all tickets ordered by created_at descending
    tickets = Ticket.query.order_by(Ticket.created_at.desc()).all()
    
    # Calculate statistics
    open_count = sum(1 for t in tickets if t.status == 'Open')
    resolved_count = sum(1 for t in tickets if t.status == 'Resolved')
    total_count = len(tickets)
    
    return render_template('dashboard.html', 
                         tickets=tickets,
                         open_count=open_count,
                         resolved_count=resolved_count,
                         total_count=total_count)


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
    ticket = Ticket.query.get_or_404(ticket_id)
    
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
        email_sent = send_admin_reply_email(
            ticket.email,
            ticket.name,
            ticket.ticket_id,
            ticket.message,
            admin_reply
        )
        
        if email_sent:
            flash(f'Reply sent successfully to {ticket.email}. Ticket {ticket.ticket_id} marked as Resolved.', 'success')
        else:
            flash(f'Reply saved and ticket marked as Resolved, but email notification failed.', 'warning')
        
    except Exception as e:
        db.session.rollback()
        print(f"Error replying to ticket: {e}")
        flash('An error occurred while sending the reply. Please try again.', 'error')
    
    return redirect(url_for('dashboard'))


# Run the application
if __name__ == '__main__':
    # Debug mode is enabled for development only
    # IMPORTANT: Set debug=False for production deployment on PythonAnywhere
    # PythonAnywhere will use WSGI, so this block won't execute in production
    app.run(debug=True, host='0.0.0.0', port=5000)
