# tests/test_config.py - Configuration Tests

import pytest
import os
import tempfile
from config import Config, DevelopmentConfig, ProductionConfig, TestingConfig, RenderConfig

class TestConfiguration:
    """Test application configuration classes"""
    
    def test_base_config(self):
        """Test base configuration"""
        config = Config()
        
        # Test default values
        assert config.SQLALCHEMY_TRACK_MODIFICATIONS == False
        assert config.UPLOAD_FOLDER is not None
        assert config.MAX_CONTENT_LENGTH == 16 * 1024 * 1024  # 16MB
        assert config.WTF_CSRF_ENABLED == True
    
    def test_development_config(self):
        """Test development configuration"""
        config = DevelopmentConfig()
        
        assert config.DEBUG == True
        assert config.TESTING == False
        assert config.SQLALCHEMY_ECHO == True
        assert config.SESSION_COOKIE_SECURE == False
        assert config.WTF_CSRF_ENABLED == False
    
    def test_production_config(self):
        """Test production configuration"""
        config = ProductionConfig()
        
        assert config.DEBUG == False
        assert config.TESTING == False
        assert config.SQLALCHEMY_ECHO == False
        assert config.SESSION_COOKIE_SECURE == True
        assert config.WTF_CSRF_ENABLED == True
    
    def test_testing_config(self):
        """Test testing configuration"""
        config = TestingConfig()
        
        assert config.DEBUG == True
        assert config.TESTING == True
        assert config.WTF_CSRF_ENABLED == False
        assert config.SQLALCHEMY_ECHO == False
        assert config.ENABLE_WHATSAPP == False
        assert config.ENABLE_CHATBOT == False
        assert config.ENABLE_EMAIL_NOTIFICATIONS == False
    
    def test_render_config(self):
        """Test Render configuration"""
        config = RenderConfig()
        
        assert config.PREFERRED_URL_SCHEME == 'https'
        assert config.SESSION_COOKIE_SECURE == True
        assert config.SESSION_COOKIE_HTTPONLY == True
        assert config.SESSION_COOKIE_SAMESITE == 'Lax'
        assert config.LOG_TO_STDOUT == True
    
    def test_environment_variables(self):
        """Test configuration from environment variables"""
        # Set test environment variables
        test_vars = {
            'SECRET_KEY': 'test-secret-key',
            'DATABASE_URL': 'postgresql://test:test@localhost/test',
            'REDIS_URL': 'redis://localhost:6379/1',
            'UPLOAD_FOLDER': '/tmp/test_uploads'
        }
        
        # Set environment variables
        for key, value in test_vars.items():
            os.environ[key] = value
        
        try:
            config = Config()
            
            assert config.SECRET_KEY == 'test-secret-key'
            assert config.UPLOAD_FOLDER == '/tmp/test_uploads'
            
        finally:
            # Clean up environment variables
            for key in test_vars.keys():
                if key in os.environ:
                    del os.environ[key]
    
    def test_config_selection(self):
        """Test configuration selection based on environment"""
        from config import get_config
        
        # Test default config
        config_class = get_config()
        assert config_class == DevelopmentConfig
        
        # Test specific environment
        os.environ['FLASK_ENV'] = 'production'
        try:
            config_class = get_config()
            assert config_class == ProductionConfig
        finally:
            if 'FLASK_ENV' in os.environ:
                del os.environ['FLASK_ENV']
    
    def test_database_url_validation(self):
        """Test database URL validation and formatting"""
        # Test PostgreSQL URL formatting for Render
        test_url = 'postgres://user:pass@host:5432/db'
        os.environ['DATABASE_URL'] = test_url
        
        try:
            config = RenderConfig()
            RenderConfig.init_database_url()
            
            # Should convert postgres:// to postgresql://
            assert config.SQLALCHEMY_DATABASE_URI.startswith('postgresql://')
            
        finally:
            if 'DATABASE_URL' in os.environ:
                del os.environ['DATABASE_URL']

