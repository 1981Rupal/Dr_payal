# 🏥 Hospital & Clinic CRM System

A comprehensive Customer Relationship Management system designed specifically for hospitals, clinics, and physiotherapy centers. Built with modern technologies and designed for scalability, security, and ease of use.

## ✨ Features

### 🎯 Core Features
- **👥 Patient Management**: Complete patient registration, profile management, and medical history
- **📅 Appointment System**: Advanced booking with calendar integration and multiple visit types
- **🏥 Visit Management**: Track clinic visits, home visits, and online consultations
- **💰 Payment System**: Flexible payment options including packages and daily payments
- **💊 Prescription Management**: Digital prescriptions and medical records
- **📱 WhatsApp Integration**: Automated notifications and communication
- **🤖 AI Chatbot**: Intelligent appointment booking with admin confirmation
- **💻 Online Consultations**: Video consultation platform
- **📊 Analytics Dashboard**: Comprehensive reporting and business intelligence

### 🔧 Technical Features
- **📱 Multi-platform**: Web, mobile, and desktop support
- **⚡ Real-time Updates**: Live notifications and updates
- **🔐 Secure Authentication**: Role-based access control with multiple user types
- **🔌 RESTful API**: Complete API for mobile and third-party integrations
- **📱 Responsive Design**: Mobile-first UI/UX with Bootstrap 5
- **🐳 Docker Support**: Easy deployment and scaling
- **☁️ Cloud Ready**: Deploy to Docker, Render, or any cloud platform

### 👥 User Roles
- **🔑 Super Admin**: Full system access and configuration
- **👨‍💼 Admin**: Clinic management and staff oversight
- **👨‍⚕️ Doctor**: Patient management and consultations
- **👩‍💼 Staff**: Appointment and basic patient management
- **🧑‍🤝‍🧑 Patient**: Self-service portal and appointments

## 🏗️ Architecture

### 🖥️ Backend
- **Framework**: Flask (Python) with SQLAlchemy ORM
- **Database**: PostgreSQL with comprehensive data models
- **Authentication**: Flask-Login with role-based access control
- **File Storage**: Local/Cloud storage for documents and images
- **Background Tasks**: Celery with Redis for async processing
- **Caching**: Redis for session storage and caching

### 🎨 Frontend
- **Web Framework**: Flask with Jinja2 templates
- **UI Framework**: Bootstrap 5 with custom CSS
- **JavaScript**: Vanilla JS with modern ES6+ features
- **Charts**: Chart.js for analytics and reporting
- **Icons**: Bootstrap Icons for consistent iconography

### 🔗 Integrations
- **📱 WhatsApp**: Twilio WhatsApp Business API
- **🤖 AI Chatbot**: OpenAI GPT integration for natural language processing
- **💳 Payments**: Support for Razorpay and Stripe
- **📧 Email**: SMTP integration for notifications
- **📊 Monitoring**: Optional Prometheus and Grafana integration

## 📁 Project Structure

```
hospital-crm/
├── 📄 app.py                    # Original Flask app (legacy)
├── 📄 app_enhanced.py           # Enhanced Flask application
├── 📄 models.py                 # Comprehensive database models
├── 📄 requirements.txt          # Python dependencies
├── 📄 Dockerfile               # Docker configuration
├── 📄 docker-compose.yml       # Multi-service Docker setup
├── 📄 .env.example             # Environment variables template
├── 📁 services/                # Business logic services
│   ├── 📄 whatsapp_service.py  # WhatsApp integration
│   ├── 📄 chatbot_service.py   # AI chatbot functionality
│   ├── 📄 appointment_service.py # Appointment management
│   └── 📄 billing_service.py   # Billing and payments
├── 📁 templates/               # HTML templates
│   ├── 📄 base.html            # Base template with modern UI
│   ├── 📁 auth/                # Authentication templates
│   ├── 📁 dashboard/           # Dashboard templates
│   ├── 📁 patients/            # Patient management
│   ├── 📁 appointments/        # Appointment templates
│   └── 📁 billing/             # Billing templates
├── 📁 static/                  # Static assets (CSS, JS, images)
├── 📁 scripts/                 # Deployment and utility scripts
│   ├── 📄 deploy.sh            # Linux/Mac deployment script
│   └── 📄 deploy.bat           # Windows deployment script
├── 📁 nginx/                   # Nginx configuration
├── 📁 monitoring/              # Prometheus & Grafana configs
└── 📁 docs/                    # Documentation
```

