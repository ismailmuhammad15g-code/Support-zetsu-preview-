"""
ZetsuServ Support Portal - Flask Application
A professional support portal with Glassmorphism Design
Designed for deployment on PythonAnywhere
"""

import os
import re
import smtplib
from html import escape
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template, request, redirect, url_for

# Initialize Flask application
app = Flask(__name__)

# Configure Flask app
# IMPORTANT: Set SECRET_KEY via environment variable in production
# Generate with: python -c "import secrets; print(secrets.token_hex(32))"
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-only-insecure-key-change-in-production')

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
}


def validate_email(email):
    """
    Validate email format using regex
    Returns True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def send_email(user_email, user_name, user_message, issue_type):
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
    
    try:
        # Email to Admin (Notification)
        msg_admin = MIMEMultipart()
        msg_admin['Subject'] = f"New Ticket: {safe_type} from {safe_name}"
        msg_admin['From'] = SENDER_EMAIL
        msg_admin['To'] = SENDER_EMAIL
        
        admin_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <h3 style="color: #0078D4;">New Support Request</h3>
            <p><strong>Name:</strong> {safe_name}</p>
            <p><strong>Email:</strong> {safe_email}</p>
            <p><strong>Type:</strong> {safe_type}</p>
            <p><strong>Message:</strong><br>{safe_message}</p>
            <hr>
            <p style="font-size: 12px; color: #666;">Powered by ZetsuServ AI</p>
        </body>
        </html>
        """
        msg_admin.attach(MIMEText(admin_body, 'html'))
        
        # Email to User (Confirmation)
        msg_user = MIMEMultipart()
        msg_user['Subject'] = "Your Support Ticket Has Been Received"
        msg_user['From'] = SENDER_EMAIL
        msg_user['To'] = user_email
        
        user_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <h3 style="color: #0078D4;">Thank You for Contacting ZetsuServ Support</h3>
            <p>Dear {safe_name},</p>
            <p>We have received your support ticket and our team will get back to you shortly.</p>
            <h4>Your Request Details:</h4>
            <p><strong>Issue Type:</strong> {safe_type}</p>
            <p><strong>Message:</strong><br>{safe_message}</p>
            <hr>
            <p style="font-size: 12px; color: #666;">Powered by ZetsuServ AI</p>
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
    # Get success or error messages from query parameters
    success_message = request.args.get('success_message')
    error_message = request.args.get('error_message')
    return render_template('support.html', 
                         success_message=success_message,
                         error_message=error_message)


@app.route('/submit', methods=['POST'])
def submit():
    """
    Form submission handler
    Accepts POST requests from the support form
    Validates data, sends emails, and redirects with message
    Returns redirect to support page (POST-Redirect-GET pattern)
    """
    # Extract form data with validation
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    issue_type = request.form.get('issue_type', '').strip()
    message = request.form.get('message', '').strip()
    
    # Basic server-side validation - check all fields present
    if not all([name, email, issue_type, message]):
        return redirect(url_for('support', 
                               error_message="Error: All fields are required. Please fill out the form completely."))
    
    # Validate field lengths
    if len(name) > 100:
        return redirect(url_for('support',
                               error_message="Error: Name must be less than 100 characters."))
    
    if len(email) > 254:
        return redirect(url_for('support',
                               error_message="Error: Email must be less than 254 characters."))
    
    if len(message) > 2000:
        return redirect(url_for('support',
                               error_message="Error: Message must be less than 2000 characters."))
    
    # Validate email format
    if not validate_email(email):
        return redirect(url_for('support',
                               error_message="Error: Please enter a valid email address."))
    
    # Validate that issue_type is one of the allowed values
    if issue_type not in ALLOWED_ISSUE_TYPES:
        return redirect(url_for('support',
                               error_message="Error: Invalid issue type selected. Please choose a valid option and resubmit the form."))
    
    # Print to console for debugging
    print("=" * 50)
    print("NEW SUPPORT TICKET RECEIVED")
    print("=" * 50)
    print(f"Name: {name}")
    print(f"Email: {email}")
    print(f"Issue Type: {issue_type}")
    print(f"Message: {message}")
    print("=" * 50)
    
    # Send email notifications
    email_sent = send_email(email, name, message, issue_type)
    
    if email_sent:
        success_msg = f"Thank you, {name}! Your ticket has been submitted successfully. We've sent a confirmation to {email}."
    else:
        success_msg = f"Thank you, {name}! Your ticket has been submitted successfully. However, we couldn't send the confirmation email. We'll contact you at {email} shortly."
    
    # Redirect to support page with success message (POST-Redirect-GET pattern)
    return redirect(url_for('support', success_message=success_msg))


# Run the application
if __name__ == '__main__':
    # Debug mode is enabled for development only
    # IMPORTANT: Set debug=False for production deployment on PythonAnywhere
    # PythonAnywhere will use WSGI, so this block won't execute in production
    app.run(debug=True)