class TestConfigurationSecurity:
    """Test security-related configuration"""
    
    def test_secret_key_requirements(self):
        """Test secret key requirements"""
        config = Config()
        
        # Should have a secret key
        assert config.SECRET_KEY is not None
        assert len(config.SECRET_KEY) > 0
    
    def test_production_security_settings(self):
        """Test production security settings"""
        config = ProductionConfig()
        
        # Security settings should be enabled in production
        assert config.SESSION_COOKIE_SECURE == True
        assert config.WTF_CSRF_ENABLED == True
    
    def test_development_security_relaxed(self):
        """Test that development has relaxed security for testing"""
        config = DevelopmentConfig()
        
        # Some security features should be relaxed for development
        assert config.SESSION_COOKIE_SECURE == False
        assert config.WTF_CSRF_ENABLED == False
    
    def test_render_security_hardened(self):
        """Test that Render config has hardened security"""
        config = RenderConfig()
        
        assert config.SESSION_COOKIE_SECURE == True
        assert config.SESSION_COOKIE_HTTPONLY == True
        assert config.SESSION_COOKIE_SAMESITE == 'Lax'
        assert config.PREFERRED_URL_SCHEME == 'https'

class TestConfigurationValidation:
    """Test configuration validation"""
    
    def test_required_settings_present(self):
        """Test that required settings are present"""
        configs = [DevelopmentConfig(), ProductionConfig(), TestingConfig(), RenderConfig()]
        
        required_settings = [
            'SECRET_KEY',
            'SQLALCHEMY_DATABASE_URI',
            'UPLOAD_FOLDER',
            'MAX_CONTENT_LENGTH'
        ]
        
        for config in configs:
            for setting in required_settings:
                assert hasattr(config, setting)
                assert getattr(config, setting) is not None
    
    def test_upload_folder_creation(self):
        """Test upload folder creation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_upload_folder = os.path.join(temp_dir, 'test_uploads')
            
            os.environ['UPLOAD_FOLDER'] = test_upload_folder
            
            try:
                config = Config()
                
                # Create the upload folder if it doesn't exist
                if not os.path.exists(config.UPLOAD_FOLDER):
                    os.makedirs(config.UPLOAD_FOLDER)
                
                assert os.path.exists(config.UPLOAD_FOLDER)
                assert os.path.isdir(config.UPLOAD_FOLDER)
                
            finally:
                if 'UPLOAD_FOLDER' in os.environ:
                    del os.environ['UPLOAD_FOLDER']
    
    def test_database_url_formats(self):
        """Test various database URL formats"""
        test_urls = [
            'postgresql://user:pass@localhost:5432/db',
            'postgres://user:pass@localhost:5432/db',
            'sqlite:///test.db'
        ]
        
        for url in test_urls:
            os.environ['DATABASE_URL'] = url
            
            try:
                config = Config()
                assert config.SQLALCHEMY_DATABASE_URI == url
                
            finally:
                if 'DATABASE_URL' in os.environ:
                    del os.environ['DATABASE_URL']

class TestFeatureFlags:
    """Test feature flag configuration"""
    
    def test_feature_flags_default(self):
        """Test default feature flag values"""
        config = Config()
        
        # Default feature flags
        assert config.ENABLE_WHATSAPP == True
        assert config.ENABLE_CHATBOT == True
        assert config.ENABLE_EMAIL_NOTIFICATIONS == True
        assert config.ENABLE_ONLINE_CONSULTATIONS == True
    
    def test_feature_flags_testing(self):
        """Test feature flags in testing environment"""
        config = TestingConfig()
        
        # Features should be disabled in testing
        assert config.ENABLE_WHATSAPP == False
        assert config.ENABLE_CHATBOT == False
        assert config.ENABLE_EMAIL_NOTIFICATIONS == False
    
    def test_feature_flags_environment_override(self):
        """Test feature flag override from environment"""
        os.environ['ENABLE_WHATSAPP'] = 'false'
        os.environ['ENABLE_CHATBOT'] = 'false'
        
        try:
            config = Config()
            
            # Should respect environment variables
            assert config.ENABLE_WHATSAPP == False
            assert config.ENABLE_CHATBOT == False
            
        finally:
            # Clean up
            for key in ['ENABLE_WHATSAPP', 'ENABLE_CHATBOT']:
                if key in os.environ:
                    del os.environ[key]
