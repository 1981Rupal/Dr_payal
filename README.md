# 🏥 Dr. Payal's Physiotherapy Clinic - Complete Hospital CRM System

A comprehensive, production-ready Hospital Customer Relationship Management (CRM) system built with Flask for managing patients, appointments, billing, and medical records. Designed specifically for physiotherapy clinics and medical practices.

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Table of Contents

1. [Features Overview](#-features-overview)
2. [System Architecture](#-system-architecture)
3. [Module Documentation](#-module-documentation)
4. [User Manual](#-user-manual)
5. [Installation & Setup](#-installation--setup)
6. [Local Development](#-local-development)
7. [Docker Deployment](#-docker-deployment)
8. [Render.com Deployment](#-rendercom-deployment)
9. [Configuration Guide](#-configuration-guide)
10. [API Documentation](#-api-documentation)
11. [Database Schema](#-database-schema)
12. [Security Features](#-security-features)
13. [Customization Guide](#-customization-guide)
14. [Troubleshooting](#-troubleshooting)
15. [Contributing](#-contributing)

## ✨ Features Overview

### 👥 User Management System
- **Multi-role authentication**: Super Admin, Admin, Doctor, Staff, Patient
- **Secure password hashing** with bcrypt
- **Role-based access control** (RBAC)
- **Session management** with Flask-Login
- **User activity tracking** and audit logs
- **Profile management** with contact information

### 🏥 Patient Management
- **Complete patient registration** with detailed medical information
- **Patient search and filtering** by name, ID, phone, email
- **Medical history tracking** with visit records
- **Document management** for patient files
- **Emergency contact information**
- **Patient visit history** and treatment records
- **Patient portal** for self-service access

### 📅 Appointment System
- **Advanced appointment scheduling** with calendar integration
- **Multiple appointment types**: Clinic, Home Visit, Online Consultation
- **Doctor availability management**
- **Appointment conflict detection**
- **Automated reminders** via WhatsApp/SMS (optional)
- **Appointment status tracking**: Pending, Confirmed, Completed, Cancelled, No-Show
- **Recurring appointments** support
- **Online consultation** integration

### 💰 Billing & Payment System
- **Comprehensive billing management**
- **Multiple payment methods**: Cash, Card, UPI, Bank Transfer
- **Invoice generation** with PDF export
- **Payment tracking** and history
- **Outstanding balance management**
- **Treatment packages** and pricing
- **Payment receipts** and reports
- **Partial payment** support

### 📊 Reports & Analytics
- **Dashboard with key metrics**
- **Patient statistics** and demographics
- **Appointment analytics** and trends
- **Revenue reports** and financial insights
- **Treatment effectiveness** tracking
- **Export capabilities** (PDF, Excel)
- **Custom date range** filtering

### 🤖 AI & Communication Features
- **Intelligent chatbot** for patient queries (optional)
- **WhatsApp integration** for notifications (optional)
- **Email notifications** for appointments and billing
- **SMS reminders** for appointments
- **Automated appointment suggestions**
- **Treatment recommendations** based on history

### 🔒 Security & Compliance
- **HIPAA-compliant** data handling
- **Encrypted data storage** and transmission
- **Audit trails** for all user actions
- **Role-based data access** controls
- **Session security** with secure cookies
- **Input validation** and sanitization
- **CSRF protection** in production

## 🏗️ System Architecture

### Core Components

```
Dr_payal/
├── app.py                    # Main Flask application factory
├── wsgi.py                   # WSGI entry point for production
├── run_local.py             # Local development server
├── models.py                # SQLAlchemy database models
├── config.py                # Configuration management
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── routes/                 # Application routes (blueprints)
│   ├── __init__.py
│   ├── auth.py            # Authentication routes
│   ├── main.py            # Dashboard and main routes
│   ├── patients.py        # Patient management routes
│   ├── appointments.py    # Appointment system routes
│   ├── billing.py         # Billing and payment routes
│   └── api.py             # REST API endpoints
├── services/              # Business logic layer
│   ├── __init__.py
│   ├── appointment_service.py  # Appointment business logic
│   ├── billing_service.py     # Billing calculations
│   ├── chatbot_service.py     # AI chatbot functionality
│   └── whatsapp_service.py    # WhatsApp integration
├── utils/                 # Utility functions
│   ├── backup_system.py   # Database backup utilities
│   ├── logging_config.py  # Logging configuration
│   ├── monitoring.py      # Health monitoring
│   └── security.py        # Security utilities
├── templates/             # Jinja2 HTML templates
│   ├── base.html          # Base template
│   ├── auth/              # Authentication templates
│   ├── dashboard/         # Dashboard templates
│   ├── patients/          # Patient management templates
│   ├── appointments/      # Appointment templates
│   ├── billing/           # Billing templates
│   ├── reports/           # Report templates
│   ├── settings/          # Settings templates
│   ├── users/             # User management templates
│   └── errors/            # Error page templates
├── static/                # Static files
│   ├── css/               # Stylesheets
│   ├── js/                # JavaScript files
│   └── images/            # Image assets
├── tests/                 # Test suite
│   ├── conftest.py        # Test configuration
│   ├── test_models.py     # Model tests
│   ├── test_auth.py       # Authentication tests
│   ├── test_api.py        # API tests
│   └── test_integration.py # Integration tests
├── scripts/               # Deployment scripts
│   ├── health_check.py    # Health check script
│   └── init-db.sql        # Database initialization
├── docs/                  # Documentation
│   ├── API.md             # API documentation
│   └── DEPLOYMENT.md      # Deployment guide
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose setup
├── render.yaml            # Render.com deployment config
├── Procfile               # Heroku deployment config
└── HOSTING_GUIDE.md       # Complete hosting guide
```

### Technology Stack

- **Backend**: Flask 3.0, Python 3.11+
- **Database**: SQLAlchemy ORM with PostgreSQL/SQLite
- **Authentication**: Flask-Login with bcrypt password hashing
- **Frontend**: Bootstrap 5, Jinja2 templates, JavaScript
- **API**: RESTful API with JSON responses
- **Deployment**: Docker, Gunicorn, Nginx (optional)
- **Monitoring**: Health checks, logging, audit trails
- **Integrations**: Twilio (WhatsApp/SMS), OpenAI (Chatbot)

## 📚 Module Documentation

### Core Application Modules

#### 1. **app.py** - Main Application Factory
The main Flask application factory that initializes the app, database, authentication, and registers all blueprints.

**Key Functions:**
- `create_app()`: Creates and configures Flask application
- `create_default_data()`: Sets up default users and system data
- `register_error_handlers()`: Handles 404/500 errors
- `create_basic_routes()`: Fallback routes if blueprints fail

**Default Users Created:**
- Super Admin: `superadmin` / `admin123`
- Doctor: `doctor` / `doctor123`
- Staff: `staff` / `staff123`

#### 2. **models.py** - Database Models
Comprehensive SQLAlchemy models for all system entities.

**Core Models:**
- **User**: System users with role-based access
- **Patient**: Patient information and medical records
- **Appointment**: Appointment scheduling and management
- **Visit**: Patient visit records and treatments
- **Billing**: Invoice and billing management
- **Payment**: Payment tracking and history
- **Prescription**: Medication prescriptions
- **TreatmentPackage**: Treatment packages and pricing
- **OnlineConsultation**: Video consultation records
- **AuditLog**: System activity tracking
- **ChatbotConversation**: AI chatbot interactions
- **WhatsAppMessage**: WhatsApp message logs

**Enums:**
- `UserRole`: SUPER_ADMIN, ADMIN, DOCTOR, STAFF, PATIENT
- `AppointmentStatus`: PENDING, CONFIRMED, CANCELLED, COMPLETED, NO_SHOW
- `PaymentStatus`: PENDING, PARTIAL, PAID, REFUNDED, CANCELLED
- `VisitType`: CLINIC, HOME, ONLINE, EMERGENCY

#### 3. **config.py** - Configuration Management
Environment-based configuration for different deployment scenarios.

**Configuration Classes:**
- `Config`: Base configuration
- `DevelopmentConfig`: Local development settings
- `ProductionConfig`: Production deployment settings
- `TestingConfig`: Testing environment settings
- `RenderConfig`: Render.com specific settings

### Route Modules (Blueprints)

#### 1. **routes/auth.py** - Authentication System
Handles user login, logout, registration, and password management.

**Routes:**
- `POST /auth/login`: User authentication
- `GET /auth/logout`: User logout
- `GET|POST /auth/register`: User registration (admin only)
- `GET|POST /auth/change-password`: Password change
- `GET|POST /auth/reset-password`: Password reset

**Features:**
- Secure password hashing with bcrypt
- Session management with Flask-Login
- Failed login attempt tracking
- Audit logging for security events

#### 2. **routes/main.py** - Dashboard & Main Routes
Main dashboard and core application routes.

**Routes:**
- `GET /`: Home page (redirects to dashboard)
- `GET /dashboard`: Main dashboard with statistics
- `GET /search`: Global search functionality

**Dashboard Features:**
- Role-based statistics display
- Recent activity tracking
- Quick action buttons
- Performance metrics

#### 3. **routes/patients.py** - Patient Management
Complete patient lifecycle management.

**Routes:**
- `GET /patients/`: List all patients with search/filter
- `GET /patients/new`: New patient registration form
- `POST /patients/create`: Create new patient
- `GET /patients/<id>`: View patient details
- `GET /patients/<id>/edit`: Edit patient form
- `POST /patients/<id>/update`: Update patient information
- `POST /patients/<id>/delete`: Soft delete patient
- `GET /patients/<id>/visits`: Patient visit history
- `POST /patients/<id>/visits/new`: Add new visit record

**Features:**
- Advanced search and filtering
- Medical history tracking
- Visit record management
- Document upload support
- Patient portal access

#### 4. **routes/appointments.py** - Appointment System
Comprehensive appointment scheduling and management.

**Routes:**
- `GET /appointments/`: List appointments with filters
- `GET /appointments/calendar`: Calendar view
- `GET /appointments/new`: New appointment form
- `POST /appointments/create`: Create appointment
- `GET /appointments/<id>`: View appointment details
- `GET /appointments/<id>/edit`: Edit appointment
- `POST /appointments/<id>/update`: Update appointment
- `POST /appointments/<id>/confirm`: Confirm appointment
- `POST /appointments/<id>/cancel`: Cancel appointment
- `POST /appointments/<id>/complete`: Mark as completed

**Features:**
- Calendar integration
- Conflict detection
- Multiple appointment types
- Automated reminders
- Online consultation setup
- Recurring appointments

#### 5. **routes/billing.py** - Billing & Payment System
Financial management and billing operations.

**Routes:**
- `GET /billing/`: List all invoices
- `GET /billing/new`: Create new invoice
- `POST /billing/create`: Process new invoice
- `GET /billing/<id>`: View invoice details
- `POST /billing/<id>/payment`: Record payment
- `GET /billing/packages`: Treatment packages
- `POST /billing/packages/create`: Create package
- `GET /billing/reports`: Financial reports

**Features:**
- Invoice generation
- Payment tracking
- Treatment packages
- Financial reporting
- Multiple payment methods
- Partial payment support

#### 6. **routes/api.py** - REST API Endpoints
RESTful API for external integrations and mobile apps.

**API Endpoints:**
- `GET /api/patients`: List patients
- `GET /api/patients/<id>`: Get patient details
- `POST /api/patients`: Create patient
- `PUT /api/patients/<id>`: Update patient
- `GET /api/appointments`: List appointments
- `POST /api/appointments`: Create appointment
- `GET /api/billing`: List invoices
- `POST /api/billing`: Create invoice
- `GET /api/dashboard/stats`: Dashboard statistics
- `GET /api/search`: Global search

**Features:**
- JSON responses
- Authentication required
- Error handling
- Pagination support
- Role-based access control

### Service Modules (Business Logic)

#### 1. **services/appointment_service.py** - Appointment Business Logic
Core appointment management functionality.

**Key Methods:**
- `create_appointment()`: Create new appointment with validation
- `confirm_appointment()`: Confirm pending appointment
- `cancel_appointment()`: Cancel appointment with reason
- `reschedule_appointment()`: Reschedule existing appointment
- `get_available_slots()`: Get available time slots
- `is_valid_appointment_time()`: Validate appointment timing
- `send_reminder()`: Send appointment reminders
- `create_online_consultation()`: Setup video consultation

#### 2. **services/billing_service.py** - Billing Calculations
Financial calculations and billing logic.

**Key Methods:**
- `calculate_bill()`: Calculate total bill amount
- `apply_discount()`: Apply discounts and offers
- `process_payment()`: Process payment transactions
- `generate_invoice()`: Generate PDF invoices
- `calculate_package_pricing()`: Treatment package calculations
- `get_outstanding_balance()`: Calculate pending amounts

#### 3. **services/chatbot_service.py** - AI Chatbot
Intelligent chatbot for patient assistance.

**Key Methods:**
- `process_message()`: Process user messages
- `detect_intent()`: Identify user intent
- `generate_response()`: Generate AI responses
- `book_appointment()`: Chatbot appointment booking
- `get_patient_info()`: Retrieve patient information
- `handle_medical_query()`: Handle medical questions

#### 4. **services/whatsapp_service.py** - WhatsApp Integration
WhatsApp messaging and notifications.

**Key Methods:**
- `send_message()`: Send WhatsApp messages
- `send_appointment_reminder()`: Appointment reminders
- `send_payment_reminder()`: Payment notifications
- `handle_incoming_message()`: Process incoming messages
- `verify_webhook()`: Webhook verification

### Utility Modules

#### 1. **utils/security.py** - Security Utilities
Security-related helper functions.

**Functions:**
- `generate_secure_token()`: Generate secure tokens
- `validate_input()`: Input validation and sanitization
- `check_permissions()`: Role-based permission checking
- `log_security_event()`: Security event logging

#### 2. **utils/backup_system.py** - Backup Management
Database and file backup utilities.

**Functions:**
- `create_database_backup()`: Database backup
- `restore_database()`: Database restoration
- `backup_files()`: File system backup
- `schedule_backups()`: Automated backup scheduling

#### 3. **utils/monitoring.py** - Health Monitoring
System health and performance monitoring.

**Functions:**
- `check_database_health()`: Database connectivity check
- `check_disk_space()`: Disk space monitoring
- `check_memory_usage()`: Memory usage tracking
- `generate_health_report()`: System health report

#### 4. **utils/logging_config.py** - Logging Configuration
Centralized logging configuration.

**Functions:**
- `setup_logging()`: Configure logging
- `log_user_action()`: User activity logging
- `log_error()`: Error logging
- `log_performance()`: Performance metrics logging

## 👤 User Manual

### Getting Started

#### First Time Login
1. Access the application at your deployment URL
2. Use default credentials:
   - **Super Admin**: `superadmin` / `admin123`
   - **Doctor**: `doctor` / `doctor123`
   - **Staff**: `staff` / `staff123`
3. **Important**: Change default passwords immediately after first login

#### Dashboard Overview
The dashboard provides a comprehensive overview of your clinic operations:

**Super Admin/Admin Dashboard:**
- Total active patients
- Today's appointments
- Pending appointments
- Monthly revenue
- Pending payments
- Recent activities

**Doctor Dashboard:**
- My appointments today
- My patients
- Pending consultations
- Recent patient visits

**Staff Dashboard:**
- Today's appointments
- Patient check-ins
- Billing tasks
- Appointment scheduling

### User Role Management

#### Super Admin Capabilities
- **Full system access** to all modules
- **User management**: Create, edit, delete users
- **System configuration**: Modify settings and preferences
- **Financial oversight**: Access all financial reports
- **Audit access**: View all system logs and activities
- **Backup management**: Create and restore backups

#### Admin Capabilities
- **Patient management**: Full patient lifecycle
- **Appointment management**: Schedule and manage appointments
- **Billing operations**: Create invoices and process payments
- **Staff management**: Manage staff users
- **Reports access**: Generate and view reports

#### Doctor Capabilities
- **Patient care**: View and update patient records
- **Appointment management**: Manage own appointments
- **Prescription writing**: Create and manage prescriptions
- **Consultation notes**: Add visit notes and diagnoses
- **Treatment planning**: Create treatment plans

#### Staff Capabilities
- **Patient registration**: Register new patients
- **Appointment scheduling**: Book and manage appointments
- **Basic billing**: Create invoices and record payments
- **Reception duties**: Check-in patients and manage queues

#### Patient Capabilities (Patient Portal)
- **View appointments**: See upcoming and past appointments
- **Medical records**: Access own medical history
- **Prescription access**: View current prescriptions
- **Payment history**: View billing and payment records

### Patient Management Guide

#### Registering New Patients
1. Navigate to **Patients** → **New Patient**
2. Fill in required information:
   - Personal details (name, DOB, gender)
   - Contact information (phone, email, address)
   - Emergency contact details
   - Medical history and allergies
3. Click **Save Patient** to create record

#### Managing Patient Records
1. **Search patients**: Use the search bar to find patients by name, ID, or phone
2. **View patient details**: Click on patient name to view complete profile
3. **Edit information**: Use the **Edit** button to update patient details
4. **Add visit records**: Document each patient visit with:
   - Date and time of visit
   - Symptoms and complaints
   - Diagnosis and treatment
   - Prescribed medications
   - Follow-up instructions

#### Patient Visit Workflow
1. **Check-in**: Mark patient as arrived for appointment
2. **Consultation**: Doctor adds visit notes and diagnosis
3. **Treatment**: Record treatment provided
4. **Prescription**: Add medications if needed
5. **Billing**: Generate invoice for services
6. **Follow-up**: Schedule next appointment if required

### Appointment Management Guide

#### Scheduling Appointments
1. Navigate to **Appointments** → **New Appointment**
2. Select patient (or create new patient)
3. Choose appointment details:
   - Doctor assignment
   - Date and time
   - Appointment type (Clinic/Home/Online)
   - Reason for visit
4. Check for conflicts and confirm booking

#### Appointment Types
- **Clinic Visit**: In-person consultation at clinic
- **Home Visit**: Doctor visits patient at home
- **Online Consultation**: Video call consultation
- **Emergency**: Urgent medical attention

#### Managing Appointment Status
- **Pending**: Newly created, awaiting confirmation
- **Confirmed**: Appointment confirmed by staff/doctor
- **Completed**: Patient visited and consultation done
- **Cancelled**: Appointment cancelled by patient/clinic
- **No Show**: Patient didn't arrive for appointment

#### Calendar View
- **Monthly view**: See all appointments for the month
- **Weekly view**: Detailed week view with time slots
- **Daily view**: Hour-by-hour schedule for selected day
- **Doctor filter**: View appointments for specific doctors

### Billing & Payment Guide

#### Creating Invoices
1. Navigate to **Billing** → **New Invoice**
2. Select patient and visit
3. Add services and treatments:
   - Consultation fees
   - Treatment charges
   - Medication costs
   - Equipment usage
4. Apply discounts if applicable
5. Generate and save invoice

#### Processing Payments
1. Open invoice from billing list
2. Click **Record Payment**
3. Enter payment details:
   - Amount received
   - Payment method (Cash/Card/UPI/Bank Transfer)
   - Transaction reference
   - Payment date
4. Save payment record

#### Treatment Packages
1. **Create packages**: Define treatment packages with multiple sessions
2. **Package pricing**: Set discounted rates for package deals
3. **Session tracking**: Track used and remaining sessions
4. **Package renewal**: Extend or renew expired packages

#### Financial Reports
- **Daily collections**: Daily payment summary
- **Monthly revenue**: Monthly financial overview
- **Outstanding payments**: Pending payment reports
- **Doctor-wise revenue**: Revenue by doctor
- **Service-wise analysis**: Popular services and treatments

### Communication Features

#### WhatsApp Integration (Optional)
- **Appointment reminders**: Automated reminders 24 hours before appointment
- **Payment notifications**: Payment due and received notifications
- **General updates**: Clinic announcements and health tips

#### Email Notifications (Optional)
- **Appointment confirmations**: Email confirmation after booking
- **Invoice delivery**: Email invoices to patients
- **Password reset**: Secure password reset emails

#### AI Chatbot (Optional)
- **Patient queries**: Answer common patient questions
- **Appointment booking**: Allow patients to book appointments via chat
- **Information retrieval**: Provide clinic information and services
- **Symptom checker**: Basic symptom assessment and advice

### Reports & Analytics

#### Patient Reports
- **Patient demographics**: Age, gender, location analysis
- **New patient trends**: Patient acquisition over time
- **Patient retention**: Return visit analysis
- **Medical conditions**: Common diagnoses and treatments

#### Appointment Reports
- **Appointment volume**: Daily, weekly, monthly appointment counts
- **Doctor utilization**: Doctor-wise appointment analysis
- **Appointment types**: Distribution of visit types
- **Cancellation rates**: Appointment cancellation analysis

#### Financial Reports
- **Revenue analysis**: Income trends and patterns
- **Payment methods**: Preferred payment options
- **Outstanding amounts**: Pending payment tracking
- **Profitability**: Service-wise profit analysis

#### Operational Reports
- **Staff performance**: User activity and productivity
- **System usage**: Feature utilization statistics
- **Peak hours**: Busy times and resource planning
- **Patient satisfaction**: Feedback and ratings analysis

## 🚀 Installation & Setup

### Prerequisites
- **Python 3.11 or higher**
- **Git** for version control
- **Virtual environment** (recommended)
- **PostgreSQL** (for production) or **SQLite** (for development)
- **Redis** (optional, for advanced features)
- **Docker & Docker Compose** (for containerized deployment)

### System Requirements
- **RAM**: Minimum 2GB, Recommended 4GB+
- **Storage**: Minimum 5GB free space
- **OS**: Linux, macOS, or Windows
- **Network**: Internet connection for external integrations

## 🖥️ Local Development

### Quick Start (Recommended)
```bash
# 1. Clone the repository
git clone https://github.com/1981Rupal/Dr_payal.git
cd Dr_payal

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the application
python run_local.py
```

### Detailed Setup Process

#### Step 1: Environment Setup
```bash
# Create and activate virtual environment
python -m venv hospital_crm_env
source hospital_crm_env/bin/activate  # Linux/Mac
# OR
hospital_crm_env\Scripts\activate     # Windows

# Upgrade pip
pip install --upgrade pip
```

#### Step 2: Install Dependencies
```bash
# Install all required packages
pip install -r requirements.txt

# Verify installation
python -c "import flask; print('Flask installed successfully')"
```

#### Step 3: Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env file (optional for basic setup)
nano .env  # Linux/Mac
# OR
notepad .env  # Windows
```

**Basic .env configuration for local development:**
```env
# Basic Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=True

# Database (SQLite for local development)
DATABASE_URL=sqlite:///hospital_crm.db

# Clinic Information
CLINIC_NAME=Dr. Payal's Physiotherapy Clinic
CLINIC_PHONE=+1234567890
CLINIC_EMAIL=info@drpayal.com

# Feature Flags (disabled by default)
ENABLE_WHATSAPP=False
ENABLE_CHATBOT=False
ENABLE_EMAIL_NOTIFICATIONS=False
```

#### Step 4: Database Initialization
```bash
# The application will automatically create the database
# and default users when you first run it
python run_local.py
```

#### Step 5: Access the Application
- Open your browser and navigate to: `http://localhost:5000`
- Login with default credentials:
  - **Super Admin**: `superadmin` / `admin123`
  - **Doctor**: `doctor` / `doctor123`
  - **Staff**: `staff` / `staff123`

### Development Tools

#### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-flask pytest-cov

# Run all tests
python -m pytest

# Run tests with coverage
python -m pytest --cov=app --cov-report=html

# Run specific test file
python -m pytest tests/test_models.py

# Run tests in verbose mode
python -m pytest -v
```

#### Code Quality Tools
```bash
# Install development tools
pip install black flake8 isort

# Format code with Black
black .

# Check code style with flake8
flake8 app.py routes/ services/ utils/

# Sort imports with isort
isort .
```

#### Database Management
```bash
# Access SQLite database directly
sqlite3 hospital_crm.db

# View tables
.tables

# View table schema
.schema users

# Exit SQLite
.quit
```

### Development Workflow

#### Making Changes
1. **Create feature branch**: `git checkout -b feature/new-feature`
2. **Make changes**: Edit code files
3. **Test changes**: Run tests and manual testing
4. **Commit changes**: `git commit -m "Add new feature"`
5. **Push changes**: `git push origin feature/new-feature`

#### Adding New Features
1. **Models**: Add new database models in `models.py`
2. **Routes**: Create new routes in appropriate blueprint
3. **Services**: Add business logic in `services/` directory
4. **Templates**: Create HTML templates in `templates/`
5. **Tests**: Write tests for new functionality

#### Debugging
```bash
# Run with debug mode
export FLASK_DEBUG=1
python app.py

# View logs
tail -f logs/app.log

# Database debugging
export SQLALCHEMY_ECHO=1
python app.py
```

## 🐳 Docker Deployment

### Quick Docker Setup
```bash
# Clone repository
git clone https://github.com/1981Rupal/Dr_payal.git
cd Dr_payal

# Start with Docker Compose
docker-compose up --build

# Access application at http://localhost:5000
```

### Detailed Docker Deployment

#### Step 1: Prerequisites
```bash
# Install Docker and Docker Compose
# Ubuntu/Debian:
sudo apt update
sudo apt install docker.io docker-compose

# CentOS/RHEL:
sudo yum install docker docker-compose

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker
```

#### Step 2: Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit environment variables for Docker
nano .env
```

**Docker .env configuration:**
```env
# Database Configuration
POSTGRES_DB=hospital_crm
POSTGRES_USER=hospital_user
POSTGRES_PASSWORD=hospital_password_2024

# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-super-secret-production-key

# Database URL for Docker
DATABASE_URL=postgresql://hospital_user:hospital_password_2024@db:5432/hospital_crm

# Feature Flags
ENABLE_WHATSAPP=False
ENABLE_CHATBOT=False
ENABLE_EMAIL_NOTIFICATIONS=False
```

#### Step 3: Build and Deploy
```bash
# Build and start all services
docker-compose up --build -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

#### Step 4: Database Setup
```bash
# The database will be automatically initialized
# Check if initialization was successful
docker-compose logs app | grep "Database initialized"
```

#### Step 5: Access Application
- **Application**: http://localhost:5000
- **Database**: localhost:5432 (if you need direct access)

### Docker Management Commands

#### Service Management
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart specific service
docker-compose restart app

# View service logs
docker-compose logs app
docker-compose logs db

# Execute commands in container
docker-compose exec app bash
docker-compose exec db psql -U hospital_user -d hospital_crm
```

#### Database Operations
```bash
# Create database backup
docker-compose exec db pg_dump -U hospital_user hospital_crm > backup.sql

# Restore database backup
docker-compose exec -T db psql -U hospital_user hospital_crm < backup.sql

# Access database shell
docker-compose exec db psql -U hospital_user -d hospital_crm
```

#### Maintenance
```bash
# Update application
git pull origin main
docker-compose down
docker-compose up --build -d

# Clean up unused containers and images
docker system prune -a

# View disk usage
docker system df
```

### Production Docker Setup

#### Step 1: Production Environment
```bash
# Create production environment file
cp .env.example .env.production

# Edit with production values
nano .env.production
```

#### Step 2: SSL Configuration (Optional)
```bash
# Create SSL certificates directory
mkdir -p ssl

# Copy your SSL certificates
cp your-cert.pem ssl/
cp your-key.pem ssl/
```

#### Step 3: Production Deployment
```bash
# Deploy with production settings
docker-compose -f docker-compose.yml --env-file .env.production up -d

# Monitor deployment
docker-compose logs -f app

## ☁️ Render.com Deployment

### Quick Render Deployment
1. **Fork the repository** to your GitHub account
2. **Sign up** for Render.com account
3. **Create PostgreSQL database** on Render
4. **Create Web Service** connected to your GitHub repo
5. **Configure environment variables**
6. **Deploy** and access your application

### Detailed Render.com Setup

#### Step 1: Prepare Repository
```bash
# Fork the repository on GitHub
# Clone your fork locally
git clone https://github.com/YOUR_USERNAME/Dr_payal.git
cd Dr_payal

# Make any necessary changes
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

#### Step 2: Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub account
3. Verify your email address

#### Step 3: Create PostgreSQL Database
1. **Click "New +"** → **"PostgreSQL"**
2. **Configure database**:
   - **Name**: `hospital-crm-db`
   - **Database**: `hospital_crm`
   - **User**: `hospital_user`
   - **Region**: Choose closest to your users
   - **Plan**: Free or Starter (based on needs)
3. **Create database** and note the connection details

#### Step 4: Create Web Service
1. **Click "New +"** → **"Web Service"**
2. **Connect repository**:
   - Select your GitHub account
   - Choose the forked `Dr_payal` repository
3. **Configure service**:
   - **Name**: `hospital-crm`
   - **Environment**: `Python 3`
   - **Region**: Same as database
   - **Branch**: `main`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 wsgi:app`

#### Step 5: Environment Variables
Add these environment variables in Render dashboard:

**Required Variables:**
```env
FLASK_ENV=production
SECRET_KEY=your-super-secret-production-key-here
DATABASE_URL=[Auto-filled by Render from database connection]
```

**Optional Variables:**
```env
# Clinic Information
CLINIC_NAME=Dr. Payal's Physiotherapy Clinic
CLINIC_PHONE=+1234567890
CLINIC_EMAIL=info@drpayal.com

# File Upload Settings
UPLOAD_FOLDER=/opt/render/project/src/uploads
MAX_CONTENT_LENGTH=16777216

# Security Settings
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax
WTF_CSRF_ENABLED=true
PREFERRED_URL_SCHEME=https

# Feature Flags (enable as needed)
ENABLE_WHATSAPP=false
ENABLE_CHATBOT=false
ENABLE_EMAIL_NOTIFICATIONS=false
ENABLE_PAYMENT_GATEWAY=false

# External Service Keys (add if enabling features)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
OPENAI_API_KEY=your_openai_api_key
MAIL_SERVER=smtp.gmail.com
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
```

#### Step 6: Deploy Application
1. **Click "Create Web Service"**
2. **Wait for deployment** (usually 5-10 minutes)
3. **Monitor build logs** for any errors
4. **Access application** at provided Render URL

#### Step 7: Post-Deployment Setup
1. **Access your application** at the Render URL
2. **Login with default credentials**:
   - Super Admin: `superadmin` / `admin123`
3. **Change default passwords** immediately
4. **Configure clinic settings**
5. **Test all functionality**

### Render.com Management

#### Monitoring Deployment
```bash
# View deployment logs in Render dashboard
# Or use Render CLI (if installed)
render logs --service hospital-crm
```

#### Updating Application
```bash
# Make changes locally
git add .
git commit -m "Update application"
git push origin main

# Render will automatically redeploy
```

#### Database Management
```bash
# Connect to Render PostgreSQL (from local machine)
psql postgresql://username:password@hostname:port/database

# Create backup
pg_dump postgresql://username:password@hostname:port/database > backup.sql

# Restore backup
psql postgresql://username:password@hostname:port/database < backup.sql
```

#### Custom Domain Setup
1. **Go to service settings** in Render dashboard
2. **Add custom domain** (e.g., clinic.yourdomain.com)
3. **Configure DNS** with your domain provider:
   - Add CNAME record pointing to Render URL
4. **SSL certificate** will be automatically provisioned

### Render.com Best Practices

#### Performance Optimization
- **Use Starter plan** or higher for production
- **Enable persistent disk** for file uploads
- **Configure health checks** for reliability
- **Monitor resource usage** in dashboard

#### Security Considerations
- **Use strong SECRET_KEY** (generate with `python -c "import secrets; print(secrets.token_hex(32))"`)
- **Enable HTTPS** (automatic with custom domain)
- **Secure environment variables** (never commit to git)
- **Regular security updates** (keep dependencies updated)

#### Backup Strategy
- **Database backups**: Use Render's backup feature or manual pg_dump
- **File backups**: Consider external storage for uploaded files
- **Configuration backup**: Keep environment variables documented

## ⚙️ Configuration Guide

### Environment Variables Reference

#### Core Configuration
```env
# Flask Settings
SECRET_KEY=your-secret-key-here                    # Required: Secure random key
FLASK_ENV=development|production                   # Environment mode
FLASK_DEBUG=True|False                            # Debug mode (development only)

# Database Settings
DATABASE_URL=sqlite:///hospital_crm.db            # SQLite for development
DATABASE_URL=postgresql://user:pass@host:port/db  # PostgreSQL for production

# Application Settings
UPLOAD_FOLDER=uploads                             # File upload directory
MAX_CONTENT_LENGTH=16777216                       # Max file size (16MB)
```

#### Security Settings
```env
# Session Security
SESSION_COOKIE_SECURE=True|False                  # HTTPS only cookies
SESSION_COOKIE_HTTPONLY=True                      # Prevent XSS
SESSION_COOKIE_SAMESITE=Lax|Strict|None          # CSRF protection
WTF_CSRF_ENABLED=True|False                       # CSRF protection

# Password Security
PASSWORD_MIN_LENGTH=8                             # Minimum password length
PASSWORD_REQUIRE_UPPERCASE=True                   # Require uppercase letters
PASSWORD_REQUIRE_NUMBERS=True                     # Require numbers
PASSWORD_REQUIRE_SYMBOLS=True                     # Require special characters
```

#### Clinic Configuration
```env
# Clinic Information
CLINIC_NAME=Dr. Payal's Physiotherapy Clinic     # Clinic name
CLINIC_ADDRESS=123 Health Street, Medical City    # Clinic address
CLINIC_PHONE=+1234567890                          # Contact phone
CLINIC_EMAIL=info@drpayal.com                     # Contact email

# Operating Hours
WORKING_HOURS_START=09:00                         # Start time
WORKING_HOURS_END=18:00                           # End time
WORKING_DAYS=Monday,Tuesday,Wednesday,Thursday,Friday,Saturday  # Working days
DEFAULT_APPOINTMENT_DURATION=30                   # Default appointment length (minutes)
```

#### Feature Flags
```env
# Core Features
ENABLE_PATIENT_PORTAL=True|False                  # Patient self-service portal
ENABLE_ONLINE_BOOKING=True|False                  # Online appointment booking
ENABLE_MULTI_LOCATION=True|False                  # Multiple clinic locations

# Communication Features
ENABLE_WHATSAPP=True|False                        # WhatsApp integration
ENABLE_SMS_NOTIFICATIONS=True|False               # SMS notifications
ENABLE_EMAIL_NOTIFICATIONS=True|False             # Email notifications
ENABLE_PUSH_NOTIFICATIONS=True|False              # Web push notifications

# Advanced Features
ENABLE_CHATBOT=True|False                         # AI chatbot
ENABLE_ONLINE_CONSULTATION=True|False             # Video consultations
ENABLE_PAYMENT_GATEWAY=True|False                 # Online payments
ENABLE_INVENTORY_MANAGEMENT=True|False            # Medicine inventory
ENABLE_LABORATORY_INTEGRATION=True|False          # Lab test integration
```

#### External Service Configuration

**WhatsApp/SMS (Twilio)**
```env
TWILIO_ACCOUNT_SID=your_account_sid               # Twilio Account SID
TWILIO_AUTH_TOKEN=your_auth_token                 # Twilio Auth Token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886      # WhatsApp Business number
TWILIO_SMS_NUMBER=+1234567890                     # SMS sender number
```

**Email Configuration**
```env
MAIL_SERVER=smtp.gmail.com                        # SMTP server
MAIL_PORT=587                                     # SMTP port
MAIL_USE_TLS=True                                 # Use TLS encryption
MAIL_USE_SSL=False                                # Use SSL encryption
MAIL_USERNAME=your_email@gmail.com                # Email username
MAIL_PASSWORD=your_app_password                   # Email password/app password
MAIL_DEFAULT_SENDER=noreply@drpayal.com          # Default sender email
```

**AI Chatbot (OpenAI)**
```env
OPENAI_API_KEY=your_openai_api_key                # OpenAI API key
OPENAI_MODEL=gpt-3.5-turbo                        # AI model to use
OPENAI_MAX_TOKENS=150                             # Max response tokens
CHATBOT_WELCOME_MESSAGE=Hello! How can I help you today?  # Welcome message
```

**Payment Gateways**
```env
# Razorpay (India)
RAZORPAY_KEY_ID=your_razorpay_key_id              # Razorpay Key ID
RAZORPAY_KEY_SECRET=your_razorpay_key_secret      # Razorpay Secret

# Stripe (International)
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key # Stripe Publishable Key
STRIPE_SECRET_KEY=your_stripe_secret_key          # Stripe Secret Key
STRIPE_WEBHOOK_SECRET=your_webhook_secret         # Webhook secret
```

**Cloud Storage (AWS S3)**
```env
AWS_ACCESS_KEY_ID=your_aws_access_key             # AWS Access Key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key         # AWS Secret Key
AWS_S3_BUCKET=your_s3_bucket_name                 # S3 Bucket name
AWS_REGION=us-east-1                              # AWS Region
S3_UPLOAD_FOLDER=uploads                          # S3 folder for uploads
```

**Monitoring & Logging**
```env
# Sentry Error Tracking
SENTRY_DSN=your_sentry_dsn_url                    # Sentry DSN for error tracking

# Logging Configuration
LOG_LEVEL=INFO                                    # Logging level (DEBUG, INFO, WARNING, ERROR)
LOG_TO_STDOUT=True|False                          # Log to console
LOG_TO_FILE=True|False                            # Log to file
LOG_FILE_PATH=logs/app.log                        # Log file path
LOG_MAX_BYTES=10485760                            # Max log file size (10MB)
LOG_BACKUP_COUNT=5                                # Number of backup log files
```

### Configuration Management

#### Environment-Specific Configs
The application supports multiple configuration environments:

**Development Configuration (`config.DevelopmentConfig`)**
- Debug mode enabled
- SQLite database
- Detailed error messages
- CSRF protection disabled for easier testing

**Production Configuration (`config.ProductionConfig`)**
- Debug mode disabled
- PostgreSQL database
- Secure cookie settings
- CSRF protection enabled

**Testing Configuration (`config.TestingConfig`)**
- Testing mode enabled
- In-memory or separate test database
- External services disabled

#### Loading Configuration
```python
# In app.py
from config import get_config

# Get configuration based on FLASK_ENV
config_class = get_config()
app.config.from_object(config_class)
```

#### Custom Configuration
You can create custom configuration classes:

```python
# In config.py
class CustomConfig(ProductionConfig):
    # Override specific settings
    SQLALCHEMY_DATABASE_URI = 'your_custom_database_url'
    CUSTOM_FEATURE_ENABLED = True

## 📡 API Documentation

### Authentication
All API endpoints require authentication. Users must be logged in through the web interface before making API calls.

### Base URL and Headers
```
Base URL: https://your-domain.com/api
Content-Type: application/json
```

### Response Format
All API responses follow this format:
```json
{
  "success": true|false,
  "data": {...},
  "message": "Success/Error message",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Core API Endpoints

#### Patients API
```http
# List all patients
GET /api/patients
Query Parameters:
  - page: Page number (default: 1)
  - per_page: Items per page (default: 20)
  - search: Search term
  - active: true|false

# Get patient details
GET /api/patients/{id}

# Create new patient
POST /api/patients
Body: {
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "date_of_birth": "1990-01-01",
  "gender": "Male",
  "address": "123 Main St",
  "city": "New York",
  "state": "NY",
  "pincode": "10001"
}

# Update patient
PUT /api/patients/{id}
Body: {patient_data}

# Delete patient (soft delete)
DELETE /api/patients/{id}
```

#### Appointments API
```http
# List appointments
GET /api/appointments
Query Parameters:
  - date: Filter by date (YYYY-MM-DD)
  - doctor_id: Filter by doctor
  - status: Filter by status
  - patient_id: Filter by patient

# Create appointment
POST /api/appointments
Body: {
  "patient_id": 1,
  "doctor_id": 2,
  "appointment_date": "2024-01-15",
  "appointment_time": "10:00",
  "visit_type": "CLINIC",
  "reason": "Regular checkup"
}

# Update appointment
PUT /api/appointments/{id}

# Cancel appointment
POST /api/appointments/{id}/cancel
Body: {
  "reason": "Patient request"
}
```

#### Billing API
```http
# List invoices
GET /api/billing

# Create invoice
POST /api/billing
Body: {
  "patient_id": 1,
  "visit_id": 1,
  "items": [
    {
      "description": "Consultation",
      "amount": 500.00
    }
  ]
}

# Record payment
POST /api/billing/{id}/payment
Body: {
  "amount": 500.00,
  "payment_method": "CASH",
  "transaction_reference": "TXN123"
}
```

#### Dashboard API
```http
# Get dashboard statistics
GET /api/dashboard/stats

# Get recent activities
GET /api/dashboard/activities
```

### Error Handling
```json
{
  "success": false,
  "error": {
    "code": 400,
    "message": "Bad Request",
    "details": "Validation errors or specific error information"
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 🗄️ Database Schema

### Core Tables

#### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    uuid VARCHAR(36) UNIQUE NOT NULL,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    role VARCHAR(20) NOT NULL,
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Patients Table
```sql
CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(120),
    phone VARCHAR(20) NOT NULL,
    date_of_birth DATE,
    gender VARCHAR(10),
    address TEXT,
    city VARCHAR(50),
    state VARCHAR(50),
    pincode VARCHAR(10),
    emergency_contact VARCHAR(20),
    medical_history TEXT,
    allergies TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Appointments Table
```sql
CREATE TABLE appointments (
    id SERIAL PRIMARY KEY,
    uuid VARCHAR(36) UNIQUE NOT NULL,
    patient_id INTEGER REFERENCES patients(id),
    doctor_id INTEGER REFERENCES users(id),
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    visit_type VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING',
    reason TEXT,
    notes TEXT,
    created_by_id INTEGER REFERENCES users(id),
    confirmed_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Visits Table
```sql
CREATE TABLE visits (
    id SERIAL PRIMARY KEY,
    uuid VARCHAR(36) UNIQUE NOT NULL,
    patient_id INTEGER REFERENCES patients(id),
    doctor_id INTEGER REFERENCES users(id),
    appointment_id INTEGER REFERENCES appointments(id),
    date_of_visit DATE NOT NULL,
    time_of_visit TIME,
    visit_type VARCHAR(20) NOT NULL,
    chief_complaint TEXT,
    diagnosis TEXT,
    treatment_provided TEXT,
    notes TEXT,
    follow_up_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Billing Table
```sql
CREATE TABLE billing (
    id SERIAL PRIMARY KEY,
    uuid VARCHAR(36) UNIQUE NOT NULL,
    patient_id INTEGER REFERENCES patients(id),
    visit_id INTEGER REFERENCES visits(id),
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    tax_amount DECIMAL(10,2) DEFAULT 0,
    final_amount DECIMAL(10,2) NOT NULL,
    payment_status VARCHAR(20) DEFAULT 'PENDING',
    due_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Relationship Diagram
```
Users (1) -----> (N) Appointments
Users (1) -----> (N) Visits
Patients (1) ---> (N) Appointments
Patients (1) ---> (N) Visits
Patients (1) ---> (N) Billing
Appointments (1) -> (1) Visits
Visits (1) -----> (N) Billing
```

## 🔒 Security Features

### Authentication & Authorization
- **Password Hashing**: bcrypt with salt rounds
- **Session Management**: Flask-Login with secure sessions
- **Role-Based Access Control**: Granular permissions by user role
- **Failed Login Protection**: Account lockout after multiple failures
- **Password Policies**: Configurable complexity requirements

### Data Protection
- **Input Validation**: Server-side validation for all inputs
- **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries
- **XSS Protection**: Template auto-escaping and CSP headers
- **CSRF Protection**: Token-based CSRF protection
- **File Upload Security**: Type validation and size limits

### Communication Security
- **HTTPS Enforcement**: Secure cookie settings for production
- **API Security**: Authentication required for all API endpoints
- **Audit Logging**: Complete audit trail for all user actions
- **Data Encryption**: Sensitive data encryption at rest

### Compliance Features
- **HIPAA Compliance**: Healthcare data protection standards
- **Data Retention**: Configurable data retention policies
- **Access Logs**: Detailed access and activity logging
- **Backup Security**: Encrypted backups with access controls

## 🎨 Customization Guide

### Theming & Branding

#### Customizing Clinic Information
Edit the `.env` file or environment variables:
```env
CLINIC_NAME=Your Clinic Name
CLINIC_ADDRESS=Your Address
CLINIC_PHONE=Your Phone Number
CLINIC_EMAIL=your@email.com
```

#### Custom Styling
1. **Edit CSS files** in `static/css/`
2. **Modify templates** in `templates/`
3. **Add custom JavaScript** in `static/js/`

#### Logo and Images
1. **Replace logo**: Add your logo to `static/images/logo.png`
2. **Update favicon**: Replace `static/images/favicon.ico`
3. **Custom images**: Add to `static/images/` directory

### Adding Custom Features

#### Creating New Routes
1. **Create new blueprint** in `routes/` directory:
```python
# routes/custom.py
from flask import Blueprint, render_template
from flask_login import login_required

custom_bp = Blueprint('custom', __name__)

@custom_bp.route('/custom-feature')
@login_required
def custom_feature():
    return render_template('custom/feature.html')
```

2. **Register blueprint** in `app.py`:
```python
from routes.custom import custom_bp
app.register_blueprint(custom_bp, url_prefix='/custom')
```

#### Adding Database Models
1. **Add model** to `models.py`:
```python
class CustomModel(db.Model):
    __tablename__ = 'custom_table'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    # Add your fields here
```

2. **Create migration** (if using Flask-Migrate):
```bash
flask db migrate -m "Add custom model"
flask db upgrade
```

#### Custom Business Logic
1. **Create service** in `services/` directory:
```python
# services/custom_service.py
class CustomService:
    def __init__(self):
        pass

    def custom_method(self):
        # Your business logic here
        pass
```

2. **Use in routes**:
```python
from services.custom_service import CustomService

@custom_bp.route('/process')
def process():
    service = CustomService()
    result = service.custom_method()
    return jsonify(result)
```

### Configuration Customization

#### Custom Configuration Class
```python
# config.py
class CustomConfig(ProductionConfig):
    # Override default settings
    CUSTOM_FEATURE_ENABLED = True
    CUSTOM_API_URL = 'https://api.example.com'

    # Custom database settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'pool_recycle': 3600
    }
```

#### Environment-Specific Features
```python
# Enable features based on environment
if os.environ.get('FLASK_ENV') == 'development':
    ENABLE_DEBUG_TOOLBAR = True
    ENABLE_PROFILER = True
else:
    ENABLE_DEBUG_TOOLBAR = False
    ENABLE_PROFILER = False
```

### Integration Customization

#### Adding New Payment Gateways
1. **Create payment service**:
```python
# services/payment_service.py
class PaymentService:
    def process_payment(self, amount, method, details):
        if method == 'CUSTOM_GATEWAY':
            return self.process_custom_gateway(amount, details)
        # Handle other methods
```

2. **Update billing routes** to use new service

#### Custom Notification Channels
1. **Create notification service**:
```python
# services/notification_service.py
class NotificationService:
    def send_notification(self, channel, message, recipient):
        if channel == 'CUSTOM_CHANNEL':
            return self.send_custom_notification(message, recipient)
        # Handle other channels
```

2. **Integrate with appointment and billing systems**

## 🚨 Troubleshooting

### Common Issues and Solutions

#### Installation Issues

**Problem**: `pip install` fails with permission errors
```bash
# Solution: Use virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

**Problem**: Database connection errors
```bash
# Check database URL format
# SQLite: sqlite:///hospital_crm.db
# PostgreSQL: postgresql://user:password@host:port/database

# Verify database exists and is accessible
python -c "from app import create_app; app = create_app(); print('Database connection successful')"
```

**Problem**: Import errors for specific modules
```bash
# Install missing dependencies
pip install --upgrade -r requirements.txt

# Check Python version (requires 3.11+)
python --version

# Verify all required packages
python -c "import flask, flask_sqlalchemy, flask_login; print('All packages imported successfully')"
```

#### Runtime Issues

**Problem**: Application won't start
```bash
# Check for syntax errors
python -m py_compile app.py

# Run with debug mode for detailed errors
export FLASK_DEBUG=1
python app.py

# Check port availability
netstat -an | grep :5000  # Linux/Mac
netstat -an | findstr :5000  # Windows
```

**Problem**: Database initialization fails
```bash
# Delete existing database and recreate
rm hospital_crm.db  # For SQLite
python app.py

# Check database permissions
ls -la hospital_crm.db  # Linux/Mac

# Verify database schema
sqlite3 hospital_crm.db ".schema"  # For SQLite
```

**Problem**: Login issues with default credentials
```bash
# Verify default users were created
python -c "
from app import create_app
from models import User
app = create_app()
with app.app_context():
    users = User.query.all()
    for user in users:
        print(f'User: {user.username}, Role: {user.role.value}')
"

# Reset default users
python -c "
from app import create_app, create_default_data
app = create_app()
with app.app_context():
    create_default_data()
"
```

#### Performance Issues

**Problem**: Slow page loading
```bash
# Enable SQL query logging
export SQLALCHEMY_ECHO=1
python app.py

# Check database indexes
# Add indexes for frequently queried columns

# Monitor memory usage
python -c "
import psutil
print(f'Memory usage: {psutil.virtual_memory().percent}%')
"
```

**Problem**: High memory usage
```bash
# Reduce worker processes in production
# Edit gunicorn command: --workers 1 (instead of 2 or 4)

# Check for memory leaks
pip install memory_profiler
python -m memory_profiler app.py
```

#### Docker Issues

**Problem**: Docker build fails
```bash
# Clean Docker cache
docker system prune -a

# Build with no cache
docker-compose build --no-cache

# Check Dockerfile syntax
docker build -t test .
```

**Problem**: Container startup issues
```bash
# Check container logs
docker-compose logs app

# Access container shell
docker-compose exec app bash

# Check environment variables
docker-compose exec app env | grep FLASK
```

**Problem**: Database connection in Docker
```bash
# Verify database container is running
docker-compose ps

# Check database logs
docker-compose logs db

# Test database connection
docker-compose exec app python -c "
from models import db
from app import create_app
app = create_app()
with app.app_context():
    db.engine.execute('SELECT 1')
    print('Database connection successful')
"
```

#### Deployment Issues

**Problem**: Render deployment fails
```bash
# Check build logs in Render dashboard
# Common issues:
# - Missing environment variables
# - Incorrect start command
# - Database connection issues

# Verify environment variables are set
# Check DATABASE_URL format
# Ensure all required variables are configured
```

**Problem**: SSL/HTTPS issues
```bash
# For Render: SSL is automatic with custom domains
# Check domain DNS configuration
# Verify CNAME record points to Render URL

# For custom deployment:
# Ensure SSL certificates are valid
# Check nginx/proxy configuration
```

### Debugging Tools

#### Application Debugging
```python
# Add debug prints
import logging
logging.basicConfig(level=logging.DEBUG)

# Use Flask debug toolbar (development only)
pip install flask-debugtoolbar
# Add to app configuration:
app.config['DEBUG_TB_ENABLED'] = True
```

#### Database Debugging
```python
# Enable SQL query logging
app.config['SQLALCHEMY_ECHO'] = True

# Check database queries
from sqlalchemy import event
from sqlalchemy.engine import Engine

@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    print(f"SQL: {statement}")
    print(f"Parameters: {parameters}")
```

#### Performance Monitoring
```python
# Add timing decorators
import time
from functools import wraps

def timing_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.2f} seconds")
        return result
    return wrapper
```

### Getting Help

#### Log Analysis
```bash
# Check application logs
tail -f logs/app.log

# Check system logs
# Linux: journalctl -u your-service
# Check error patterns and timestamps
```

#### Health Checks
```bash
# Application health check
curl http://localhost:5000/health

# Database health check
python -c "
from app import create_app
from models import db
app = create_app()
with app.app_context():
    try:
        db.session.execute('SELECT 1')
        print('✅ Database: Healthy')
    except Exception as e:
        print(f'❌ Database: {e}')
"
```

#### Support Resources
- **GitHub Issues**: Report bugs and request features
- **Documentation**: Check HOSTING_GUIDE.md for detailed setup
- **Community**: Join discussions in GitHub Discussions
- **Professional Support**: Contact for enterprise support options

## 🤝 Contributing

### Development Setup
```bash
# Fork the repository on GitHub
git clone https://github.com/YOUR_USERNAME/Dr_payal.git
cd Dr_payal

# Create development branch
git checkout -b feature/your-feature-name

# Set up development environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If exists

# Run tests
python -m pytest
```

### Code Standards
- **Python Style**: Follow PEP 8 guidelines
- **Code Formatting**: Use Black for code formatting
- **Import Sorting**: Use isort for import organization
- **Linting**: Use flake8 for code linting
- **Type Hints**: Add type hints where appropriate

### Testing Guidelines
- **Unit Tests**: Write tests for all new functions
- **Integration Tests**: Test API endpoints and workflows
- **Test Coverage**: Maintain >80% test coverage
- **Test Data**: Use fixtures for consistent test data

### Pull Request Process
1. **Create feature branch** from main
2. **Make changes** with proper commit messages
3. **Add tests** for new functionality
4. **Update documentation** if needed
5. **Run tests** and ensure they pass
6. **Submit pull request** with detailed description

### Commit Message Format
```
type(scope): description

[optional body]

[optional footer]
```

**Types**: feat, fix, docs, style, refactor, test, chore

**Examples**:
```
feat(patients): add patient search functionality
fix(billing): resolve payment calculation error
docs(readme): update installation instructions
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### MIT License Summary
- ✅ **Commercial use** allowed
- ✅ **Modification** allowed
- ✅ **Distribution** allowed
- ✅ **Private use** allowed
- ❌ **Liability** not provided
- ❌ **Warranty** not provided

## 🆘 Support & Contact

### Documentation
- **Complete Setup Guide**: [HOSTING_GUIDE.md](HOSTING_GUIDE.md)
- **API Documentation**: [docs/API.md](docs/API.md)
- **Deployment Guide**: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

### Community Support
- **GitHub Issues**: [Report bugs and request features](https://github.com/1981Rupal/Dr_payal/issues)
- **GitHub Discussions**: [Community discussions and Q&A](https://github.com/1981Rupal/Dr_payal/discussions)
- **Documentation**: Check this README and linked guides

### Professional Support
For enterprise deployments, custom development, or professional support:
- **Email**: Contact through GitHub profile
- **Custom Development**: Available for feature additions
- **Training**: Setup and usage training available
- **Maintenance**: Ongoing maintenance and support contracts

### Contributing
We welcome contributions! See the [Contributing](#-contributing) section for guidelines.

## 🙏 Acknowledgments

### Technology Stack
- **[Flask](https://flask.palletsprojects.com/)**: Web framework
- **[SQLAlchemy](https://sqlalchemy.org/)**: Database ORM
- **[Bootstrap](https://getbootstrap.com/)**: UI framework
- **[jQuery](https://jquery.com/)**: JavaScript library

### External Services
- **[Twilio](https://twilio.com/)**: WhatsApp and SMS integration
- **[OpenAI](https://openai.com/)**: AI chatbot functionality
- **[Render.com](https://render.com/)**: Cloud hosting platform
- **[PostgreSQL](https://postgresql.org/)**: Production database

### Icons and Assets
- **[Bootstrap Icons](https://icons.getbootstrap.com/)**: Icon library
- **[Unsplash](https://unsplash.com/)**: Stock photography
- **[Font Awesome](https://fontawesome.com/)**: Additional icons

---

## 📋 Quick Reference

### Default Login Credentials
- **Super Admin**: `superadmin` / `admin123`
- **Doctor**: `doctor` / `doctor123`
- **Staff**: `staff` / `staff123`

### Important URLs
- **Application**: `http://localhost:5000`
- **Health Check**: `http://localhost:5000/health`
- **API Base**: `http://localhost:5000/api`

### Key Commands
```bash
# Local development
python run_local.py

# Docker deployment
docker-compose up --build

# Run tests
python -m pytest

# Database backup (SQLite)
cp hospital_crm.db backup_$(date +%Y%m%d).db
```

### Environment Variables
```env
# Minimum required
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///hospital_crm.db

# Production additions
FLASK_ENV=production
SESSION_COOKIE_SECURE=true
```

---

**Made with ❤️ for healthcare professionals worldwide**

*This comprehensive Hospital CRM system is designed to streamline clinic operations, improve patient care, and enhance healthcare delivery. Whether you're running a small physiotherapy clinic or a larger medical practice, this system provides the tools you need to manage patients, appointments, billing, and more.*
```
```
