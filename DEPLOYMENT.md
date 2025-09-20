# 🚀 Hospital CRM Deployment Guide

This guide provides step-by-step instructions for deploying the Hospital CRM system on various platforms.

## 📋 Prerequisites

### System Requirements
- **Operating System**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: 10GB free space
- **Network**: Internet connection for API integrations

### Required Software
- **Docker Desktop** (recommended) or **Python 3.11+**
- **Git** for version control
- **Text Editor** (VS Code, Sublime Text, etc.)

## 🐳 Docker Deployment (Recommended)

### Step 1: Install Docker
#### Windows
1. Download Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop)
2. Run the installer and follow the setup wizard
3. Restart your computer when prompted
4. Verify installation: `docker --version`

#### macOS
```bash
# Using Homebrew
brew install --cask docker

# Or download from docker.com
```

#### Linux (Ubuntu)
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Step 2: Clone and Configure
```bash
# Clone the repository
git clone https://github.com/your-username/hospital-crm.git
cd hospital-crm

# Copy environment configuration
cp .env.example .env

# Edit .env file with your settings
# Use your preferred text editor
code .env  # VS Code
nano .env  # Terminal editor
```

### Step 3: Configure Environment Variables
Edit the `.env` file with your specific configuration:

```env
# Database (leave as-is for Docker)
DATABASE_URL=postgresql://hospital_user:hospital_password_2024@db:5432/hospital_crm

# Security (CHANGE THESE!)
SECRET_KEY=your-unique-secret-key-here-change-this

# WhatsApp Integration (Optional)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# AI Chatbot (Optional)
OPENAI_API_KEY=your_openai_api_key

# Email Configuration (Optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
```

### Step 4: Deploy
#### Windows
```batch
# Run the deployment script
scripts\deploy.bat local
```

#### Linux/macOS
```bash
# Make script executable
chmod +x scripts/deploy.sh

# Run deployment
./scripts/deploy.sh local
```

#### Manual Docker Commands
```bash
# Build and start services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f app
```

### Step 5: Access the Application
1. Open your web browser
2. Navigate to `http://localhost:5000`
3. Login with default credentials:
   - **Username**: `superadmin`
   - **Password**: `admin123`

⚠️ **Important**: Change the default password immediately after first login!

## ☁️ Render Deployment

### Step 1: Prepare Repository
1. Fork this repository to your GitHub account
2. Clone your fork locally
3. Configure environment variables in `.env`
4. Commit and push changes

### Step 2: Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with your GitHub account
3. Connect your GitHub repository

### Step 3: Create Database
1. In Render Dashboard, click "New +"
2. Select "PostgreSQL"
3. Configure:
   - **Name**: `hospital-crm-db`
   - **Database**: `hospital_crm`
   - **User**: `hospital_user`
   - **Region**: Choose closest to your users
4. Click "Create Database"
5. Note the connection string

### Step 4: Create Web Service
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: `hospital-crm`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT app_enhanced:create_app()`

### Step 5: Configure Environment Variables
Add these environment variables in Render:

```
DATABASE_URL=<your-render-postgres-connection-string>
SECRET_KEY=<generate-a-secure-secret-key>
FLASK_ENV=production
TWILIO_ACCOUNT_SID=<your-twilio-sid>
TWILIO_AUTH_TOKEN=<your-twilio-token>
OPENAI_API_KEY=<your-openai-key>
```

### Step 6: Deploy
1. Click "Create Web Service"
2. Render will automatically build and deploy
3. Access your app at the provided URL

## 🖥️ VPS/Server Deployment

### Step 1: Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Git
sudo apt install git -y
```

### Step 2: Deploy Application
```bash
# Clone repository
git clone https://github.com/your-username/hospital-crm.git
cd hospital-crm

# Configure environment
cp .env.example .env
nano .env  # Edit with your settings

# Deploy
./scripts/deploy.sh local
```

### Step 3: Configure Nginx (Optional)
For production with custom domain:

