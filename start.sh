#!/bin/bash

# Dr. Payal's Hospital CRM - Startup Script

echo "🏥 Dr. Payal's Hospital CRM - Startup Script"
echo "============================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python version: $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file..."
    cat > .env << EOF
# Database Configuration
DATABASE_URL=sqlite:///hospital_crm.db
SECRET_KEY=dev-secret-key-change-in-production

# WhatsApp/Twilio Configuration (Optional)
TWILIO_ACCOUNT_SID=demo_account_sid
TWILIO_AUTH_TOKEN=demo_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# Email Configuration (Optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password

# Feature Flags
ENABLE_WHATSAPP=true
ENABLE_EMAIL_NOTIFICATIONS=true
ENABLE_CHATBOT=true
EOF
    echo "✅ .env file created with default settings"
fi

# Check if main.py exists
if [ ! -f "main.py" ]; then
    echo "❌ main.py not found. Please ensure you're in the correct directory."
    exit 1
fi

echo ""
echo "🚀 Starting Dr. Payal's Hospital CRM..."
echo "📱 The application will be available at: http://localhost:5000"
echo ""
echo "👤 Default Login Credentials:"
echo "   Super Admin: superadmin / admin123"
echo "   Doctor: doctor / doctor123"
echo "   Staff: staff / staff123"
echo ""
echo "🔄 Starting application..."
echo "   Press Ctrl+C to stop the application"
echo ""

# Start the application
python main.py
