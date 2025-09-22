# 🚀 Deployment Guide

This guide covers all deployment options for the Hospital CRM System.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Docker Deployment](#docker-deployment)
3. [Render.com Deployment](#rendercom-deployment)
4. [Traditional Server Deployment](#traditional-server-deployment)
5. [Environment Configuration](#environment-configuration)
6. [Database Setup](#database-setup)
7. [SSL Configuration](#ssl-configuration)
8. [Monitoring Setup](#monitoring-setup)
9. [Backup Configuration](#backup-configuration)
10. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **CPU**: 2+ cores recommended
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 20GB minimum, SSD recommended
- **OS**: Linux (Ubuntu 20.04+), macOS, or Windows with WSL2

### Software Requirements

- **Docker**: 20.10+ and Docker Compose 2.0+
- **Python**: 3.8+ (for manual installation)
- **PostgreSQL**: 13+ (for manual installation)
- **Redis**: 6+ (for manual installation)
- **Git**: Latest version

## Docker Deployment

### Production Deployment

1. **Clone and Setup**
```bash
git clone https://github.com/1981Rupal/Dr_payal.git
cd Dr_payal
cp .env.example .env
```

2. **Configure Environment**
Edit `.env` file with your production settings:
```bash
# Required settings
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=postgresql://hospital_user:secure_password@db:5432/hospital_crm
REDIS_URL=redis://redis:6379/0
FLASK_ENV=production
DEBUG=False
```

3. **Start Services**
```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

4. **Initialize Database**
```bash
# Run database migrations
docker-compose exec web python migrations_setup.py

# Create admin user (optional)
docker-compose exec web python -c "
from app_enhanced import create_app
from models import db, User, UserRole
app = create_app()
with app.app_context():
    admin = User(
        username='admin',
        email='admin@hospital.com',
        first_name='Admin',
        last_name='User',
        role=UserRole.SUPER_ADMIN,
        phone='+1234567890'
    )
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
    print('Admin user created: admin/admin123')
"
```

5. **Access Application**
- Application: http://localhost:5000
- Grafana: http://localhost:3000 (admin/admin)
- Prometheus: http://localhost:9090

### Development Deployment

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# Access additional services
# - Adminer: http://localhost:8080
# - Redis Commander: http://localhost:8081
# - Mailhog: http://localhost:8025
```

### Docker Management

Use the provided management script:

```bash
# Make script executable
chmod +x scripts/docker_manager.sh

# Available commands
./scripts/docker_manager.sh dev-up      # Start development
./scripts/docker_manager.sh prod-up     # Start production
./scripts/docker_manager.sh down        # Stop all services
./scripts/docker_manager.sh logs        # View logs
./scripts/docker_manager.sh backup      # Create backup
./scripts/docker_manager.sh restore     # Restore backup
./scripts/docker_manager.sh health      # Check health
```

## Render.com Deployment

### Automatic Deployment

1. **Fork Repository**
   - Fork the repository to your GitHub account

2. **Connect to Render**
   - Sign up at [render.com](https://render.com)
   - Connect your GitHub account
   - Select the forked repository

3. **Configure Service**
   - Render will automatically detect the `render.yaml` configuration
   - Review and approve the service configuration
   - Set environment variables in Render dashboard

4. **Environment Variables**
   Set these in Render dashboard:
   ```
   SECRET_KEY=your-secret-key
   OPENAI_API_KEY=your-openai-key
   WHATSAPP_API_KEY=your-whatsapp-key
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   ```

5. **Deploy**
   - Click "Deploy" to start deployment
   - Monitor deployment logs
   - Access your application at the provided URL

### Manual Render Deployment

1. **Prepare Deployment**
```bash
# Run the Render deployment script
./scripts/render_deploy.sh
```

2. **Create Services**
   - Web Service: Use the repository root
   - Database: PostgreSQL 13+
   - Redis: Redis 6+

3. **Configure Build**
   - Build Command: `pip install -r requirements.txt && python migrations_setup.py`
   - Start Command: `gunicorn --bind 0.0.0.0:$PORT wsgi:app`

## Traditional Server Deployment

### Ubuntu/Debian Server

1. **System Setup**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib redis-server nginx

# Create application user
sudo useradd -m -s /bin/bash hospital
sudo usermod -aG sudo hospital
```

2. **Database Setup**
```bash
# Configure PostgreSQL
sudo -u postgres psql
CREATE DATABASE hospital_crm;
CREATE USER hospital_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE hospital_crm TO hospital_user;
\q
```

3. **Application Setup**
```bash
# Switch to application user
sudo su - hospital

# Clone repository
git clone https://github.com/1981Rupal/Dr_payal.git
cd Dr_payal

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Initialize database
python migrations_setup.py
```

4. **Systemd Service**
```bash
# Create service file
sudo tee /etc/systemd/system/hospital-crm.service > /dev/null <<EOF
[Unit]
Description=Hospital CRM
After=network.target

[Service]
Type=exec
User=hospital
Group=hospital
WorkingDirectory=/home/hospital/Dr_payal
Environment=PATH=/home/hospital/Dr_payal/venv/bin
ExecStart=/home/hospital/Dr_payal/venv/bin/gunicorn --bind 127.0.0.1:5000 wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable hospital-crm
sudo systemctl start hospital-crm
```

5. **Nginx Configuration**
```bash
# Create Nginx configuration
sudo tee /etc/nginx/sites-available/hospital-crm > /dev/null <<EOF
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static {
        alias /home/hospital/Dr_payal/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/hospital-crm /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Environment Configuration

### Production Environment Variables

```bash
# Application
SECRET_KEY=your-super-secret-key-here
FLASK_ENV=production
DEBUG=False

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/hospital_crm

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=15
SESSION_COOKIE_SECURE=true
WTF_CSRF_ENABLED=true

# Features
ENABLE_WHATSAPP=true
ENABLE_CHATBOT=true
ENABLE_EMAIL_NOTIFICATIONS=true
ENABLE_ONLINE_CONSULTATIONS=true

# External Services
WHATSAPP_API_KEY=your-whatsapp-api-key
OPENAI_API_KEY=your-openai-api-key
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# File Storage
UPLOAD_FOLDER=/var/uploads
MAX_CONTENT_LENGTH=16777216

# Monitoring
LOG_TO_STDOUT=false
LOG_LEVEL=INFO

# Backup
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_S3_BUCKET=your-backup-bucket
BACKUP_RETENTION_DAYS=30
```

### Development Environment Variables

```bash
# Application
SECRET_KEY=dev-secret-key
FLASK_ENV=development
DEBUG=true

# Database
DATABASE_URL=postgresql://hospital_user:hospital_password_2024@localhost:5432/hospital_crm

# Redis
REDIS_URL=redis://localhost:6379/0

# Security (Relaxed for development)
SESSION_COOKIE_SECURE=false
WTF_CSRF_ENABLED=false

# Features (Disabled for development)
ENABLE_WHATSAPP=false
ENABLE_CHATBOT=false
ENABLE_EMAIL_NOTIFICATIONS=false

# Logging
LOG_TO_STDOUT=true
LOG_LEVEL=DEBUG
```

## Database Setup

### PostgreSQL Setup

1. **Installation**
```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib

# macOS
brew install postgresql

# Start service
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

2. **Database Creation**
```bash
sudo -u postgres psql
CREATE DATABASE hospital_crm;
CREATE USER hospital_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE hospital_crm TO hospital_user;
ALTER USER hospital_user CREATEDB;  # For running tests
\q
```

3. **Connection Testing**
```bash
psql -h localhost -U hospital_user -d hospital_crm
```

### Database Migrations

```bash
# Initialize database
python migrations_setup.py

# Create migration (if needed)
flask db migrate -m "Description of changes"

# Apply migration
flask db upgrade
```

## SSL Configuration

### Let's Encrypt with Certbot

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Manual SSL Certificate

```bash
# Update Nginx configuration
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;

    # Rest of configuration...
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

## Monitoring Setup

### Prometheus and Grafana (Docker)

Monitoring is included in the Docker Compose setup:

```bash
# Access monitoring
# Grafana: http://localhost:3000 (admin/admin)
# Prometheus: http://localhost:9090

# Import dashboards
# - Go to Grafana
# - Import dashboard from monitoring/grafana/dashboards/
```

### Manual Monitoring Setup

1. **Prometheus**
```bash
# Install Prometheus
wget https://github.com/prometheus/prometheus/releases/download/v2.40.0/prometheus-2.40.0.linux-amd64.tar.gz
tar xvfz prometheus-*.tar.gz
sudo mv prometheus-*/prometheus /usr/local/bin/
sudo mv prometheus-*/promtool /usr/local/bin/

# Create configuration
sudo mkdir /etc/prometheus
sudo cp monitoring/prometheus.yml /etc/prometheus/
```

2. **Grafana**
```bash
# Install Grafana
sudo apt-get install -y software-properties-common
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
sudo apt-get update
sudo apt-get install grafana

# Start Grafana
sudo systemctl start grafana-server
sudo systemctl enable grafana-server
```

## Backup Configuration

### Automated Backups

```bash
# Create backup script
sudo tee /usr/local/bin/hospital-backup.sh > /dev/null <<EOF
#!/bin/bash
cd /home/hospital/Dr_payal
source venv/bin/activate
python -c "
from utils.backup_system import BackupManager
from app_enhanced import create_app
app = create_app()
with app.app_context():
    backup_manager = BackupManager(app)
    result = backup_manager.create_full_backup(upload_to_s3=True)
    print(f'Backup completed: {result}')
"
EOF

chmod +x /usr/local/bin/hospital-backup.sh

# Schedule daily backups
sudo crontab -e
# Add: 0 2 * * * /usr/local/bin/hospital-backup.sh
```

### Manual Backup

```bash
# Database backup
pg_dump -h localhost -U hospital_user hospital_crm > backup_$(date +%Y%m%d_%H%M%S).sql

# Files backup
tar -czf files_backup_$(date +%Y%m%d_%H%M%S).tar.gz uploads static/uploads logs
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connection
psql -h localhost -U hospital_user -d hospital_crm

# Check logs
sudo tail -f /var/log/postgresql/postgresql-13-main.log
```

2. **Redis Connection Failed**
```bash
# Check Redis status
sudo systemctl status redis-server

# Test connection
redis-cli ping

# Check logs
sudo tail -f /var/log/redis/redis-server.log
```

3. **Application Won't Start**
```bash
# Check application logs
sudo journalctl -u hospital-crm -f

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log

# Check permissions
sudo chown -R hospital:hospital /home/hospital/Dr_payal
```

4. **Docker Issues**
```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs web

# Restart services
docker-compose restart

# Clean rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Performance Issues

1. **Slow Database Queries**
```bash
# Enable query logging in PostgreSQL
sudo nano /etc/postgresql/13/main/postgresql.conf
# Set: log_statement = 'all'
# Set: log_min_duration_statement = 1000

sudo systemctl restart postgresql
```

2. **High Memory Usage**
```bash
# Check memory usage
free -h
docker stats

# Optimize PostgreSQL
sudo nano /etc/postgresql/13/main/postgresql.conf
# Adjust: shared_buffers, effective_cache_size, work_mem
```

3. **High CPU Usage**
```bash
# Check processes
top
htop

# Check application performance
docker-compose exec web python -c "
from utils.monitoring import HealthChecker
from app_enhanced import create_app
app = create_app()
with app.app_context():
    health = HealthChecker(app)
    print(health.get_comprehensive_health())
"
```

### Getting Help

- Check application logs: `/var/log/hospital-crm/`
- Review health endpoint: `http://your-domain.com/health`
- Monitor metrics: Grafana dashboard
- GitHub Issues: [Report bugs](https://github.com/1981Rupal/Dr_payal/issues)
- Documentation: [Wiki](https://github.com/1981Rupal/Dr_payal/wiki)
