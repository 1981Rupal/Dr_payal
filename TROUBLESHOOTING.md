# 🔧 Dr. Payal's Hospital CRM - Troubleshooting Guide

## 🚨 Common Issues and Solutions

### 1. Application Won't Start

#### Error: "Port 5000 is already in use"

**Solution:**
```bash
# Find what's using port 5000
lsof -i :5000

# Kill the process (replace PID with actual process ID)
kill -9 <PID>

# Or use a different port
export PORT=8080
python main.py
```

#### Error: "Python not found" or "Command not found"

**Solution:**
```bash
# Install Python 3.8 or higher
# On Ubuntu/Debian:
sudo apt update
sudo apt install python3 python3-pip python3-venv

# On macOS (using Homebrew):
brew install python3

# On Windows: Download from https://python.org
```

#### Error: "No module named 'flask'"

**Solution:**
```bash
# Activate virtual environment first
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate     # Windows

# Then install dependencies
pip install -r requirements.txt
```

### 2. Database Issues

#### Error: "Database connection failed"

**Solution:**
```bash
# Delete existing database and recreate
rm hospital_crm.db

# Restart the application
python main.py
```

#### Error: "Table doesn't exist"

**Solution:**
```bash
# The application should auto-create tables
# If not, check the logs for specific errors
# Ensure models.py is present and correct
```

### 3. Login Issues

#### Error: "Invalid username or password"

**Default credentials:**
- Super Admin: `superadmin` / `admin123`
- Doctor: `doctor` / `doctor123`
- Staff: `staff` / `staff123`

**If still not working:**
```bash
# Delete database and restart to recreate default users
rm hospital_crm.db
python main.py
```

### 4. Template Errors

#### Error: "Template not found"

**Solution:**
```bash
# Ensure all template directories exist
mkdir -p templates/auth
mkdir -p templates/dashboard
mkdir -p templates/patients
mkdir -p templates/appointments
mkdir -p templates/billing
mkdir -p templates/reports
mkdir -p templates/users
mkdir -p templates/settings

# Check if templates are present
ls -la templates/
```

### 5. WhatsApp Integration Issues

#### Error: "WhatsApp service not working"

**Solution:**
The app works in demo mode by default. For production:

1. Sign up for Twilio account
2. Get WhatsApp sandbox credentials
3. Update `.env` file:
```bash
TWILIO_ACCOUNT_SID=your_real_account_sid
TWILIO_AUTH_TOKEN=your_real_auth_token
TWILIO_PHONE_NUMBER=your_whatsapp_number
```

### 6. Permission Errors

#### Error: "Permission denied"

**Solution:**
```bash
# Fix file permissions
chmod +x start.sh
chmod -R 755 .

# On Windows, run as Administrator
```

### 7. Import Errors

#### Error: "ModuleNotFoundError"

**Solution:**
```bash
# Ensure you're in the correct directory
pwd
ls -la main.py

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python path
python -c "import sys; print(sys.path)"
```

## 🔍 Diagnostic Commands

### Check Application Health

```bash
# Test health endpoint
curl http://localhost:5000/health

# Expected response:
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-09-24T10:00:00.000000+00:00"
}
```

### Check Dependencies

```bash
# List installed packages
pip list

# Check specific packages
pip show flask
pip show sqlalchemy
```

### Check File Structure

```bash
# Verify all required files are present
ls -la main.py models.py config.py requirements.txt
ls -la routes/
ls -la templates/
ls -la services/
```

### Check Database

```bash
# If using SQLite, check database file
ls -la hospital_crm.db

# Check database tables (if SQLite)
sqlite3 hospital_crm.db ".tables"
```

## 🐛 Debug Mode

### Enable Debug Logging

Add to your `.env` file:
```bash
FLASK_ENV=development
FLASK_DEBUG=True
LOG_LEVEL=DEBUG
```

### View Detailed Logs

