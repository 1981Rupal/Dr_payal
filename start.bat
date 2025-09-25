@echo off
REM Dr. Payal's Hospital CRM - Windows Startup Script

echo 🏥 Dr. Payal's Hospital CRM - Windows Startup Script
echo =====================================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Show Python version
echo ✅ Python version:
python --version

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo ⚙️ Creating .env file...
    (
        echo # Database Configuration
        echo DATABASE_URL=sqlite:///hospital_crm.db
        echo SECRET_KEY=dev-secret-key-change-in-production
        echo.
        echo # WhatsApp/Twilio Configuration ^(Optional^)
        echo TWILIO_ACCOUNT_SID=demo_account_sid
        echo TWILIO_AUTH_TOKEN=demo_auth_token
        echo TWILIO_PHONE_NUMBER=+1234567890
        echo.
        echo # Email Configuration ^(Optional^)
        echo MAIL_SERVER=smtp.gmail.com
        echo MAIL_PORT=587
        echo MAIL_USE_TLS=True
        echo MAIL_USERNAME=your_email@gmail.com
        echo MAIL_PASSWORD=your_app_password
        echo.
        echo # Feature Flags
        echo ENABLE_WHATSAPP=true
        echo ENABLE_EMAIL_NOTIFICATIONS=true
        echo ENABLE_CHATBOT=true
    ) > .env
    echo ✅ .env file created with default settings
)

REM Check if main.py exists
if not exist "main.py" (
    echo ❌ main.py not found. Please ensure you're in the correct directory.
    pause
    exit /b 1
)

echo.
echo 🚀 Starting Dr. Payal's Hospital CRM...
echo 📱 The application will be available at: http://localhost:5000
echo.
echo 👤 Default Login Credentials:
echo    Super Admin: superadmin / admin123
echo    Doctor: doctor / doctor123
echo    Staff: staff / staff123
echo.
echo 🔄 Starting application...
echo    Press Ctrl+C to stop the application
echo.

REM Start the application
python main.py

pause
