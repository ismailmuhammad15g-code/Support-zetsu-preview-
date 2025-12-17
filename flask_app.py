"""
ZetsuServ Support Portal - Flask Application
A professional support portal with Microsoft Fluent Design styling
Designed for deployment on PythonAnywhere
"""

from flask import Flask, render_template, request, redirect, url_for

# Initialize Flask application
app = Flask(__name__)

# Configure Flask app for production
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
    # Extract form data
    name = request.form.get('name')
    email = request.form.get('email')
    issue_type = request.form.get('issue_type')
    message = request.form.get('message')
    
    # Print to console for debugging (since no database yet)
    print("=" * 50)
    print("NEW SUPPORT TICKET RECEIVED")
    print("=" * 50)
    print(f"Name: {name}")
    print(f"Email: {email}")
    print(f"Issue Type: {issue_type}")
    print(f"Message: {message}")
    print("=" * 50)
    
    # Return success message (will be displayed on the page)
    success_message = f"Thank you, {name}! Your ticket has been submitted successfully. We'll contact you at {email} shortly."
    
    # Render support page with success message
    return render_template('support.html', success_message=success_message)


# Run the application
if __name__ == '__main__':
    # Debug mode for development - set to False in production
    app.run(debug=True)