```bash
# Install Nginx
sudo apt install nginx -y

# Copy our Nginx config
sudo cp nginx/nginx.conf /etc/nginx/sites-available/hospital-crm
sudo ln -s /etc/nginx/sites-available/hospital-crm /etc/nginx/sites-enabled/

# Update config with your domain
sudo nano /etc/nginx/sites-enabled/hospital-crm

# Test and restart Nginx
sudo nginx -t
sudo systemctl restart nginx
```

## 🔧 Manual Installation (Development)

### Step 1: Install Python
```bash
# Check Python version
python3 --version  # Should be 3.11+

# Install pip if not available
sudo apt install python3-pip -y
```

### Step 2: Setup Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
# Install Python packages
pip install -r requirements.txt
```

### Step 4: Setup Database
```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Create database
sudo -u postgres createdb hospital_crm
sudo -u postgres createuser hospital_user
sudo -u postgres psql -c "ALTER USER hospital_user WITH PASSWORD 'hospital_password_2024';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE hospital_crm TO hospital_user;"
```

### Step 5: Configure and Run
```bash
# Copy environment file
cp .env.example .env

# Edit with your database settings
nano .env

# Run database migrations
python migrations_setup.py

# Start the application
python app_enhanced.py
```

## 🧪 Testing the Deployment

### Health Check
```bash
# Check if application is running
curl http://localhost:5000/health

# Expected response:
# {"status": "healthy", "database": "connected", "timestamp": "..."}
```

### Login Test
1. Open `http://localhost:5000`
2. Login with:
   - Username: `superadmin`
   - Password: `admin123`
3. You should see the dashboard

### Feature Testing
1. **Patient Management**: Try adding a new patient
2. **Appointments**: Create a test appointment
3. **WhatsApp**: Send a test message (if configured)
4. **AI Chatbot**: Test the chatbot functionality

## 🔍 Troubleshooting

### Common Issues

#### Docker Issues
```bash
# Check Docker status
docker --version
docker-compose --version

# Check running containers
docker-compose ps

# View logs
docker-compose logs app
docker-compose logs db

# Restart services
docker-compose restart

# Clean restart
docker-compose down
docker-compose up -d
```

#### Database Connection Issues
```bash
# Check database logs
docker-compose logs db

# Connect to database manually
docker-compose exec db psql -U hospital_user -d hospital_crm

# Reset database
docker-compose down -v
docker-compose up -d
```

#### Permission Issues (Linux)
```bash
# Fix file permissions
sudo chown -R $USER:$USER .

# Fix Docker permissions
sudo usermod -aG docker $USER
# Logout and login again
```

#### Port Conflicts
```bash
# Check what's using port 5000
sudo lsof -i :5000

# Kill process if needed
sudo kill -9 <PID>

# Or change port in docker-compose.yml
```

### Getting Help

1. **Check Logs**: Always check application and database logs first
2. **GitHub Issues**: Report bugs at [GitHub Issues](https://github.com/your-username/hospital-crm/issues)
3. **Documentation**: Review the main README.md for additional information
4. **Community**: Join our community discussions

## 🔒 Security Considerations

### Production Deployment
1. **Change Default Passwords**: Update all default credentials
2. **Use HTTPS**: Configure SSL certificates
3. **Firewall**: Configure proper firewall rules
4. **Backup**: Set up regular database backups
5. **Updates**: Keep system and dependencies updated

### Environment Variables
Never commit sensitive information to version control:
- API keys
- Database passwords
- Secret keys
- Email passwords

## 📊 Monitoring and Maintenance

### Health Monitoring
```bash
# Check application health
curl http://localhost:5000/health

# Monitor Docker containers
docker-compose ps
docker stats
```

### Backup
```bash
# Create database backup
./scripts/deploy.sh backup

# Backup files
tar -czf backup_$(date +%Y%m%d).tar.gz uploads/ logs/
```

### Updates
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose build --no-cache
docker-compose up -d
```

---

**Need help?** Contact support at support@drpayal.com or create an issue on GitHub.
