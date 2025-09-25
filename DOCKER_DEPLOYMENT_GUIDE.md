# 🐳 Dr. Payal's Hospital CRM - Docker Deployment Guide

## 🚀 Quick Docker Deployment

### Prerequisites

- **Docker** (version 20.10 or higher)
- **Docker Compose** (version 2.0 or higher)
- **Git**

### 1. Clone the Repository

```bash
git clone https://github.com/1981Rupal/Dr_payal.git
cd Dr_payal
```

### 2. Quick Start with Docker Compose

```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

**🎉 Success!** The application will be available at: **http://localhost:5000**

### 3. Default Login Credentials

- **Super Admin**: `superadmin` / `admin123`
- **Doctor**: `doctor` / `doctor123`
- **Staff**: `staff` / `staff123`

## 📋 Docker Configuration Files

### Dockerfile

```dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs static/uploads

# Set environment variables
ENV FLASK_APP=main.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run the application
CMD ["python", "main.py"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://hospital_user:hospital_pass@db:5432/hospital_crm
      - SECRET_KEY=your-super-secret-production-key
      - FLASK_ENV=production
    depends_on:
      - db
      - redis
    volumes:
      - ./logs:/app/logs
      - ./uploads:/app/static/uploads
    restart: unless-stopped

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=hospital_crm
      - POSTGRES_USER=hospital_user
      - POSTGRES_PASSWORD=hospital_pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"
    restart: unless-stopped

volumes:
  postgres_data:
```

## 🔧 Docker Commands

### Basic Operations

```bash
# Build the image
docker-compose build

# Start services
docker-compose up

# Start in background
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs

# View specific service logs
docker-compose logs web
docker-compose logs db

# Restart a service
docker-compose restart web

# Scale the web service
docker-compose up --scale web=3
```

### Development Commands

```bash
# Build without cache
docker-compose build --no-cache

# Pull latest images
docker-compose pull

# Remove all containers and volumes
docker-compose down -v

# Execute commands in running container
docker-compose exec web bash
docker-compose exec web python -c "print('Hello from container')"

# View container status
docker-compose ps
```

## 🗄️ Database Management

### PostgreSQL Commands

```bash
# Connect to PostgreSQL
docker-compose exec db psql -U hospital_user -d hospital_crm

# Backup database
docker-compose exec db pg_dump -U hospital_user hospital_crm > backup.sql

# Restore database
docker-compose exec -T db psql -U hospital_user hospital_crm < backup.sql

# View database logs
docker-compose logs db
```

### Database Initialization

The application automatically:
1. Creates all database tables
2. Sets up default users
3. Initializes system settings

## 🔍 Monitoring and Health Checks

### Health Check Endpoint

```bash
# Check application health
curl http://localhost:5000/health

# Expected response:
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-09-24T10:00:00.000000+00:00"
}
```

### Container Health

```bash
# Check container health
docker-compose ps

# View health check logs
docker inspect dr_payal_web_1 | grep -A 10 Health
```

## 🌐 Production Deployment

### Environment Variables for Production

Create a `.env.production` file:

```bash
# Security
SECRET_KEY=your-super-secret-production-key-here
FLASK_ENV=production

# Database
DATABASE_URL=postgresql://user:password@db:5432/hospital_crm

# Security Headers
FORCE_HTTPS=true
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true

# WhatsApp (Production)
TWILIO_ACCOUNT_SID=your_production_twilio_sid
TWILIO_AUTH_TOKEN=your_production_twilio_token
TWILIO_PHONE_NUMBER=your_production_whatsapp_number

# Email (Production)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_production_email@gmail.com
MAIL_PASSWORD=your_production_app_password
```

### Production Docker Compose

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "80:5000"
    env_file:
      - .env.production
    depends_on:
      - db
      - redis
    volumes:
      - ./logs:/app/logs
      - ./uploads:/app/static/uploads
      - ./backups:/app/backups
    restart: always
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=hospital_crm
      - POSTGRES_USER=hospital_user
      - POSTGRES_PASSWORD=your_secure_db_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: always

  redis:
    image: redis:6-alpine
    restart: always

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web
    restart: always

volumes:
  postgres_data:
```

## 🔒 Security Considerations

### 1. Environment Variables

```bash
# Never commit these to version control
echo ".env*" >> .gitignore
echo "*.env" >> .gitignore
```

### 2. Database Security

```bash
# Use strong passwords
POSTGRES_PASSWORD=your_very_secure_password_here

# Restrict database access
# Only allow connections from web service
```

### 3. SSL/TLS Configuration

```nginx
# nginx.conf for HTTPS
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    location / {
        proxy_pass http://web:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📊 Monitoring and Logging

### Log Management

```bash
# View application logs
docker-compose logs -f web

# View database logs
docker-compose logs -f db

# Save logs to file
docker-compose logs web > app.log

# Rotate logs (add to crontab)
docker-compose logs --tail=1000 web > logs/app-$(date +%Y%m%d).log
```

### Performance Monitoring

```bash
# Monitor resource usage
docker stats

# Monitor specific container
docker stats dr_payal_web_1

# View container processes
docker-compose exec web ps aux
```

## 🚀 Scaling and Load Balancing

### Horizontal Scaling

```bash
# Scale web service to 3 instances
docker-compose up --scale web=3

# Use nginx for load balancing
# Configure upstream in nginx.conf
```

### Resource Limits

```yaml
# In docker-compose.yml
services:
  web:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

## 🔧 Troubleshooting

### Common Issues

1. **Port Already in Use**:
   ```bash
   # Check what's using port 5000
   lsof -i :5000
   # Change port in docker-compose.yml
   ports:
     - "8080:5000"  # Use port 8080 instead
   ```

2. **Database Connection Issues**:
   ```bash
   # Check database container
   docker-compose logs db
   # Restart database
   docker-compose restart db
   ```

3. **Build Failures**:
   ```bash
   # Clean build
   docker-compose build --no-cache
   # Remove old images
   docker system prune -a
   ```

4. **Permission Issues**:
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER .
   chmod -R 755 .
   ```

### Debug Mode

```bash
# Run with debug output
docker-compose up --build --verbose

# Access container shell
docker-compose exec web bash

# Check environment variables
docker-compose exec web env
```

## 📋 Backup and Recovery

### Database Backup

```bash
# Create backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec db pg_dump -U hospital_user hospital_crm > backups/backup_$DATE.sql
```

### Full System Backup

```bash
# Backup volumes
docker run --rm -v dr_payal_postgres_data:/data -v $(pwd)/backups:/backup alpine tar czf /backup/postgres_data.tar.gz -C /data .

# Backup application files
tar czf backups/app_backup_$(date +%Y%m%d).tar.gz --exclude=backups .
```

## 🎉 Success Indicators

When Docker deployment is successful:

1. ✅ All containers are running: `docker-compose ps`
2. ✅ Health check passes: `curl http://localhost:5000/health`
3. ✅ Database is accessible
4. ✅ Application loads in browser
5. ✅ Login works for all user roles
6. ✅ No error logs in `docker-compose logs`

---

## 🎉 Congratulations!

Your Dr. Payal's Hospital CRM is now running in Docker! 🐳🏥

Access it at: **http://localhost:5000**

For production deployment, remember to:
- Use strong passwords
- Enable HTTPS
- Set up monitoring
- Configure backups
- Use environment-specific configurations
