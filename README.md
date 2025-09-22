# 🏥 Hospital CRM System

A comprehensive, production-ready Hospital/Medical CRM system built with Flask for managing patients, appointments, billing, and medical records. Designed for physiotherapy clinics and medical practices.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3%2B-green.svg)](https://flask.palletsprojects.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ Features

### 👥 Patient Management
- Complete patient registration and profile management
- Medical history tracking
- Patient search and filtering
- Document management

### 📅 Appointment Scheduling
- Advanced appointment booking with calendar integration
- Multiple appointment types (Clinic, Home Visit, Online)
- Automated reminders and notifications
- Doctor availability management

### 💰 Billing System
- Comprehensive billing and payment tracking
- Multiple payment methods support
- Invoice generation
- Payment history and reports

### 🔐 User Management
- Role-based access control (Super Admin, Admin, Doctor, Staff, Patient)
- Secure authentication and authorization
- User activity tracking
- Permission management

### 📱 Communication
- **WhatsApp Integration**: Automated notifications and communication
- **AI Chatbot**: Intelligent patient assistance and query handling
- **Email Notifications**: Appointment reminders and updates

### 🌐 Online Services
- **Video Consultations**: Integrated online consultation platform
- **Patient Portal**: Self-service patient interface
- **Mobile-Responsive**: Works on all devices

### 🔍 Advanced Features
- **Audit Logging**: Complete audit trail for all user actions
- **Analytics Dashboard**: Comprehensive reporting and analytics
- **Backup System**: Automated database and file backups
- **Monitoring**: Health checks and performance monitoring
- **Security**: Advanced security features and threat protection

## 🛠 Technology Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Flask (Python 3.8+) |
| **Database** | PostgreSQL 13+ |
| **Cache/Queue** | Redis 6+ |
| **Frontend** | HTML5, CSS3, JavaScript, Bootstrap 5 |
| **Authentication** | Flask-Login, bcrypt |
| **ORM** | SQLAlchemy |
| **Task Queue** | Celery |
| **Monitoring** | Prometheus, Grafana |
| **Deployment** | Docker, Render.com |

## 🚀 Quick Start

### Option 1: Docker (Recommended)

1. **Clone the repository:**
```bash
git clone https://github.com/1981Rupal/Dr_payal.git
cd Dr_payal
```

2. **Set up environment:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start the application:**
```bash
# Production deployment
docker-compose up -d

# Development with live reload
docker-compose -f docker-compose.dev.yml up -d
```

4. **Access the application:**
- Main App: http://localhost:5000
- Grafana: http://localhost:3000 (admin/admin)
- Adminer: http://localhost:8080

### Option 2: Manual Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up database:**
```bash
python migrations_setup.py
```

3. **Run the application:**
```bash
python app.py
```

### Option 3: Render.com Deployment

1. Fork this repository
2. Connect to Render.com
3. Use the provided `render.yaml` configuration
4. Set environment variables
5. Deploy automatically

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following configuration:

```bash
# Application
SECRET_KEY=your-secret-key-here
FLASK_ENV=production
DEBUG=False

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/hospital_crm

# Redis
REDIS_URL=redis://localhost:6379/0

# WhatsApp Integration
ENABLE_WHATSAPP=true
WHATSAPP_API_KEY=your-whatsapp-api-key
WHATSAPP_API_URL=https://api.whatsapp.com

# AI Chatbot
ENABLE_CHATBOT=true
OPENAI_API_KEY=your-openai-api-key

# Email Configuration
ENABLE_EMAIL_NOTIFICATIONS=true
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# File Uploads
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216  # 16MB

# Security
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=15

# Backup (Optional)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_S3_BUCKET=your-backup-bucket
```

### Database Setup

The application supports PostgreSQL and SQLite:

```bash
# PostgreSQL (Recommended for production)
DATABASE_URL=postgresql://user:password@localhost:5432/hospital_crm

# SQLite (Development only)
DATABASE_URL=sqlite:///hospital_crm.db
```

## 📚 Documentation

- [Deployment Guide](docs/DEPLOYMENT.md) - Comprehensive deployment instructions
- [API Documentation](docs/API.md) - REST API reference
- [User Guide](docs/USER_GUIDE.md) - End-user documentation
- [Developer Guide](docs/DEVELOPER.md) - Development setup and guidelines
- [Security Guide](docs/SECURITY.md) - Security features and best practices

## 🔧 Development

### Running Tests

```bash
# Run all tests
python scripts/run_tests.py --all

# Run specific test suites
python scripts/run_tests.py --unit
python scripts/run_tests.py --api
python scripts/run_tests.py --integration

# Run with coverage
python scripts/run_tests.py --coverage
```

### Code Quality

```bash
# Linting
flake8 .

# Security scan
bandit -r .

# Dependency check
safety check
```

### Docker Management

```bash
# Use the Docker management script
./scripts/docker_manager.sh

# Available commands:
# - dev-up: Start development environment
# - prod-up: Start production environment
# - down: Stop all services
# - logs: View logs
# - backup: Create backup
# - restore: Restore from backup
```

## 🔒 Security Features

- **Authentication**: Secure login with password hashing
- **Authorization**: Role-based access control
- **CSRF Protection**: Cross-site request forgery prevention
- **XSS Protection**: Cross-site scripting prevention
- **SQL Injection Prevention**: Parameterized queries
- **Rate Limiting**: Brute force attack prevention
- **Audit Logging**: Complete activity tracking
- **Security Headers**: Comprehensive security headers
- **File Upload Security**: Safe file handling

## 📊 Monitoring & Analytics

### Health Checks
- Database connectivity
- Redis connectivity
- External service status
- System resource usage

### Metrics
- Request/response metrics
- Error rates
- Performance metrics
- Business metrics

### Logging
- Structured JSON logging
- Security event logging
- Performance logging
- Audit trail logging

## 🚀 Deployment Options

### 1. Docker Deployment
- Production-ready containers
- Multi-stage builds
- Health checks
- Monitoring stack included

### 2. Render.com Deployment
- One-click deployment
- Automatic scaling
- Managed database
- SSL certificates

### 3. Traditional Server Deployment
- Systemd service files
- Nginx configuration
- SSL setup
- Backup scripts

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📧 Email: support@hospitalcrm.com
- 🐛 Issues: [GitHub Issues](https://github.com/1981Rupal/Dr_payal/issues)
- 📖 Documentation: [Wiki](https://github.com/1981Rupal/Dr_payal/wiki)
- 💬 Discussions: [GitHub Discussions](https://github.com/1981Rupal/Dr_payal/discussions)

## 🙏 Acknowledgments

- Flask community for the excellent framework
- Bootstrap team for the UI components
- All contributors who have helped improve this project

---

**Made with ❤️ for healthcare professionals**