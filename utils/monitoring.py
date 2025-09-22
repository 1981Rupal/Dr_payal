# utils/monitoring.py - Application Monitoring and Health Checks

import psutil
import time
import logging
from datetime import datetime, timedelta
from flask import jsonify, current_app
from sqlalchemy import text
from models import db
import redis
import requests

logger = logging.getLogger(__name__)

class HealthChecker:
    """Comprehensive health checking system"""
    
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app"""
        self.app = app
    
    def check_database(self):
        """Check database connectivity and performance"""
        try:
            start_time = time.time()
            
            # Simple query to test connection
            result = db.session.execute(text('SELECT 1'))
            result.fetchone()
            
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            # Check if response time is acceptable
            max_db_response_time = self.app.config.get('MAX_DB_RESPONSE_TIME_MS', 1000)
            
            if response_time > max_db_response_time:
                return {
                    'status': 'warning',
                    'message': f'Database response time high: {response_time:.2f}ms',
                    'response_time_ms': response_time
                }
            
            return {
                'status': 'healthy',
                'message': 'Database connection successful',
                'response_time_ms': response_time
            }
        
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                'status': 'unhealthy',
                'message': f'Database connection failed: {str(e)}',
                'response_time_ms': None
            }
    
    def check_redis(self):
        """Check Redis connectivity"""
        try:
            redis_url = self.app.config.get('REDIS_URL')
            if not redis_url:
                return {
                    'status': 'not_configured',
                    'message': 'Redis not configured'
                }
            
            start_time = time.time()
            
            # Connect to Redis
            r = redis.from_url(redis_url)
            
            # Test basic operations
            test_key = 'health_check_test'
            r.set(test_key, 'test_value', ex=10)  # Expire in 10 seconds
            value = r.get(test_key)
            r.delete(test_key)
            
            response_time = (time.time() - start_time) * 1000
            
            if value.decode() != 'test_value':
                return {
                    'status': 'unhealthy',
                    'message': 'Redis read/write test failed',
                    'response_time_ms': response_time
                }
            
            return {
                'status': 'healthy',
                'message': 'Redis connection successful',
                'response_time_ms': response_time
            }
        
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {
                'status': 'unhealthy',
                'message': f'Redis connection failed: {str(e)}',
                'response_time_ms': None
            }
    
    def check_disk_space(self):
        """Check available disk space"""
        try:
            disk_usage = psutil.disk_usage('/')
            
            # Calculate percentages
            used_percent = (disk_usage.used / disk_usage.total) * 100
            free_gb = disk_usage.free / (1024**3)  # Convert to GB
            
            # Thresholds
            warning_threshold = self.app.config.get('DISK_WARNING_THRESHOLD', 80)
            critical_threshold = self.app.config.get('DISK_CRITICAL_THRESHOLD', 90)
            
            if used_percent >= critical_threshold:
                status = 'critical'
                message = f'Disk space critically low: {used_percent:.1f}% used'
            elif used_percent >= warning_threshold:
                status = 'warning'
                message = f'Disk space low: {used_percent:.1f}% used'
            else:
                status = 'healthy'
                message = f'Disk space OK: {used_percent:.1f}% used'
            
            return {
                'status': status,
                'message': message,
                'used_percent': round(used_percent, 1),
                'free_gb': round(free_gb, 2),
                'total_gb': round(disk_usage.total / (1024**3), 2)
            }
        
        except Exception as e:
            logger.error(f"Disk space check failed: {e}")
            return {
                'status': 'error',
                'message': f'Disk space check failed: {str(e)}'
            }
    
    def check_memory_usage(self):
        """Check memory usage"""
        try:
            memory = psutil.virtual_memory()
            
            used_percent = memory.percent
            available_gb = memory.available / (1024**3)
            
            # Thresholds
            warning_threshold = self.app.config.get('MEMORY_WARNING_THRESHOLD', 80)
            critical_threshold = self.app.config.get('MEMORY_CRITICAL_THRESHOLD', 90)
            
            if used_percent >= critical_threshold:
                status = 'critical'
                message = f'Memory usage critically high: {used_percent:.1f}%'
            elif used_percent >= warning_threshold:
                status = 'warning'
                message = f'Memory usage high: {used_percent:.1f}%'
            else:
                status = 'healthy'
                message = f'Memory usage OK: {used_percent:.1f}%'
            
            return {
                'status': status,
                'message': message,
                'used_percent': round(used_percent, 1),
                'available_gb': round(available_gb, 2),
                'total_gb': round(memory.total / (1024**3), 2)
            }
        
        except Exception as e:
            logger.error(f"Memory check failed: {e}")
            return {
                'status': 'error',
                'message': f'Memory check failed: {str(e)}'
            }
    
    def check_cpu_usage(self):
        """Check CPU usage"""
        try:
            # Get CPU usage over a short interval
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Thresholds
            warning_threshold = self.app.config.get('CPU_WARNING_THRESHOLD', 80)
            critical_threshold = self.app.config.get('CPU_CRITICAL_THRESHOLD', 90)
            
            if cpu_percent >= critical_threshold:
                status = 'critical'
                message = f'CPU usage critically high: {cpu_percent:.1f}%'
            elif cpu_percent >= warning_threshold:
                status = 'warning'
                message = f'CPU usage high: {cpu_percent:.1f}%'
            else:
                status = 'healthy'
                message = f'CPU usage OK: {cpu_percent:.1f}%'
            
            return {
                'status': status,
                'message': message,
                'usage_percent': round(cpu_percent, 1),
                'cpu_count': cpu_count
            }
        
        except Exception as e:
            logger.error(f"CPU check failed: {e}")
            return {
                'status': 'error',
                'message': f'CPU check failed: {str(e)}'
            }
    
    def check_external_services(self):
        """Check external service dependencies"""
        services = {}
        
        # Check WhatsApp service if enabled
        if self.app.config.get('ENABLE_WHATSAPP', False):
            whatsapp_url = self.app.config.get('WHATSAPP_API_URL')
            if whatsapp_url:
                services['whatsapp'] = self._check_http_service(whatsapp_url, 'WhatsApp API')
        
        # Check email service if enabled
        if self.app.config.get('ENABLE_EMAIL_NOTIFICATIONS', False):
            smtp_server = self.app.config.get('MAIL_SERVER')
            if smtp_server:
                services['email'] = self._check_smtp_service(smtp_server, 'Email Service')
        
        return services
    
    def _check_http_service(self, url, service_name, timeout=5):
        """Check HTTP service availability"""
        try:
            start_time = time.time()
            response = requests.get(url, timeout=timeout)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                return {
                    'status': 'healthy',
                    'message': f'{service_name} is responding',
                    'response_time_ms': response_time,
                    'status_code': response.status_code
                }
            else:
                return {
                    'status': 'unhealthy',
                    'message': f'{service_name} returned status {response.status_code}',
                    'response_time_ms': response_time,
                    'status_code': response.status_code
                }
        
        except requests.exceptions.Timeout:
            return {
                'status': 'unhealthy',
                'message': f'{service_name} timeout after {timeout}s'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'{service_name} check failed: {str(e)}'
            }
    
    def _check_smtp_service(self, smtp_server, service_name):
        """Check SMTP service availability"""
        try:
            import smtplib
            import socket
            
            start_time = time.time()
            
            # Try to connect to SMTP server
            server = smtplib.SMTP(smtp_server, timeout=5)
            server.quit()
            
            response_time = (time.time() - start_time) * 1000
            
            return {
                'status': 'healthy',
                'message': f'{service_name} is responding',
                'response_time_ms': response_time
            }
        
        except socket.timeout:
            return {
                'status': 'unhealthy',
                'message': f'{service_name} connection timeout'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'{service_name} check failed: {str(e)}'
            }
    
    def get_comprehensive_health(self):
        """Get comprehensive health status"""
        health_checks = {
            'timestamp': datetime.utcnow().isoformat(),
            'application': {
                'status': 'healthy',
                'version': self.app.config.get('VERSION', '1.0.0'),
                'environment': self.app.config.get('FLASK_ENV', 'production')
            },
            'database': self.check_database(),
            'redis': self.check_redis(),
            'system': {
                'disk': self.check_disk_space(),
                'memory': self.check_memory_usage(),
                'cpu': self.check_cpu_usage()
            },
            'external_services': self.check_external_services()
        }
        
        # Determine overall status
        overall_status = 'healthy'
        
        # Check each component
        for component, status in health_checks.items():
            if isinstance(status, dict) and 'status' in status:
                if status['status'] in ['critical', 'unhealthy']:
                    overall_status = 'unhealthy'
                    break
                elif status['status'] == 'warning' and overall_status == 'healthy':
                    overall_status = 'warning'
            elif isinstance(status, dict):
                # Check nested components
                for sub_component, sub_status in status.items():
                    if isinstance(sub_status, dict) and 'status' in sub_status:
                        if sub_status['status'] in ['critical', 'unhealthy']:
                            overall_status = 'unhealthy'
                            break
                        elif sub_status['status'] == 'warning' and overall_status == 'healthy':
                            overall_status = 'warning'
        
        health_checks['overall_status'] = overall_status
        
        return health_checks

class MetricsCollector:
    """Collect application metrics"""
    
    def __init__(self, app=None):
        self.app = app
        self.metrics = {}
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app"""
        self.app = app
    
    def collect_request_metrics(self):
        """Collect request-related metrics"""
        # This would typically integrate with a metrics system like Prometheus
        # For now, we'll return basic metrics
        
        return {
            'active_connections': self._get_active_connections(),
            'request_rate': self._get_request_rate(),
            'error_rate': self._get_error_rate(),
            'response_time_avg': self._get_avg_response_time()
        }
    
    def _get_active_connections(self):
        """Get number of active connections"""
        try:
            connections = psutil.net_connections(kind='inet')
            return len([c for c in connections if c.status == 'ESTABLISHED'])
        except:
            return 0
    
    def _get_request_rate(self):
        """Get request rate (requests per minute)"""
        # This would need to be implemented with actual request tracking
        return 0
    
    def _get_error_rate(self):
        """Get error rate percentage"""
        # This would need to be implemented with actual error tracking
        return 0
    
    def _get_avg_response_time(self):
        """Get average response time"""
        # This would need to be implemented with actual response time tracking
        return 0
