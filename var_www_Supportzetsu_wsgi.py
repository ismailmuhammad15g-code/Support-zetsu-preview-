"""
WSGI Configuration for PythonAnywhere Deployment
This file should be placed at: /var/www/Supportzetsu_wsgi.py
"""

import sys
import os

# Add your project directory to the sys.path
project_home = '/home/Supportzetsu/Support-zetsu-preview'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables if needed
# os.environ['SECRET_KEY'] = 'your-secret-key-here'
# os.environ['GEMINI_API_KEY'] = 'your-gemini-api-key-here'

# Activate virtual environment
activate_this = '/home/Supportzetsu/.virtualenvs/zetsu-env/bin/activate_this.py'
if os.path.exists(activate_this):
    with open(activate_this) as f:
        exec(f.read(), {'__file__': activate_this})

# Import Flask app
from flask_app import app as application

# For debugging (remove in production)
# application.debug = False
