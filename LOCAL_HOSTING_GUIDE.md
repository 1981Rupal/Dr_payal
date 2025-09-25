# 🏥 Dr. Payal's Hospital CRM - Local Hosting Guide

## 🚀 Quick Start (Local Development)

### Prerequisites

- **Python 3.8 or higher**
- **pip** (Python package installer)
- **Git**

### 1. Clone the Repository

```bash
git clone https://github.com/1981Rupal/Dr_payal.git
cd Dr_payal
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the root directory:

```bash
# Database Configuration
DATABASE_URL=sqlite:///hospital_crm.db
SECRET_KEY=your-secret-key-here

# WhatsApp/Twilio Configuration (Optional)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
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
```

### 5. Run the Application

```bash
python main.py
```

**🎉 Success!** The application will be available at: **http://localhost:5000**

### 6. Default Login Credentials

- **Super Admin**: `superadmin` / `admin123`
- **Doctor**: `doctor` / `doctor123`
- **Staff**: `staff` / `staff123`

## 🔧 Alternative Running Methods

### Method 1: Using main.py (Recommended)
```bash
python main.py
```

### Method 2: Using Flask CLI
```bash
export FLASK_APP=main.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000
```

### Method 3: Using app.py
```bash
python app.py
```

## 🧪 Testing the Installation

### 1. Health Check
```bash
curl http://localhost:5000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-09-24T10:00:00.000000+00:00"
}
```

### 2. Test Login
1. Open browser: http://localhost:5000
2. Login with: `superadmin` / `admin123`
3. You should see the dashboard

### 3. Test API Endpoints
```bash
# Test patients API (requires login)
curl -X GET http://localhost:5000/api/patients

# Test appointments API
curl -X GET http://localhost:5000/api/appointments
```

## 📁 Project Structure

```
Dr_payal/
├── main.py                 # Main application entry point ⭐
├── app.py                  # Alternative entry point
├── models.py               # Database models
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables
├── routes/                # Application routes
│   ├── auth.py           # Authentication routes
│   ├── main.py           # Main routes
│   ├── patients.py       # Patient management
│   ├── appointments.py   # Appointment system
│   ├── billing.py        # Billing system
│   └── api.py            # API endpoints
├── services/             # Business logic services
│   ├── whatsapp_service.py
│   ├── email_service.py
│   ├── chatbot_service.py
│   ├── appointment_service.py
│   └── billing_service.py
├── templates/            # HTML templates
│   ├── base.html
│   ├── auth/
│   ├── dashboard/
│   ├── patients/
│   ├── appointments/
│   ├── billing/
│   └── reports/
└── static/              # Static files (CSS, JS, images)
    ├── css/
    ├── js/
    └── images/
```

## 🔧 Configuration Options

### Database Configuration

The application supports multiple database backends:

- **SQLite** (default for development): `sqlite:///hospital_crm.db`
- **PostgreSQL** (recommended for production): `postgresql://user:password@localhost/dbname`
- **MySQL**: `mysql://user:password@localhost/dbname`

### WhatsApp Integration

To enable WhatsApp notifications:

1. Sign up for a Twilio account
2. Get your Account SID and Auth Token
3. Configure a WhatsApp-enabled phone number
4. Update the `.env` file with your credentials

### Email Configuration

For email notifications:

1. Configure your SMTP settings in `.env`
2. For Gmail, use an App Password instead of your regular password

## 🐛 Troubleshooting

### Common Issues

1. **Port Already in Use**:
   ```bash
   # Find process using port 5000
   lsof -i :5000
   # Kill the process
   kill -9 <PID>
   ```

2. **Database Connection Error**:
   - Check database credentials in `.env`
   - Ensure database server is running
   - Delete `hospital_crm.db` and restart to recreate

3. **Template Not Found**:
   - Ensure all template files are present
   - Check template paths in routes

4. **WhatsApp Not Working**:
   - Verify Twilio credentials
   - Check phone number format
   - The app works in demo mode without real credentials

5. **Import Errors**:
   ```bash
   # Reinstall dependencies
   pip install -r requirements.txt --force-reinstall
   ```

### Logs

Check application logs for detailed error information:

```bash
# View application output
python main.py

# Check for specific errors in terminal output
```

## 🔒 Security Considerations

1. **Change Default Passwords**: Update all default user passwords
2. **Environment Variables**: Never commit `.env` files to version control
3. **Database Security**: Use strong database passwords
4. **Regular Updates**: Keep dependencies updated

## 📊 Features Available

### ✅ Working Features

- **👥 Patient Management**: Complete patient records
- **📅 Appointment Scheduling**: Calendar-based system
- **💰 Billing System**: Treatment packages and invoicing
- **📊 Reports & Analytics**: Comprehensive reporting
- **👤 User Management**: Role-based access control
- **📱 WhatsApp Integration**: Demo mode working
- **🔌 RESTful API**: Complete API endpoints
- **⚙️ System Settings**: Configurable settings

### 🎯 User Roles

- **Super Admin**: Full system access
- **Doctor**: Medical functionality access
- **Staff**: Administrative access

## 🎉 Success Indicators

When everything is working correctly, you should see:

1. ✅ Application starts without errors
2. ✅ Database initialized successfully
3. ✅ Default users created
4. ✅ Health check returns "healthy"
5. ✅ Login works for all user roles
6. ✅ Dashboard loads with statistics
7. ✅ All menu items are accessible

## 📞 Support

If you encounter any issues:

1. Check the troubleshooting section above
2. Ensure all prerequisites are installed
3. Verify the `.env` file configuration
4. Check the terminal output for error messages

---

## 🎉 Congratulations!

Your Dr. Payal's Hospital CRM is now running locally! 🏥✨

Access it at: **http://localhost:5000**
