#!/bin/bash
# PythonAnywhere Deployment Script
# Run this script on PythonAnywhere console

echo "====================================="
echo "Flask App Deployment Script"
echo "====================================="

# Navigate to project directory
cd /home/Supportzetsu/Support-zetsu-preview

echo "Step 1: Activating virtual environment..."
source /home/Supportzetsu/.virtualenvs/zetsu-env/bin/activate

echo "Step 2: Installing dependencies..."
pip install -r requirements.txt

echo "Step 3: Cleaning cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete

echo "Step 4: Cleaning log files..."
rm -f error.log *.log 2>/dev/null

echo "Step 5: Testing imports..."
python3 << 'EOF'
try:
    import flask
    print("✓ Flask imported successfully")
    from flask_wtf.csrf import CSRFProtect
    print("✓ Flask-WTF imported successfully")
    import google.generativeai as genai
    print("✓ Google GenerativeAI imported successfully")
    from flask_app import app
    print("✓ Flask app imported successfully")
    print("\n✅ All imports successful!")
except ImportError as e:
    print(f"\n❌ Import error: {e}")
    exit(1)
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "====================================="
    echo "✅ Deployment Complete!"
    echo "====================================="
    echo ""
    echo "Next Steps:"
    echo "1. Go to PythonAnywhere Web tab"
    echo "2. Click 'Reload' button to restart the app"
    echo "3. Visit your website to verify it's working"
    echo ""
    echo "Important: Remember to set environment variables:"
    echo "  - SECRET_KEY"
    echo "  - GEMINI_API_KEY"
    echo ""
else
    echo ""
    echo "====================================="
    echo "❌ Deployment Failed"
    echo "====================================="
    echo "Check the error messages above"
fi
