# utils/security.py - Security Enhancement Module

import hashlib
import secrets
import logging
import re
from datetime import datetime, timedelta
from functools import wraps
from flask import request, abort, current_app, session, g
from flask_login import current_user
from collections import defaultdict
import ipaddress

logger = logging.getLogger(__name__)

class SecurityManager:
    """Comprehensive security management system"""
    
    def __init__(self, app=None):
        self.app = app
        self.failed_attempts = defaultdict(list)
        self.blocked_ips = set()
        self.suspicious_activities = defaultdict(list)
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app"""
        self.app = app
        
        # Security configuration
        self.max_login_attempts = app.config.get('MAX_LOGIN_ATTEMPTS', 5)
        self.lockout_duration = app.config.get('LOCKOUT_DURATION_MINUTES', 15)
        self.rate_limit_requests = app.config.get('RATE_LIMIT_REQUESTS', 100)
        self.rate_limit_window = app.config.get('RATE_LIMIT_WINDOW_MINUTES', 15)
        
        # Setup security middleware
        app.before_request(self.before_request_security_check)
        app.after_request(self.after_request_security_headers)
    
    def before_request_security_check(self):
        """Security checks before each request"""
        client_ip = self.get_client_ip()
        
        # Check if IP is blocked
        if self.is_ip_blocked(client_ip):
            logger.warning(f"Blocked IP attempted access: {client_ip}")
            abort(403)
        
        # Rate limiting
        if self.is_rate_limited(client_ip):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            abort(429)
        
        # Store request info for logging
        g.client_ip = client_ip
        g.request_start_time = datetime.utcnow()
    
    def after_request_security_headers(self, response):
        """Add security headers to response"""
        # Security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "img-src 'self' data: https:; "
            "font-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        response.headers['Content-Security-Policy'] = csp
        
        return response
    
    def get_client_ip(self):
        """Get the real client IP address"""
        # Check for forwarded headers (for proxy/load balancer setups)
        if request.headers.get('X-Forwarded-For'):
            # Get the first IP in the chain
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            return request.headers.get('X-Real-IP')
        else:
            return request.remote_addr
    
    def is_ip_blocked(self, ip_address):
        """Check if IP address is blocked"""
        return ip_address in self.blocked_ips
    
    def block_ip(self, ip_address, reason="Security violation"):
        """Block an IP address"""
        self.blocked_ips.add(ip_address)
        logger.warning(f"IP blocked: {ip_address}, Reason: {reason}")
        
        # Log security event
        from utils.logging_config import log_security_event
        log_security_event(
            'IP_BLOCKED',
            {'ip_address': ip_address, 'reason': reason},
            'ERROR'
        )
    
    def is_rate_limited(self, ip_address):
        """Check if IP is rate limited"""
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=self.rate_limit_window)
        
        # Clean old entries
        self.failed_attempts[ip_address] = [
            timestamp for timestamp in self.failed_attempts[ip_address]
            if timestamp > window_start
        ]
        
        # Check if rate limit exceeded
        return len(self.failed_attempts[ip_address]) >= self.rate_limit_requests
    
    def record_failed_login(self, username, ip_address):
        """Record a failed login attempt"""
        now = datetime.utcnow()
        
        # Record the attempt
        self.failed_attempts[ip_address].append(now)
        
        # Clean old attempts
        cutoff_time = now - timedelta(minutes=self.lockout_duration)
        self.failed_attempts[ip_address] = [
            timestamp for timestamp in self.failed_attempts[ip_address]
            if timestamp > cutoff_time
        ]
        
        # Check if should block IP
        if len(self.failed_attempts[ip_address]) >= self.max_login_attempts:
            self.block_ip(ip_address, f"Too many failed login attempts for user: {username}")
        
        # Log security event
        from utils.logging_config import log_security_event
        log_security_event(
            'FAILED_LOGIN',
            {
                'username': username,
                'ip_address': ip_address,
                'attempt_count': len(self.failed_attempts[ip_address])
            },
            'WARNING'
        )
    
    def record_successful_login(self, username, ip_address):
        """Record a successful login"""
        # Clear failed attempts for this IP
        if ip_address in self.failed_attempts:
            del self.failed_attempts[ip_address]
        
        # Log security event
        from utils.logging_config import log_security_event
        log_security_event(
            'SUCCESSFUL_LOGIN',
            {'username': username, 'ip_address': ip_address},
            'INFO'
        )
    
    def validate_password_strength(self, password):
        """Validate password strength"""
        errors = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        
        # Check for common passwords
        common_passwords = [
            'password', '123456', 'password123', 'admin', 'qwerty',
            'letmein', 'welcome', 'monkey', '1234567890'
        ]
        
        if password.lower() in common_passwords:
            errors.append("Password is too common")
        
        return errors
    
    def generate_secure_token(self, length=32):
        """Generate a cryptographically secure random token"""
        return secrets.token_urlsafe(length)
    
    def hash_sensitive_data(self, data):
        """Hash sensitive data for storage"""
        salt = secrets.token_hex(16)
        hashed = hashlib.pbkdf2_hmac('sha256', data.encode(), salt.encode(), 100000)
        return f"{salt}:{hashed.hex()}"
    
    def verify_hashed_data(self, data, hashed_data):
        """Verify hashed sensitive data"""
        try:
            salt, hash_hex = hashed_data.split(':')
            hashed = hashlib.pbkdf2_hmac('sha256', data.encode(), salt.encode(), 100000)
            return hashed.hex() == hash_hex
        except ValueError:
            return False

def require_role(required_role):
    """Decorator to require specific user role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            
            if not current_user.has_role(required_role):
                logger.warning(
                    f"Unauthorized access attempt by user {current_user.username} "
                    f"to role-restricted endpoint requiring {required_role}"
                )
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_permission(permission):
    """Decorator to require specific permission"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            
            if not current_user.has_permission(permission):
                logger.warning(
                    f"Unauthorized access attempt by user {current_user.username} "
                    f"to permission-restricted endpoint requiring {permission}"
                )
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def audit_log(action):
    """Decorator to log user actions for audit trail"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Execute the function
            result = f(*args, **kwargs)
            
            # Log the action
            if current_user.is_authenticated:
                from models import AuditLog, db
                
                audit_entry = AuditLog(
                    user_id=current_user.id,
                    action=action,
                    details=f"Endpoint: {request.endpoint}, Method: {request.method}",
                    ip_address=g.get('client_ip', request.remote_addr),
                    user_agent=request.headers.get('User-Agent', '')
                )
                
                try:
                    db.session.add(audit_entry)
                    db.session.commit()
                except Exception as e:
                    logger.error(f"Failed to log audit entry: {e}")
                    db.session.rollback()
            
            return result
        return decorated_function
    return decorator

