# config.py - Configuration settings for Hospital CRM

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    
    # File upload settings
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16777216))  # 16MB
    ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'gif', 'doc', 'docx'}
    
    # Security settings
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = os.environ.get('SESSION_COOKIE_HTTPONLY', 'True').lower() == 'true'
    SESSION_COOKIE_SAMESITE = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')
    WTF_CSRF_ENABLED = os.environ.get('WTF_CSRF_ENABLED', 'True').lower() == 'true'
    
    # Email settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@drpayal.com')
    
    # Twilio settings
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_WHATSAPP_NUMBER = os.environ.get('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')
    
    # OpenAI settings
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # Redis settings
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # Feature flags
    ENABLE_WHATSAPP = os.environ.get('ENABLE_WHATSAPP', 'True').lower() == 'true'
    ENABLE_CHATBOT = os.environ.get('ENABLE_CHATBOT', 'True').lower() == 'true'
    ENABLE_ONLINE_CONSULTATION = os.environ.get('ENABLE_ONLINE_CONSULTATION', 'True').lower() == 'true'
    ENABLE_PAYMENT_GATEWAY = os.environ.get('ENABLE_PAYMENT_GATEWAY', 'True').lower() == 'true'
    ENABLE_EMAIL_NOTIFICATIONS = os.environ.get('ENABLE_EMAIL_NOTIFICATIONS', 'True').lower() == 'true'
    ENABLE_SMS_NOTIFICATIONS = os.environ.get('ENABLE_SMS_NOTIFICATIONS', 'True').lower() == 'true'
    
    # Clinic settings
    CLINIC_NAME = os.environ.get('CLINIC_NAME', "Dr. Payal's Physiotherapy Clinic")
    CLINIC_ADDRESS = os.environ.get('CLINIC_ADDRESS', '123 Health Street, Medical City, MC 12345')
    CLINIC_PHONE = os.environ.get('CLINIC_PHONE', '+1234567890')
    CLINIC_EMAIL = os.environ.get('CLINIC_EMAIL', 'info@drpayal.com')
    
    # Appointment settings
    DEFAULT_APPOINTMENT_DURATION = int(os.environ.get('DEFAULT_APPOINTMENT_DURATION', 30))
    WORKING_HOURS_START = os.environ.get('WORKING_HOURS_START', '09:00')
    WORKING_HOURS_END = os.environ.get('WORKING_HOURS_END', '18:00')
    WORKING_DAYS = os.environ.get('WORKING_DAYS', 'Monday,Tuesday,Wednesday,Thursday,Friday,Saturday').split(',')
    
    # Payment gateway settings
    RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID')
    RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET')
    STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    
    # Monitoring settings
    SENTRY_DSN = os.environ.get('SENTRY_DSN')
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Backup settings
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_S3_BUCKET = os.environ.get('AWS_S3_BUCKET')
    AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://hospital_user:hospital_password_2024@localhost:5432/hospital_crm'
    
    # Development-specific settings
    SQLALCHEMY_ECHO = True  # Log SQL queries
    SESSION_COOKIE_SECURE = False  # Allow HTTP in development
    WTF_CSRF_ENABLED = False  # Disable CSRF for easier testing

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://hospital_user:hospital_password_2024@db:5432/hospital_crm'
    
    # Production-specific settings
    SQLALCHEMY_ECHO = False
    SESSION_COOKIE_SECURE = True  # Require HTTPS
    WTF_CSRF_ENABLED = True
    
    # Logging
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'postgresql://hospital_user:hospital_password_2024@localhost:5432/hospital_crm_test'
    
    # Testing-specific settings
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_ECHO = False
    
    # Disable external services in testing
    ENABLE_WHATSAPP = False
    ENABLE_CHATBOT = False
    ENABLE_EMAIL_NOTIFICATIONS = False

class RenderConfig(ProductionConfig):
    """Render.com specific configuration"""

    # Render provides DATABASE_URL automatically
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    # Fix for Render's PostgreSQL URL format
    @classmethod
    def init_database_url(cls):
        if cls.SQLALCHEMY_DATABASE_URI and cls.SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
            cls.SQLALCHEMY_DATABASE_URI = cls.SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)

    # Render provides Redis URL automatically
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

    # File uploads on Render
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/opt/render/project/src/uploads')

    # Render-specific settings
    PREFERRED_URL_SCHEME = 'https'
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Security headers
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year

    # Render disk storage
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB

    # Logging configuration for Render
    LOG_TO_STDOUT = True
    LOG_LEVEL = 'INFO'

    @staticmethod
    def init_app(app):
        ProductionConfig.init_app(app)

        # Fix database URL format
        RenderConfig.init_database_url()

        # Handle proxy headers
        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'render': RenderConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on environment"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])
