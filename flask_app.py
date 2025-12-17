"""
ZetsuServ Support Portal - Flask Application
A professional support portal with Glassmorphism design
Designed for deployment on PythonAnywhere
"""

import os
import smtplib
import sqlite3
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template, request, redirect, url_for, g

# Initialize Flask application
app = Flask(__name__)

# Configure Flask app
# IMPORTANT: Change SECRET_KEY to a secure random value in production
# Generate with: python -c "import secrets; print(secrets.token_hex(32))"
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'

# Database configuration
DATABASE = 'tickets.db'


def get_db():
    """Get database connection for current request context."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    """Close database connection when request ends."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db():
    """Initialize the database with tickets table."""
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                issue_type TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        db.commit()


def send_email(user_email, user_name, user_message, issue_type):
    """
    Send email notifications using SMTP.
    Sends notification to admin and confirmation to user.
    
    Required environment variables:
    - ZETSUSERV_EMAIL: The sender email address
    - ZETSUSERV_PASSWORD: The app password for SMTP authentication
    """
    sender_email = os.environ.get('ZETSUSERV_EMAIL')
    password = os.environ.get('ZETSUSERV_PASSWORD')
    
    if not sender_email or not password:
        print("Email configuration missing: ZETSUSERV_EMAIL or ZETSUSERV_PASSWORD not set")
        return False

    # Email to Admin (Notification)
    msg_admin = MIMEMultipart()
    msg_admin['Subject'] = f"New Ticket: {issue_type} from {user_name}"
    msg_admin['From'] = sender_email
    msg_admin['To'] = sender_email

    admin_body = f"""
    <html>
    <body style="font-family: 'Segoe UI', Arial, sans-serif; background: linear-gradient(135deg, #1a1a2e, #16213e); color: #fff; padding: 30px;">
        <div style="max-width: 600px; margin: 0 auto; background: rgba(255,255,255,0.1); border-radius: 20px; padding: 30px; backdrop-filter: blur(10px);">
            <h2 style="color: #00d9ff; margin-bottom: 20px;">🎫 New Support Request</h2>
            <p><strong style="color: #a855f7;">Name:</strong> {user_name}</p>
            <p><strong style="color: #a855f7;">Email:</strong> {user_email}</p>
            <p><strong style="color: #a855f7;">Issue Type:</strong> {issue_type}</p>
            <p><strong style="color: #a855f7;">Message:</strong></p>
            <div style="background: rgba(0,0,0,0.3); padding: 15px; border-radius: 10px; margin-top: 10px;">
                {user_message}
            </div>
            <hr style="border: 1px solid rgba(255,255,255,0.1); margin: 20px 0;">
            <p style="font-size: 12px; color: #888;">Powered by ZetsuServ AI</p>
        </div>
    </body>
    </html>
    """
    msg_admin.attach(MIMEText(admin_body, 'html'))

    # Email to User (Confirmation)
    msg_user = MIMEMultipart()
    msg_user['Subject'] = f"✅ Ticket Received - {issue_type}"
    msg_user['From'] = sender_email
    msg_user['To'] = user_email

    user_body = f"""
    <html>
    <body style="font-family: 'Segoe UI', Arial, sans-serif; background: linear-gradient(135deg, #1a1a2e, #16213e); color: #fff; padding: 30px;">
        <div style="max-width: 600px; margin: 0 auto; background: rgba(255,255,255,0.1); border-radius: 20px; padding: 30px; backdrop-filter: blur(10px);">
            <h2 style="color: #00d9ff; margin-bottom: 20px;">✨ Thank You, {user_name}!</h2>
            <p>We've received your support request and our team is on it!</p>
            <div style="background: rgba(168,85,247,0.2); padding: 15px; border-radius: 10px; margin: 20px 0; border-left: 4px solid #a855f7;">
                <p><strong>Issue Type:</strong> {issue_type}</p>
                <p><strong>Your Message:</strong></p>
                <p style="color: #ccc;">{user_message}</p>
            </div>
            <p>We'll get back to you as soon as possible at <strong style="color: #00d9ff;">{user_email}</strong></p>
            <hr style="border: 1px solid rgba(255,255,255,0.1); margin: 20px 0;">
            <p style="font-size: 12px; color: #888;">Powered by ZetsuServ AI</p>
        </div>
    </body>
    </html>
    """
    msg_user.attach(MIMEText(user_body, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        # Send to admin
        server.sendmail(sender_email, sender_email, msg_admin.as_string())
        # Send confirmation to user
        server.sendmail(sender_email, user_email, msg_user.as_string())
        server.quit()
        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP Authentication failed: {e}")
        return False
    except smtplib.SMTPConnectError as e:
        print(f"SMTP Connection failed: {e}")
        return False
    except smtplib.SMTPException as e:
        print(f"SMTP error occurred: {e}")
        return False
    except OSError as e:
        print(f"Network error sending email: {e}")
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
    return render_template('support.html')


@app.route('/submit', methods=['POST'])
def submit():
    """
    Form submission handler
    Accepts POST requests from the support form
    Saves to database and sends email notifications
    Returns success message
    """
    # Extract form data with validation
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    issue_type = request.form.get('issue_type', '').strip()
    message = request.form.get('message', '').strip()

    # Basic server-side validation
    if not all([name, email, issue_type, message]):
        return render_template('support.html',
                               success_message="Error: All fields are required. Please fill out the form completely.")

    # Save to database
    db_saved = False
    try:
        db = get_db()
        db.execute(
            'INSERT INTO tickets (name, email, issue_type, message) VALUES (?, ?, ?, ?)',
            (name, email, issue_type, message)
        )
        db.commit()
        db_saved = True
    except sqlite3.Error as e:
        print(f"Database error: {e}")

    # Print to console for debugging
    print("=" * 50)
    print("NEW SUPPORT TICKET RECEIVED")
    print("=" * 50)
    print(f"Name: {name}")
    print(f"Email: {email}")
    print(f"Issue Type: {issue_type}")
    print(f"Message: {message}")
    print("=" * 50)

    # Handle database failure
    if not db_saved:
        return render_template('support.html',
                               success_message="Error: Unable to save your ticket. Please try again later.")

    # Send email notifications
    email_sent = send_email(email, name, message, issue_type)

    # Return success message (Jinja2 auto-escapes to prevent XSS)
    if email_sent:
        success_message = f"Thank you, {name}! Your ticket has been submitted successfully. A confirmation email has been sent to {email}."
    else:
        success_message = f"Thank you, {name}! Your ticket has been submitted successfully. We'll contact you at {email} shortly."

    # Render support page with success message
    return render_template('support.html', success_message=success_message)


# Initialize database on startup
init_db()

# Run the application
if __name__ == '__main__':
    # Debug mode is enabled for development only
    # IMPORTANT: Set debug=False for production deployment on PythonAnywhere
    # PythonAnywhere will use WSGI, so this block won't execute in production
    app.run(debug=True)
