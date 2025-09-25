# 🏥 Dr. Payal's Hospital CRM - Complete Hosting Guide

This guide provides step-by-step instructions for hosting the Hospital CRM application locally, with Docker, and on Render.com.

## 📋 Prerequisites

- Python 3.11 or higher
- Git
- Docker and Docker Compose (for Docker deployment)
- A Render.com account (for cloud deployment)

## 🖥️ Local Development Setup

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone https://github.com/1981Rupal/Dr_payal.git
cd Dr_payal

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings (optional for basic setup)
# The default SQLite configuration will work out of the box
```

### Step 3: Run the Application

```bash
# Option 1: Use the simple run script
python run_local.py

# Option 2: Run directly
python app.py

# Option 3: Use Flask CLI
export FLASK_APP=app.py
flask run --host=0.0.0.0 --port=5000
```

### Step 4: Access the Application

- Open your browser and go to: `http://localhost:5000`
- Default login credentials:
  - **Super Admin**: `superadmin` / `admin123`
  - **Doctor**: `doctor` / `doctor123`
  - **Staff**: `staff` / `staff123`

## 🐳 Docker Deployment

### Step 1: Prepare Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file if needed (optional for basic setup)
```

### Step 2: Build and Run with Docker Compose

```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

### Step 3: Access the Application

- Open your browser and go to: `http://localhost:5000`
- The application will use PostgreSQL database in Docker
- Same login credentials as local setup

### Docker Management Commands

```bash
# Rebuild only the app
docker-compose build app

# Restart specific service
docker-compose restart app

# View database logs
docker-compose logs db

# Access database directly
docker-compose exec db psql -U hospital_user -d hospital_crm

# Clean up everything
docker-compose down -v --remove-orphans
```

## ☁️ Render.com Deployment

### Step 1: Prepare Repository

1. Push your code to GitHub
2. Ensure all files are committed and pushed

### Step 2: Create Render Services

1. **Sign up/Login** to [Render.com](https://render.com)

2. **Create Database**:
   - Click "New +" → "PostgreSQL"
   - Name: `hospital-crm-db`
   - Database: `hospital_crm`
   - User: `hospital_user`
   - Region: Choose closest to your users
   - Plan: Free or Starter

3. **Create Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Name: `hospital-crm`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 wsgi:app`

### Step 3: Configure Environment Variables

In your Render web service settings, add these environment variables:

```
FLASK_ENV=production
DATABASE_URL=[Auto-filled by Render from database]
SECRET_KEY=[Generate a secure random key]
UPLOAD_FOLDER=/opt/render/project/src/uploads
MAX_CONTENT_LENGTH=16777216
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
PREFERRED_URL_SCHEME=https
ENABLE_WHATSAPP=false
ENABLE_CHATBOT=false
ENABLE_ONLINE_CONSULTATION=false
ENABLE_PAYMENT_GATEWAY=false
ENABLE_EMAIL_NOTIFICATIONS=false
ENABLE_SMS_NOTIFICATIONS=false
```

### Step 4: Deploy

1. Click "Create Web Service"
2. Wait for deployment to complete
3. Access your application at the provided Render URL

## 🔧 Configuration Options

### Database Options

- **Local Development**: SQLite (default, no setup required)
- **Docker**: PostgreSQL (automatically configured)
- **Production**: PostgreSQL (recommended)

### Optional Features

Enable these features by setting environment variables to `true`:

- `ENABLE_WHATSAPP`: WhatsApp integration via Twilio
- `ENABLE_CHATBOT`: AI chatbot functionality
- `ENABLE_EMAIL_NOTIFICATIONS`: Email notifications
- `ENABLE_PAYMENT_GATEWAY`: Payment processing
- `ENABLE_ONLINE_CONSULTATION`: Video consultation features

### Security Settings

For production deployments, ensure:

- Use strong `SECRET_KEY`
- Set `SESSION_COOKIE_SECURE=true` for HTTPS
- Configure proper database credentials
- Enable CSRF protection

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Database Connection**: Check DATABASE_URL format
3. **Port Conflicts**: Change port in run commands if 5000 is busy
4. **Permission Errors**: Ensure proper file permissions

### Getting Help

- Check application logs for error details
- Verify environment variables are set correctly
- Ensure all required files are present
- Test with minimal configuration first

## 📝 Default Login Credentials

After first setup, use these credentials to access the system:

- **Super Admin**: `superadmin` / `admin123`
- **Doctor**: `doctor` / `doctor123`
- **Staff**: `staff` / `staff123`

**Important**: Change these default passwords in production!

## 🔄 Updates and Maintenance

### Local Updates
```bash
git pull origin main
pip install -r requirements.txt
python run_local.py
```

### Docker Updates
```bash
git pull origin main
docker-compose down
docker-compose up --build
```

### Render Updates
- Push changes to GitHub
- Render will automatically redeploy

---

**Need help?** Check the application logs or create an issue in the GitHub repository.
