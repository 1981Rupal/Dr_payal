#!/bin/bash

# Render.com Deployment Script for Hospital CRM
# This script prepares the application for deployment on Render

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "app_enhanced.py" ]; then
    log_error "This script must be run from the project root directory"
    exit 1
fi

log_info "Starting Render deployment preparation..."

# Create uploads directory if it doesn't exist
log_info "Creating necessary directories..."
mkdir -p uploads
mkdir -p logs
mkdir -p static/uploads

# Set proper permissions
chmod 755 uploads
chmod 755 logs
chmod 755 static/uploads

# Create a Render-specific requirements file if needed
log_info "Checking requirements..."
if [ ! -f "requirements.txt" ]; then
    log_error "requirements.txt not found!"
    exit 1
fi

# Add Render-specific dependencies if not present
RENDER_DEPS="gunicorn psycopg2-binary"
for dep in $RENDER_DEPS; do
    if ! grep -q "^$dep" requirements.txt; then
        log_info "Adding $dep to requirements.txt"
        echo "$dep" >> requirements.txt
    fi
done

# Create Procfile for Render (alternative to render.yaml)
log_info "Creating Procfile..."
cat > Procfile << EOF
web: gunicorn --bind 0.0.0.0:\$PORT --workers 2 --worker-class gevent --worker-connections 1000 --timeout 120 --keepalive 2 --max-requests 1000 --max-requests-jitter 100 --access-logfile - --error-logfile - wsgi:app
worker: celery -A wsgi.app.celery worker --loglevel=info --concurrency=2
beat: celery -A wsgi.app.celery beat --loglevel=info
EOF

# Create runtime.txt for Python version
log_info "Creating runtime.txt..."
echo "python-3.11.0" > runtime.txt

# Create a health check endpoint test
log_info "Creating health check test..."
cat > scripts/test_health.py << 'EOF'
#!/usr/bin/env python3
"""
Test health check endpoint for Render deployment
"""

import requests
import sys
import os