def sanitize_input(input_string):
    """Sanitize user input to prevent XSS and injection attacks"""
    if not isinstance(input_string, str):
        return input_string
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', input_string)
    
    # Remove SQL injection patterns
    sql_patterns = [
        r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)',
        r'(--|#|/\*|\*/)',
        r'(\bOR\b.*=.*\bOR\b)',
        r'(\bAND\b.*=.*\bAND\b)'
    ]
    
    for pattern in sql_patterns:
        sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
    
    return sanitized.strip()

def validate_file_upload(file):
    """Validate uploaded files for security"""
    if not file or not file.filename:
        return False, "No file selected"
    
    # Check file extension
    allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {
        'images': ['jpg', 'jpeg', 'png', 'gif'],
        'documents': ['pdf', 'doc', 'docx', 'txt'],
        'data': ['csv', 'xlsx']
    })
    
    all_allowed = []
    for ext_list in allowed_extensions.values():
        all_allowed.extend(ext_list)
    
    file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    
    if file_ext not in all_allowed:
        return False, f"File type '{file_ext}' not allowed"
    
    # Check file size
    max_size = current_app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)  # 16MB
    
    # Read file content to check size and content
    file.seek(0, 2)  # Seek to end
    file_size = file.tell()
    file.seek(0)  # Reset to beginning
    
    if file_size > max_size:
        return False, f"File too large. Maximum size: {max_size // (1024*1024)}MB"
    
    # Basic content validation
    if file_ext in ['jpg', 'jpeg', 'png', 'gif']:
        # Check if it's actually an image
        try:
            from PIL import Image
            Image.open(file)
            file.seek(0)  # Reset for actual upload
        except Exception:
            return False, "Invalid image file"
    
    return True, "File is valid"
