#!/usr/bin/env python3
"""
Local Development Server for Dr. Payal's Hospital CRM
Run this script to start the application locally with SQLite database
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set default environment for local development
os.environ.setdefault('FLASK_ENV', 'development')
os.environ.setdefault('FLASK_DEBUG', 'True')
os.environ.setdefault('DATABASE_URL', 'sqlite:///hospital_crm.db')

def check_requirements():
    """Check if required packages are installed"""
    try:
        import flask
        import flask_sqlalchemy
        import flask_login
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        return False

def setup_database():
    """Initialize the database"""
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            from models import db
            db.create_all()
            print("✅ Database initialized successfully")
            return True
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def main():
    """Main function to start the local server"""
    print("🏥 Dr. Payal's Hospital CRM - Local Development Server")
    print("=" * 60)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Setup database
    if not setup_database():
        sys.exit(1)
    
    # Import and create app
    try:
        from app import create_app
        app = create_app()
        
        print("\n🚀 Starting development server...")
        print("📱 Access the application at: http://localhost:5000")
        print("👤 Default login credentials:")
        print("   Super Admin: superadmin / admin123")
        print("   Doctor: doctor / doctor123")
        print("   Staff: staff / staff123")
        print("\n💡 Press Ctrl+C to stop the server")
        print("=" * 60)
        
        # Run the development server
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000,
            use_reloader=True
        )
        
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
