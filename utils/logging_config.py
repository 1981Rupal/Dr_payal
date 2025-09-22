# utils/logging_config.py - Advanced Logging Configuration

import os
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path
import json

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record):
        """Format log record as JSON"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'process_id': os.getpid(),
            'thread_id': record.thread,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        
        if hasattr(record, 'ip_address'):
            log_entry['ip_address'] = record.ip_address
        
        if hasattr(record, 'user_agent'):
            log_entry['user_agent'] = record.user_agent
        
        return json.dumps(log_entry)

class SecurityFilter(logging.Filter):
    """Filter to prevent logging of sensitive information"""
    
    SENSITIVE_PATTERNS = [
        'password', 'token', 'secret', 'key', 'auth',
        'credit_card', 'ssn', 'social_security'
    ]
    
    def filter(self, record):
        """Filter out sensitive information"""
        message = record.getMessage().lower()
        
        for pattern in self.SENSITIVE_PATTERNS:
            if pattern in message:
                record.msg = "[SENSITIVE DATA FILTERED]"
                record.args = ()
                break
        
        return True

def setup_logging(app):
    """Setup comprehensive logging for the application"""
    
    # Create logs directory
    log_dir = Path(app.config.get('LOG_FOLDER', 'logs'))
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    if app.config.get('LOG_TO_STDOUT', False):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        if app.config.get('LOG_FORMAT') == 'json':
            console_handler.setFormatter(JSONFormatter())
        else:
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
        
        console_handler.addFilter(SecurityFilter())
        root_logger.addHandler(console_handler)
    
    # File handlers
    if not app.config.get('LOG_TO_STDOUT', False):
        # Application log file
        app_log_file = log_dir / 'app.log'
        app_handler = logging.handlers.RotatingFileHandler(
            app_log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        app_handler.setLevel(logging.INFO)
        app_handler.setFormatter(JSONFormatter())
        app_handler.addFilter(SecurityFilter())
        root_logger.addHandler(app_handler)
        
        # Error log file
        error_log_file = log_dir / 'error.log'
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(JSONFormatter())
        error_handler.addFilter(SecurityFilter())
        root_logger.addHandler(error_handler)
        
        # Access log file
        access_log_file = log_dir / 'access.log'
        access_handler = logging.handlers.RotatingFileHandler(
            access_log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10
        )
        access_handler.setLevel(logging.INFO)
        access_handler.setFormatter(JSONFormatter())
        
        # Create access logger
        access_logger = logging.getLogger('access')
        access_logger.addHandler(access_handler)
        access_logger.setLevel(logging.INFO)
        access_logger.propagate = False
    
    # Security log file
    security_log_file = log_dir / 'security.log'
    security_handler = logging.handlers.RotatingFileHandler(
        security_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10
    )
    security_handler.setLevel(logging.WARNING)
    security_handler.setFormatter(JSONFormatter())
    
    # Create security logger
    security_logger = logging.getLogger('security')
    security_logger.addHandler(security_handler)
    security_logger.setLevel(logging.WARNING)
    security_logger.propagate = False
    
    # Performance log file
    performance_log_file = log_dir / 'performance.log'
    performance_handler = logging.handlers.RotatingFileHandler(
        performance_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    performance_handler.setLevel(logging.INFO)
    performance_handler.setFormatter(JSONFormatter())
    
    # Create performance logger
    performance_logger = logging.getLogger('performance')
    performance_logger.addHandler(performance_handler)
    performance_logger.setLevel(logging.INFO)
    performance_logger.propagate = False
    
    # Set specific logger levels
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    app.logger.info("Logging system initialized")

def log_request(request, response, duration):
    """Log HTTP request details"""
    access_logger = logging.getLogger('access')
    
    log_data = {
        'method': request.method,
        'url': request.url,
        'status_code': response.status_code,
        'duration_ms': round(duration * 1000, 2),
        'ip_address': request.remote_addr,
        'user_agent': request.headers.get('User-Agent', ''),
        'content_length': response.content_length or 0
    }
    
    # Add user info if available
    from flask_login import current_user
    if current_user and current_user.is_authenticated:
        log_data['user_id'] = current_user.id
        log_data['username'] = current_user.username
    
    access_logger.info("HTTP Request", extra=log_data)

def log_security_event(event_type, details, severity='WARNING'):
    """Log security-related events"""
    security_logger = logging.getLogger('security')
    
    log_data = {
        'event_type': event_type,
        'details': details,
        'severity': severity
    }
    
    if severity == 'CRITICAL':
        security_logger.critical("Security Event", extra=log_data)
    elif severity == 'ERROR':
        security_logger.error("Security Event", extra=log_data)
    else:
        security_logger.warning("Security Event", extra=log_data)

def log_performance_metric(metric_name, value, unit='ms', tags=None):
    """Log performance metrics"""
    performance_logger = logging.getLogger('performance')
    
    log_data = {
        'metric_name': metric_name,
        'value': value,
        'unit': unit,
        'tags': tags or {}
    }
    
    performance_logger.info("Performance Metric", extra=log_data)

def log_business_event(event_type, details, user_id=None):
    """Log business-related events"""
    app_logger = logging.getLogger('business')
    
    log_data = {
        'event_type': event_type,
        'details': details
    }
    
    if user_id:
        log_data['user_id'] = user_id
    
    app_logger.info("Business Event", extra=log_data)

class RequestLoggingMiddleware:
    """Middleware to log all HTTP requests"""
    
    def __init__(self, app):
        self.app = app
        self.app.before_request(self.before_request)
        self.app.after_request(self.after_request)
    
    def before_request(self):
        """Called before each request"""
        from flask import g
        import time
        g.start_time = time.time()
    
    def after_request(self, response):
        """Called after each request"""
        from flask import g, request
        import time
        
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            log_request(request, response, duration)
        
        return response