## 🚀 Quick Start

### 🐳 Using Docker (Recommended)

#### Prerequisites
- Docker Desktop installed
- Docker Compose available
- Git for cloning the repository

#### Windows Users
```batch
# Clone the repository
git clone https://github.com/your-username/hospital-crm.git
cd hospital-crm

# Copy environment file and configure
copy .env.example .env
# Edit .env file with your configuration

# Deploy using the Windows script
scripts\deploy.bat local
```

#### Linux/Mac Users
```bash
# Clone the repository
git clone https://github.com/your-username/hospital-crm.git
cd hospital-crm

# Copy environment file and configure
cp .env.example .env
# Edit .env file with your configuration

# Make deployment script executable and run
chmod +x scripts/deploy.sh
./scripts/deploy.sh local
```

#### Manual Docker Setup
```bash
# Build and start all services
docker-compose up -d

# Initialize database (first time only)
docker-compose exec app flask db upgrade

# Access the application
# Web: http://localhost:5000
# Database: localhost:5432
# Redis: localhost:6379
```

### 🔧 Manual Setup (Development)
```bash
# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database and API keys

# Set up PostgreSQL database
createdb hospital_crm

# Run database migrations
flask db upgrade

# Start the application
python app_enhanced.py
```

## ⚙️ Configuration

### 🔐 Environment Variables

Copy `.env.example` to `.env` and configure the following:

#### 🗄️ Database Configuration
```env
DATABASE_URL=postgresql://hospital_user:hospital_password_2024@localhost:5432/hospital_crm
```

#### 🔑 Application Security
```env
SECRET_KEY=your-super-secret-key-change-in-production-2024
FLASK_ENV=development  # or production
```

#### 📱 WhatsApp Integration (Twilio)
```env
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

#### 🤖 AI Chatbot (OpenAI)
```env
OPENAI_API_KEY=your_openai_api_key
```

#### 📧 Email Configuration
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
```

#### 💳 Payment Gateways (Optional)
```env
# Razorpay (for Indian payments)
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret

# Stripe (for international payments)
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
STRIPE_SECRET_KEY=your_stripe_secret_key
```

### 🏥 Default Login Credentials

After deployment, use these credentials to access the system:

| Role | Username | Password |
|------|----------|----------|
| Super Admin | `superadmin` | `admin123` |
| Doctor | `doctor` | `doctor123` |
| Staff | `staff` | `staff123` |

⚠️ **Important**: Change these default passwords immediately after first login!

## 🚀 Deployment Options

### 🐳 Docker Deployment (Recommended)

#### Production Deployment
```bash
# Clone and configure
git clone https://github.com/your-username/hospital-crm.git
cd hospital-crm
cp .env.example .env
# Edit .env with production values

# Deploy with monitoring (optional)
docker-compose --profile monitoring up -d

# Or deploy basic setup
docker-compose up -d
```

#### Features
- ✅ Production-ready Docker configuration
- ✅ Multi-stage builds for optimization
- ✅ Health checks and monitoring
- ✅ Nginx reverse proxy with SSL support
- ✅ PostgreSQL database with persistent storage
- ✅ Redis for caching and sessions
- ✅ Celery for background tasks
- ✅ Optional Prometheus & Grafana monitoring

### ☁️ Render Deployment

