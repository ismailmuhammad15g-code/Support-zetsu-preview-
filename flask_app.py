"""
ZetsuServ Support Portal - Flask Application
A professional support portal with Microsoft Fluent Design styling
Designed for deployment on PythonAnywhere
"""

from flask import Flask, render_template, request, redirect, url_for

# Initialize Flask application
app = Flask(__name__)

# Configure Flask app
# IMPORTANT: Change SECRET_KEY to a secure random value in production
# Generate with: python -c "import secrets; print(secrets.token_hex(32))"
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'


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
    Prints data to console (no database yet)
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
    
    # Print to console for debugging (since no database yet)
    print("=" * 50)
    print("NEW SUPPORT TICKET RECEIVED")
    print("=" * 50)
    print(f"Name: {name}")
    print(f"Email: {email}")
    print(f"Issue Type: {issue_type}")
    print(f"Message: {message}")
    print("=" * 50)
    
    # Return success message (Jinja2 auto-escapes to prevent XSS)
    success_message = f"Thank you, {name}! Your ticket has been submitted successfully. We'll contact you at {email} shortly."
    
    # Render support page with success message
    return render_template('support.html', success_message=success_message)


# Run the application
if __name__ == '__main__':
    # Debug mode is enabled for development only
    # IMPORTANT: Set debug=False for production deployment on PythonAnywhere
    # PythonAnywhere will use WSGI, so this block won't execute in production
    app.run(debug=True)