def test_health_endpoint():
    """Test the health endpoint"""
    try:
        # Get the app URL from environment or use default
        app_url = os.getenv('RENDER_EXTERNAL_URL', 'http://localhost:5000')
        
        response = requests.get(f"{app_url}/health", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Health check passed: {data}")
            return True
        else:
            print(f"✗ Health check failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Health check error: {e}")
        return False

if __name__ == "__main__":
    if test_health_endpoint():
        sys.exit(0)
    else:
        sys.exit(1)
EOF

chmod +x scripts/test_health.py

# Create environment variables template for Render
log_info "Creating environment variables template..."
cat > .env.render.template << 'EOF'
# Render Environment Variables Template
# Copy these to your Render service environment variables

# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-secret-key-here

# Database (automatically provided by Render)
# DATABASE_URL=postgresql://user:password@host:port/database

# Redis (automatically provided by Render)
# REDIS_URL=redis://host:port

# File Upload Configuration
UPLOAD_FOLDER=/opt/render/project/src/uploads
MAX_CONTENT_LENGTH=16777216

# Security Settings
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax
WTF_CSRF_ENABLED=true
PREFERRED_URL_SCHEME=https

# Optional: External Services
# TWILIO_ACCOUNT_SID=your-twilio-sid
# TWILIO_AUTH_TOKEN=your-twilio-token
# TWILIO_WHATSAPP_NUMBER=your-whatsapp-number
# OPENAI_API_KEY=your-openai-key
# SENTRY_DSN=your-sentry-dsn

# Email Configuration (optional)
# MAIL_SERVER=smtp.gmail.com
# MAIL_PORT=587
# MAIL_USE_TLS=true
# MAIL_USERNAME=your-email@gmail.com
# MAIL_PASSWORD=your-app-password
EOF

# Create a deployment checklist
log_info "Creating deployment checklist..."
cat > RENDER_DEPLOYMENT.md << 'EOF'
# Render Deployment Checklist

## Pre-deployment Steps

1. **Repository Setup**
   - [ ] Code is pushed to GitHub/GitLab
   - [ ] Repository is public or Render has access
   - [ ] All sensitive data is removed from code

2. **Configuration Files**
   - [ ] `render.yaml` is configured
   - [ ] `requirements.txt` includes all dependencies
   - [ ] `wsgi.py` is present and correct
   - [ ] Health check endpoint (`/health`) is working

3. **Environment Variables**
   - [ ] Copy variables from `.env.render.template`
   - [ ] Set `SECRET_KEY` (use Render's generate option)
   - [ ] Configure external service keys if needed

## Render Service Setup

1. **Create Services**
   - [ ] Web Service: hospital-crm
   - [ ] Worker Service: hospital-crm-worker (optional)
   - [ ] Scheduler Service: hospital-crm-scheduler (optional)

2. **Create Database**
   - [ ] PostgreSQL database: hospital-crm-db
   - [ ] Note the connection string

3. **Create Redis**
   - [ ] Redis instance: hospital-crm-redis
   - [ ] Note the connection string

## Deployment Steps

1. **Connect Repository**
   - Go to Render Dashboard
   - Click "New +" → "Web Service"
   - Connect your GitHub/GitLab repository
   - Select the repository

2. **Configure Web Service**
   - Name: `hospital-crm`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt && python migrations_setup.py`
   - Start Command: `gunicorn --bind 0.0.0.0:$PORT --workers 2 wsgi:app`

3. **Set Environment Variables**
   - Copy from `.env.render.template`
   - Use database and Redis connection strings from Render

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete
   - Check logs for any errors

## Post-deployment Verification

1. **Health Check**
   - [ ] Visit `https://your-app.onrender.com/health`
   - [ ] Should return JSON with status information

2. **Application Access**
   - [ ] Visit `https://your-app.onrender.com`
   - [ ] Login page should load
   - [ ] Test login functionality

3. **Database**
   - [ ] Check if tables are created
   - [ ] Test patient/appointment creation

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check `requirements.txt` for missing dependencies
   - Ensure Python version compatibility

2. **Database Connection Issues**
   - Verify `DATABASE_URL` environment variable
   - Check if migrations ran successfully

3. **Static Files Not Loading**
   - Ensure static files are properly configured
   - Check file paths in templates

4. **Health Check Failing**
   - Check application logs
   - Verify database connectivity
   - Test health endpoint locally

### Useful Commands

```bash
# Test health endpoint locally
python scripts/test_health.py

# Check logs
# Go to Render Dashboard → Your Service → Logs

# Manual migration (if needed)
# Add to build command: python migrations_setup.py
```

## Monitoring

1. **Set up monitoring**
   - [ ] Configure Sentry for error tracking
   - [ ] Set up uptime monitoring
   - [ ] Monitor resource usage

2. **Backup Strategy**
   - [ ] Regular database backups
   - [ ] File upload backups
   - [ ] Configuration backups

## Scaling

1. **Performance Optimization**
   - Monitor response times
   - Upgrade plan if needed
   - Consider adding worker services

2. **Database Scaling**
   - Monitor database performance
   - Upgrade database plan if needed
   - Consider read replicas for high traffic
EOF

# Create a simple migration script for Render
log_info "Creating Render migration script..."
cat > scripts/render_migrate.py << 'EOF'
#!/usr/bin/env python3
"""
Database migration script for Render deployment
"""

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app_enhanced import create_app
from models import db

def run_migrations():
    """Run database migrations"""
    app = create_app()
    
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✓ Database tables created successfully")
            
            # Run any additional setup
            from migrations_setup import setup_initial_data
            setup_initial_data()
            print("✓ Initial data setup completed")
            
            return True
            
        except Exception as e:
            print(f"✗ Migration failed: {e}")
            return False

if __name__ == "__main__":
    if run_migrations():
        print("✓ All migrations completed successfully")
        sys.exit(0)
    else:
        print("✗ Migration failed")
        sys.exit(1)
EOF

chmod +x scripts/render_migrate.py

# Final checks
log_info "Running final checks..."

# Check if wsgi.py exists
if [ ! -f "wsgi.py" ]; then
    log_error "wsgi.py not found! This is required for Render deployment."
    exit 1
fi

# Check if health endpoint exists
if ! grep -q "/health" app_enhanced.py; then
    log_warning "Health endpoint not found in app_enhanced.py"
fi

log_success "Render deployment preparation completed!"
log_info "Next steps:"
echo "1. Push your code to GitHub/GitLab"
echo "2. Create a new Web Service on Render"
echo "3. Connect your repository"
echo "4. Set environment variables from .env.render.template"
echo "5. Deploy and test"
echo ""
echo "For detailed instructions, see RENDER_DEPLOYMENT.md"
