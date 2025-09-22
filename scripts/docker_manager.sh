#!/bin/bash

# Hospital CRM Docker Management Script
# This script provides easy commands to manage the Docker environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="hospital-crm"
COMPOSE_FILE="docker-compose.yml"
DEV_COMPOSE_FILE="docker-compose.dev.yml"

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

check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed or not in PATH"
        exit 1
    fi
}

show_help() {
    echo "Hospital CRM Docker Management Script"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  dev-up          Start development environment"
    echo "  dev-down        Stop development environment"
    echo "  dev-logs        Show development logs"
    echo "  dev-shell       Open shell in development container"
    echo ""
    echo "  prod-up         Start production environment"
    echo "  prod-down       Stop production environment"
    echo "  prod-logs       Show production logs"
    echo "  prod-shell      Open shell in production container"
    echo ""
    echo "  build           Build all images"
    echo "  rebuild         Rebuild all images (no cache)"
    echo "  clean           Clean up containers, images, and volumes"
    echo "  health          Check health of all services"
    echo "  backup          Backup database and uploads"
    echo "  restore         Restore from backup"
    echo ""
    echo "  monitoring-up   Start monitoring stack (Prometheus, Grafana)"
    echo "  monitoring-down Stop monitoring stack"
    echo ""
    echo "Options:"
    echo "  -h, --help      Show this help message"
    echo "  -v, --verbose   Verbose output"
}

dev_up() {
    log_info "Starting development environment..."
    docker-compose -f $DEV_COMPOSE_FILE up -d
    log_success "Development environment started"
    log_info "Services available at:"
    echo "  - Application: http://localhost:5001"
    echo "  - Database Admin: http://localhost:8080"
    echo "  - Redis Commander: http://localhost:8081"
    echo "  - Mailhog: http://localhost:8025"
}

dev_down() {
    log_info "Stopping development environment..."
    docker-compose -f $DEV_COMPOSE_FILE down
    log_success "Development environment stopped"
}

dev_logs() {
    docker-compose -f $DEV_COMPOSE_FILE logs -f "${@:2}"
}

dev_shell() {
    log_info "Opening shell in development container..."
    docker-compose -f $DEV_COMPOSE_FILE exec app bash
}

prod_up() {
    log_info "Starting production environment..."
    docker-compose -f $COMPOSE_FILE up -d
    log_success "Production environment started"
    log_info "Services available at:"
    echo "  - Application: http://localhost:80"
    echo "  - HTTPS: https://localhost:443"
}

prod_down() {
    log_info "Stopping production environment..."
    docker-compose -f $COMPOSE_FILE down
    log_success "Production environment stopped"
}

prod_logs() {
    docker-compose -f $COMPOSE_FILE logs -f "${@:2}"
}

prod_shell() {
    log_info "Opening shell in production container..."
    docker-compose -f $COMPOSE_FILE exec app bash
}

build_images() {
    log_info "Building all images..."
    docker-compose -f $COMPOSE_FILE build
    docker-compose -f $DEV_COMPOSE_FILE build
    log_success "All images built successfully"
}

rebuild_images() {
    log_info "Rebuilding all images (no cache)..."
    docker-compose -f $COMPOSE_FILE build --no-cache
    docker-compose -f $DEV_COMPOSE_FILE build --no-cache
    log_success "All images rebuilt successfully"
}

clean_docker() {
    log_warning "This will remove all containers, images, and volumes for this project"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Cleaning up Docker resources..."
        
        # Stop and remove containers
        docker-compose -f $COMPOSE_FILE down -v --remove-orphans 2>/dev/null || true
        docker-compose -f $DEV_COMPOSE_FILE down -v --remove-orphans 2>/dev/null || true
        
        # Remove project images
        docker images | grep $PROJECT_NAME | awk '{print $3}' | xargs docker rmi -f 2>/dev/null || true
        
        # Clean up unused resources
        docker system prune -f
        
        log_success "Docker cleanup completed"
    else
        log_info "Cleanup cancelled"
    fi
}

