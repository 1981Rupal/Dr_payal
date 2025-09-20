@echo off
REM Hospital CRM Deployment Script for Windows
REM This script handles deployment to various platforms

setlocal enabledelayedexpansion

REM Function to print colored output (simplified for Windows)
:print_status
echo [INFO] %~1
goto :eof

:print_success
echo [SUCCESS] %~1
goto :eof

:print_warning
echo [WARNING] %~1
goto :eof

:print_error
echo [ERROR] %~1
goto :eof

REM Function to check if command exists
:command_exists
where %1 >nul 2>&1
goto :eof

REM Function to check prerequisites
:check_prerequisites
call :print_status "Checking prerequisites..."

call :command_exists docker
if errorlevel 1 (
    call :print_error "Docker is not installed. Please install Docker Desktop first."
    exit /b 1
)

call :command_exists docker-compose
if errorlevel 1 (
    call :print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit /b 1
)

call :print_success "Prerequisites check passed"
goto :eof

REM Function to setup environment
:setup_environment
call :print_status "Setting up environment..."

if not exist .env (
    if exist .env.example (
        copy .env.example .env
        call :print_warning "Created .env file from .env.example. Please update the values before proceeding."
        call :print_warning "Edit .env file with your configuration and run the script again."
        exit /b 1
    ) else (
        call :print_error ".env.example file not found. Cannot create environment configuration."
        exit /b 1
    )
)

call :print_success "Environment configuration ready"
goto :eof

REM Function to build and start services
:start_services
call :print_status "Building and starting services..."

REM Build the application
docker-compose build --no-cache
if errorlevel 1 (
    call :print_error "Failed to build services"
    exit /b 1
)

REM Start the services
docker-compose up -d
if errorlevel 1 (
    call :print_error "Failed to start services"
    exit /b 1
)

call :print_success "Services started successfully"
goto :eof

REM Function to initialize database
:init_database
call :print_status "Initializing database..."

REM Wait for database to be ready
call :print_status "Waiting for database to be ready..."
timeout /t 10 /nobreak >nul

REM Run database migrations
docker-compose exec app flask db upgrade
if errorlevel 1 (
    call :print_warning "Database migration failed or no migrations to run"
)

REM Create default data
docker-compose exec app python -c "from app_enhanced import create_app; from models import db; app = create_app(); app.app_context().push(); from app_enhanced import create_default_data; create_default_data(); print('Default data created successfully')"

call :print_success "Database initialized successfully"
goto :eof

REM Function to run health checks
:health_check
call :print_status "Running health checks..."

REM Check if services are running
docker-compose ps | findstr "Up" >nul
if errorlevel 1 (
    call :print_error "Some services are not running properly"
    docker-compose ps
    exit /b 1
)

REM Wait a bit for services to fully start
timeout /t 5 /nobreak >nul

REM Check application health
curl -f http://localhost:5000/health >nul 2>&1
if errorlevel 1 (
    call :print_warning "Application health check failed, but services are running"
) else (
    call :print_success "Application health check passed"
)

call :print_success "Health checks completed"
goto :eof

REM Function to deploy to Render
:deploy_to_render
call :print_status "Preparing for Render deployment..."

if not exist render.yaml (
    call :print_status "Creating render.yaml configuration..."
    (
        echo services:
        echo   - type: web
        echo     name: hospital-crm
        echo     env: python
        echo     buildCommand: pip install -r requirements.txt
        echo     startCommand: gunicorn --bind 0.0.0.0:$PORT app_enhanced:create_app^(^)
        echo     envVars:
        echo       - key: PYTHON_VERSION
        echo         value: 3.11.0
        echo       - key: DATABASE_URL
        echo         fromDatabase:
        echo           name: hospital-crm-db
        echo           property: connectionString
        echo       - key: SECRET_KEY
        echo         generateValue: true
        echo       - key: FLASK_ENV
        echo         value: production
        echo.
        echo databases:
        echo   - name: hospital-crm-db
        echo     databaseName: hospital_crm
        echo     user: hospital_user
    ) > render.yaml
    call :print_success "render.yaml created"
)

call :print_warning "To deploy to Render:"
call :print_warning "1. Push your code to GitHub"
call :print_warning "2. Connect your GitHub repository to Render"
call :print_warning "3. Configure environment variables in Render dashboard"
call :print_warning "4. Deploy using the Render dashboard"
goto :eof

REM Function to show usage
:show_usage
echo Usage: %0 [OPTION]
echo.
echo Options:
echo   local     Deploy locally using Docker Compose
echo   render    Prepare for Render deployment
echo   stop      Stop all services
echo   restart   Restart all services
echo   logs      Show application logs
echo   backup    Create database backup
echo   help      Show this help message
echo.
goto :eof

REM Function to stop services
:stop_services
call :print_status "Stopping services..."
docker-compose down
call :print_success "Services stopped"
goto :eof

REM Function to restart services
:restart_services
call :print_status "Restarting services..."
docker-compose restart
call :print_success "Services restarted"
goto :eof

REM Function to show logs
:show_logs
call :print_status "Showing application logs..."
docker-compose logs -f app
goto :eof

REM Function to create backup
:create_backup
call :print_status "Creating database backup..."

set BACKUP_DIR=backups
set BACKUP_FILE=hospital_crm_backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.sql
set BACKUP_FILE=%BACKUP_FILE: =0%

if not exist %BACKUP_DIR% mkdir %BACKUP_DIR%

docker-compose exec -T db pg_dump -U hospital_user hospital_crm > "%BACKUP_DIR%\%BACKUP_FILE%"

call :print_success "Database backup created: %BACKUP_DIR%\%BACKUP_FILE%"
goto :eof

REM Main deployment logic
if "%1"=="local" (
    call :print_status "Starting local deployment..."
    call :check_prerequisites
    if errorlevel 1 exit /b 1
    call :setup_environment
    if errorlevel 1 exit /b 1
    call :start_services
    if errorlevel 1 exit /b 1
    call :init_database
    call :health_check
    call :print_success "Local deployment completed successfully!"
    call :print_status "Application is running at: http://localhost:5000"
    call :print_status "Admin login: superadmin / admin123"
) else if "%1"=="render" (
    call :deploy_to_render
) else if "%1"=="stop" (
    call :stop_services
) else if "%1"=="restart" (
    call :restart_services
) else if "%1"=="logs" (
    call :show_logs
) else if "%1"=="backup" (
    call :create_backup
) else if "%1"=="help" (
    call :show_usage
) else if "%1"=="--help" (
    call :show_usage
) else if "%1"=="-h" (
    call :show_usage
) else (
    call :print_error "Invalid option: %1"
    call :show_usage
    exit /b 1
)
