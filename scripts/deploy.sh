#!/bin/bash

# Hospital CRM Deployment Script
# This script handles deployment to various platforms

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command_exists docker-compose; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Function to setup environment
setup_environment() {
    print_status "Setting up environment..."
    
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            cp .env.example .env
            print_warning "Created .env file from .env.example. Please update the values before proceeding."
            print_warning "Edit .env file with your configuration and run the script again."
            exit 1
        else
            print_error ".env.example file not found. Cannot create environment configuration."
            exit 1
        fi
    fi
    
    print_success "Environment configuration ready"
}

# Function to build and start services
start_services() {
    print_status "Building and starting services..."
    
    # Build the application
    docker-compose build --no-cache
    
    # Start the services
    docker-compose up -d
    
    print_success "Services started successfully"
}

# Function to initialize database
init_database() {
    print_status "Initializing database..."
    
    # Wait for database to be ready
    print_status "Waiting for database to be ready..."
    sleep 10
    
    # Run database migrations
    docker-compose exec app flask db upgrade
    
    # Create default data
    docker-compose exec app python -c "
from app_enhanced import create_app
from models import db
app = create_app()
with app.app_context():
    # Import and run the create_default_data function
    from app_enhanced import create_default_data
    create_default_data()
    print('Default data created successfully')
"
    
    print_success "Database initialized successfully"
}

# Function to run health checks
health_check() {
    print_status "Running health checks..."
    
    # Check if services are running
    if ! docker-compose ps | grep -q "Up"; then
        print_error "Some services are not running properly"
        docker-compose ps
        exit 1
    fi
    
    # Check application health
    sleep 5
    if curl -f http://localhost:5000/health >/dev/null 2>&1; then
        print_success "Application health check passed"
    else
        print_error "Application health check failed"
        exit 1
    fi
    
    print_success "All health checks passed"
}

# Function to deploy to Render
deploy_to_render() {
    print_status "Preparing for Render deployment..."
    
    # Check if render.yaml exists
    if [ ! -f render.yaml ]; then
        print_status "Creating render.yaml configuration..."
        cat > render.yaml << EOF
services:
  - type: web
    name: hospital-crm
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn --bind 0.0.0.0:\$PORT app_enhanced:create_app()
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: DATABASE_URL
        fromDatabase:
          name: hospital-crm-db
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: FLASK_ENV
        value: production

databases:
  - name: hospital-crm-db
    databaseName: hospital_crm
    user: hospital_user
EOF
        print_success "render.yaml created"
    fi
    
    print_warning "To deploy to Render:"
    print_warning "1. Push your code to GitHub"
    print_warning "2. Connect your GitHub repository to Render"
    print_warning "3. Configure environment variables in Render dashboard"
    print_warning "4. Deploy using the Render dashboard"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  local     Deploy locally using Docker Compose"
    echo "  render    Prepare for Render deployment"
    echo "  stop      Stop all services"
    echo "  restart   Restart all services"
    echo "  logs      Show application logs"
    echo "  backup    Create database backup"
    echo "  help      Show this help message"
    echo ""
}

# Function to stop services
stop_services() {
    print_status "Stopping services..."
    docker-compose down
    print_success "Services stopped"
}

# Function to restart services
restart_services() {
    print_status "Restarting services..."
    docker-compose restart
    print_success "Services restarted"
}

# Function to show logs
show_logs() {
    print_status "Showing application logs..."
    docker-compose logs -f app
}

# Function to create backup
create_backup() {
    print_status "Creating database backup..."
    
    BACKUP_DIR="backups"
    BACKUP_FILE="hospital_crm_backup_$(date +%Y%m%d_%H%M%S).sql"
    
    mkdir -p $BACKUP_DIR
    
    docker-compose exec -T db pg_dump -U hospital_user hospital_crm > "$BACKUP_DIR/$BACKUP_FILE"
    
    print_success "Database backup created: $BACKUP_DIR/$BACKUP_FILE"
}

# Main deployment logic
case "$1" in
    "local")
        print_status "Starting local deployment..."
        check_prerequisites
        setup_environment
        start_services
        init_database
        health_check
        print_success "Local deployment completed successfully!"
        print_status "Application is running at: http://localhost:5000"
        print_status "Admin login: superadmin / admin123"
        ;;
    "render")
        deploy_to_render
        ;;
    "stop")
        stop_services
        ;;
    "restart")
        restart_services
        ;;
    "logs")
        show_logs
        ;;
    "backup")
        create_backup
        ;;
    "help"|"--help"|"-h")
        show_usage
        ;;
    *)
        print_error "Invalid option: $1"
        show_usage
        exit 1
        ;;
esac