```bash
# Run with verbose output
python main.py

# Check for specific errors in the output
```

## 🔧 Environment Issues

### Virtual Environment Problems

```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Environment Variables

```bash
# Check if .env file exists and has correct format
cat .env

# Verify environment variables are loaded
python -c "import os; print(os.environ.get('DATABASE_URL'))"
```

## 🌐 Network Issues

### Firewall/Network Problems

```bash
# Check if port is accessible
telnet localhost 5000

# Test from another machine
curl http://YOUR_IP:5000/health

# Check firewall settings (Linux)
sudo ufw status
```

### DNS/Host Issues

```bash
# Try different host configurations
python main.py --host=0.0.0.0 --port=5000

# Or modify main.py to use different host
app.run(debug=True, host='127.0.0.1', port=5000)
```

## 📱 Browser Issues

### Page Not Loading

1. **Clear browser cache**
2. **Try incognito/private mode**
3. **Try different browser**
4. **Check browser console for errors** (F12)

### JavaScript Errors

1. **Check browser console** (F12 → Console)
2. **Ensure static files are loading**
3. **Check network tab for failed requests**

## 🔒 Security Issues

### CSRF Token Errors

```bash
# Ensure SECRET_KEY is set in .env
SECRET_KEY=your-secret-key-here

# Clear browser cookies and try again
```

### Session Issues

```bash
# Clear browser data
# Restart the application
# Try different browser
```

## 📊 Performance Issues

### Slow Loading

```bash
# Check system resources
top
htop

# Monitor database queries
# Enable SQL logging in development
```

### Memory Issues

```bash
# Check memory usage
free -h

# Monitor Python process
ps aux | grep python
```

## 🆘 Getting Help

### Collect Debug Information

Before asking for help, collect:

1. **Operating System**: `uname -a` (Linux/macOS) or `systeminfo` (Windows)
2. **Python Version**: `python --version`
3. **Error Messages**: Copy exact error text
4. **Log Output**: Application startup logs
5. **File Structure**: `ls -la` output

### Log Files

```bash
# Application logs (if configured)
tail -f logs/app.log

# System logs
tail -f /var/log/syslog  # Linux
```

### Test Configuration

```bash
# Test basic Python functionality
python -c "print('Python is working')"

# Test Flask installation
python -c "import flask; print(f'Flask version: {flask.__version__}')"

# Test database connection
python -c "
from models import db
from main import create_app
app = create_app()
with app.app_context():
    print('Database connection: OK')
"
```

## ✅ Success Checklist

When everything is working correctly:

- [ ] Application starts without errors
- [ ] Health check returns "healthy"
- [ ] Database is created and initialized
- [ ] Default users are created
- [ ] Login works for all user roles
- [ ] Dashboard loads with statistics
- [ ] All menu items are accessible
- [ ] No error messages in browser console
- [ ] WhatsApp test works (demo mode)

## 🎯 Quick Fix Commands

```bash
# Nuclear option - reset everything
rm -rf venv hospital_crm.db __pycache__ .pytest_cache
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py

# Quick restart
pkill -f "python main.py"
python main.py

# Check if everything is working
curl http://localhost:5000/health
```

---

## 📞 Still Need Help?

If you're still experiencing issues:

1. **Check the error message carefully**
2. **Search for the specific error online**
3. **Try the nuclear option above**
4. **Ensure all prerequisites are installed**
5. **Check file permissions**

Remember: Most issues are related to:
- Missing dependencies
- Wrong Python version
- Port conflicts
- File permissions
- Missing environment variables

## 🎉 Success!

Once everything is working, you should see:
```
🏥 Starting Dr. Payal's Hospital CRM...
📱 Access the application at: http://localhost:5000
👤 Login credentials:
   Super Admin: superadmin / admin123
   Doctor: doctor / doctor123
   Staff: staff / staff123
```

Happy coding! 🏥✨