check_health() {
    log_info "Checking health of all services..."
    
    # Check if containers are running
    if docker-compose -f $COMPOSE_FILE ps | grep -q "Up"; then
        log_info "Production containers status:"
        docker-compose -f $COMPOSE_FILE ps
        
        # Check health endpoints
        log_info "Checking health endpoints..."
        
        # App health
        if curl -f http://localhost:5000/health &>/dev/null; then
            log_success "Application health check passed"
        else
            log_error "Application health check failed"
        fi
        
    elif docker-compose -f $DEV_COMPOSE_FILE ps | grep -q "Up"; then
        log_info "Development containers status:"
        docker-compose -f $DEV_COMPOSE_FILE ps
        
        # Check health endpoints
        if curl -f http://localhost:5001/health &>/dev/null; then
            log_success "Development application health check passed"
        else
            log_error "Development application health check failed"
        fi
    else
        log_warning "No containers are currently running"
    fi
}

backup_data() {
    log_info "Creating backup..."
    
    BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p $BACKUP_DIR
    
    # Backup database
    log_info "Backing up database..."
    docker-compose -f $COMPOSE_FILE exec -T db pg_dump -U hospital_user hospital_crm > $BACKUP_DIR/database.sql
    
    # Backup uploads
    log_info "Backing up uploads..."
    docker cp $(docker-compose -f $COMPOSE_FILE ps -q app):/app/uploads $BACKUP_DIR/
    
    # Create archive
    tar -czf $BACKUP_DIR.tar.gz -C backups $(basename $BACKUP_DIR)
    rm -rf $BACKUP_DIR
    
    log_success "Backup created: $BACKUP_DIR.tar.gz"
}

restore_data() {
    if [ -z "$2" ]; then
        log_error "Please specify backup file: $0 restore <backup_file>"
        exit 1
    fi
    
    BACKUP_FILE="$2"
    if [ ! -f "$BACKUP_FILE" ]; then
        log_error "Backup file not found: $BACKUP_FILE"
        exit 1
    fi
    
    log_warning "This will overwrite existing data"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Restoring from backup: $BACKUP_FILE"
        
        # Extract backup
        TEMP_DIR=$(mktemp -d)
        tar -xzf $BACKUP_FILE -C $TEMP_DIR
        
        # Restore database
        log_info "Restoring database..."
        docker-compose -f $COMPOSE_FILE exec -T db psql -U hospital_user -d hospital_crm < $TEMP_DIR/*/database.sql
        
        # Restore uploads
        log_info "Restoring uploads..."
        docker cp $TEMP_DIR/*/uploads $(docker-compose -f $COMPOSE_FILE ps -q app):/app/
        
        # Cleanup
        rm -rf $TEMP_DIR
        
        log_success "Restore completed"
    else
        log_info "Restore cancelled"
    fi
}

monitoring_up() {
    log_info "Starting monitoring stack..."
    docker-compose -f $COMPOSE_FILE --profile monitoring up -d
    log_success "Monitoring stack started"
    log_info "Services available at:"
    echo "  - Prometheus: http://localhost:9090"
    echo "  - Grafana: http://localhost:3000 (admin/admin_password_2024)"
}

monitoring_down() {
    log_info "Stopping monitoring stack..."
    docker-compose -f $COMPOSE_FILE --profile monitoring down
    log_success "Monitoring stack stopped"
}

# Main script logic
check_docker

case "$1" in
    "dev-up")
        dev_up
        ;;
    "dev-down")
        dev_down
        ;;
    "dev-logs")
        dev_logs "$@"
        ;;
    "dev-shell")
        dev_shell
        ;;
    "prod-up")
        prod_up
        ;;
    "prod-down")
        prod_down
        ;;
    "prod-logs")
        prod_logs "$@"
        ;;
    "prod-shell")
        prod_shell
        ;;
    "build")
        build_images
        ;;
    "rebuild")
        rebuild_images
        ;;
    "clean")
        clean_docker
        ;;
    "health")
        check_health
        ;;
    "backup")
        backup_data
        ;;
    "restore")
        restore_data "$@"
        ;;
    "monitoring-up")
        monitoring_up
        ;;
    "monitoring-down")
        monitoring_down
        ;;
    "-h"|"--help"|"help")
        show_help
        ;;
    *)
        log_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