#### One-Click Deployment
1. **Fork this repository** to your GitHub account
2. **Connect to Render**: Go to [Render Dashboard](https://dashboard.render.com)
3. **Create New Web Service**: Connect your GitHub repository
4. **Configure Environment Variables** in Render dashboard:
   ```
   DATABASE_URL=<provided by Render PostgreSQL>
   SECRET_KEY=<generate secure key>
   TWILIO_ACCOUNT_SID=<your twilio sid>
   TWILIO_AUTH_TOKEN=<your twilio token>
   OPENAI_API_KEY=<your openai key>
   ```
5. **Deploy**: Render will automatically build and deploy

#### Render Features
- ✅ Automatic SSL certificates
- ✅ Managed PostgreSQL database
- ✅ Auto-scaling and health monitoring
- ✅ Git-based deployments
- ✅ Built-in CDN and DDoS protection

### 🖥️ VPS/Server Deployment

#### Using the deployment script:
```bash
# On your server
git clone https://github.com/your-username/hospital-crm.git
cd hospital-crm
./scripts/deploy.sh local
```

#### Manual server setup:
```bash
# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Clone and deploy
git clone https://github.com/your-username/hospital-crm.git
cd hospital-crm
cp .env.example .env
# Configure .env file
docker-compose up -d
```

## 📊 Features Overview

### 👥 Patient Management
- Complete patient profiles with medical history
- Emergency contact information
- Insurance details and allergies tracking
- Patient portal for self-service

### 📅 Appointment System
- Calendar-based scheduling
- Multiple visit types (Clinic, Home, Online)
- Automated reminders via WhatsApp
- Admin confirmation workflow
- Recurring appointments support

### 💊 Prescription Management
- Digital prescription creation
- Medication tracking and history
- PDF generation for prescriptions
- Patient access to prescription history

### 💰 Billing & Payments
- Flexible payment options
- Package-based billing
- Payment tracking and history
- Automated payment reminders
- Multiple payment methods support

### 🤖 AI-Powered Features
- WhatsApp chatbot for appointment booking
- Natural language processing
- Automated responses and routing
- Intent recognition and entity extraction

### 📱 WhatsApp Integration
- Appointment confirmations and reminders
- Bill notifications
- Prescription sharing
- Two-way communication support
- Automated status updates

### 📊 Analytics & Reporting
- Patient visit statistics
- Revenue tracking and analysis
- Appointment analytics
- Package utilization reports
- Custom date range filtering

## 🛠️ Development

### 🔧 Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/your-username/hospital-crm.git
cd hospital-crm

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with development settings

# Set up database
createdb hospital_crm_dev
flask db upgrade

# Run development server
python app_enhanced.py
```

### 🧪 Running Tests

```bash
# Install test dependencies
pip install pytest pytest-flask

# Run tests
pytest

# Run with coverage
pytest --cov=.
```

### 🔍 Code Quality

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

## 📚 API Documentation

The system provides RESTful APIs for all major functions:

### 🔐 Authentication Endpoints
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user info

### 👥 Patient Endpoints
- `GET /api/patients` - List patients
- `POST /api/patients` - Create patient
- `GET /api/patients/{id}` - Get patient details
- `PUT /api/patients/{id}` - Update patient
- `DELETE /api/patients/{id}` - Delete patient

### 📅 Appointment Endpoints
- `GET /api/appointments` - List appointments
- `POST /api/appointments` - Create appointment
- `PUT /api/appointments/{id}/confirm` - Confirm appointment
- `PUT /api/appointments/{id}/cancel` - Cancel appointment

### 💊 Prescription Endpoints
- `GET /api/prescriptions` - List prescriptions
- `POST /api/prescriptions` - Create prescription
- `GET /api/prescriptions/{id}/pdf` - Download prescription PDF

### 💰 Billing Endpoints
- `GET /api/billing` - List bills
- `POST /api/billing` - Create bill
- `POST /api/payments` - Process payment

## 🔧 Troubleshooting

### Common Issues

#### Database Connection Issues
```bash
# Check if PostgreSQL is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Reset database
docker-compose down -v
docker-compose up -d
```

#### WhatsApp Integration Issues
- Verify Twilio credentials in `.env`
- Check Twilio console for webhook configuration
- Ensure WhatsApp number is verified

#### AI Chatbot Issues
- Verify OpenAI API key is valid
- Check API usage limits
- Review chatbot logs for errors

### 📞 Support

For support and questions:
- 📧 Email: support@drpayal.com
- 📱 WhatsApp: +1234567890
- 🐛 Issues: [GitHub Issues](https://github.com/your-username/hospital-crm/issues)

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🙏 Acknowledgments

- Built with ❤️ for healthcare professionals
- Powered by Flask, PostgreSQL, and modern web technologies
- WhatsApp integration via Twilio
- AI capabilities powered by OpenAI
- UI components from Bootstrap 5

---

**Made with ❤️ for Dr. Payal's Physiotherapy Clinic and healthcare professionals worldwide.**
