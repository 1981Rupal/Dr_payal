#!/usr/bin/env python3
"""
Comprehensive health check script for Hospital CRM application
"""

import os
import sys
import time
import json
import logging
import requests
import psycopg2
import redis
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HealthChecker:
    def __init__(self):
        self.checks = []
        self.results = {}
        
    def add_check(self, name, check_func):
        """Add a health check function"""
        self.checks.append((name, check_func))
    
    def run_checks(self):
        """Run all health checks"""
        all_passed = True
        
        for name, check_func in self.checks:
            try:
                start_time = time.time()
                result = check_func()
                duration = time.time() - start_time
                
                self.results[name] = {
                    'status': 'healthy' if result else 'unhealthy',
                    'duration': round(duration, 3),
                    'timestamp': time.time()
                }
                
                if result:
                    logger.info(f"✓ {name} - healthy ({duration:.3f}s)")
                else:
                    logger.error(f"✗ {name} - unhealthy ({duration:.3f}s)")
                    all_passed = False
                    
            except Exception as e:
                self.results[name] = {
                    'status': 'error',
                    'error': str(e),
                    'timestamp': time.time()
                }
                logger.error(f"✗ {name} - error: {e}")
                all_passed = False
        
        return all_passed
    
    def get_results(self):
        """Get health check results"""
        return self.results

def check_database():
    """Check PostgreSQL database connectivity"""
    try:
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            return False
            
        parsed = urlparse(database_url)
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            database=parsed.path[1:],  # Remove leading slash
            user=parsed.username,
            password=parsed.password
        )
        
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return result[0] == 1
        
    except Exception as e:
        logger.error(f"Database check failed: {e}")
        return False

def check_redis():
    """Check Redis connectivity"""
    try:
        redis_url = os.getenv('REDIS_URL')
        if not redis_url:
            return False
            
        r = redis.from_url(redis_url)
        r.ping()
        return True
        
    except Exception as e:
        logger.error(f"Redis check failed: {e}")
        return False

def check_application():
    """Check application health endpoint"""
    try:
        app_url = os.getenv('APP_URL', 'http://localhost:5000')
        response = requests.get(f"{app_url}/health", timeout=10)
        return response.status_code == 200
        
    except Exception as e:
        logger.error(f"Application check failed: {e}")
        return False

def check_disk_space():
    """Check available disk space"""
    try:
        import shutil
        total, used, free = shutil.disk_usage('/')
        free_percent = (free / total) * 100
        
        # Consider healthy if more than 10% free space
        return free_percent > 10
        
    except Exception as e:
        logger.error(f"Disk space check failed: {e}")
        return False

def check_memory():
    """Check available memory"""
    try:
        with open('/proc/meminfo', 'r') as f:
            meminfo = f.read()
        
        lines = meminfo.split('\n')
        mem_total = None
        mem_available = None
        
        for line in lines:
            if line.startswith('MemTotal:'):
                mem_total = int(line.split()[1]) * 1024  # Convert to bytes
            elif line.startswith('MemAvailable:'):
                mem_available = int(line.split()[1]) * 1024  # Convert to bytes
        
        if mem_total and mem_available:
            usage_percent = ((mem_total - mem_available) / mem_total) * 100
            # Consider healthy if memory usage is below 90%
            return usage_percent < 90
        
        return False
        
    except Exception as e:
        logger.error(f"Memory check failed: {e}")
        return False

def check_file_permissions():
    """Check critical file permissions"""
    try:
        critical_paths = [
            '/app/logs',
            '/app/uploads',
            '/app/static/uploads'
        ]
        
        for path in critical_paths:
            if os.path.exists(path):
                if not os.access(path, os.R_OK | os.W_OK):
                    return False
        
        return True
        
    except Exception as e:
        logger.error(f"File permissions check failed: {e}")
        return False

def check_environment_variables():
    """Check required environment variables"""
    try:
        required_vars = [
            'DATABASE_URL',
            'SECRET_KEY',
            'FLASK_ENV'
        ]
        
        for var in required_vars:
            if not os.getenv(var):
                logger.error(f"Missing required environment variable: {var}")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"Environment variables check failed: {e}")
        return False

def main():
    """Main health check function"""
    checker = HealthChecker()
    
    # Add all health checks
    checker.add_check("Database", check_database)
    checker.add_check("Redis", check_redis)
    checker.add_check("Application", check_application)
    checker.add_check("Disk Space", check_disk_space)
    checker.add_check("Memory", check_memory)
    checker.add_check("File Permissions", check_file_permissions)
    checker.add_check("Environment Variables", check_environment_variables)
    
    # Run checks
    logger.info("Starting health checks...")
    all_healthy = checker.run_checks()
    
    # Output results
    results = checker.get_results()
    
    if os.getenv('OUTPUT_JSON', '').lower() == 'true':
        print(json.dumps(results, indent=2))
    
    # Summary
    healthy_count = sum(1 for r in results.values() if r['status'] == 'healthy')
    total_count = len(results)
    
    logger.info(f"Health check summary: {healthy_count}/{total_count} checks passed")
    
    if all_healthy:
        logger.info("All health checks passed ✓")
        sys.exit(0)
    else:
        logger.error("Some health checks failed ✗")
        sys.exit(1)

if __name__ == "__main__":
    main()
