# main.py - Main Application Entry Point

import os
import sys
from flask import Flask
from datetime import datetime, timezone

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Basic configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL',
        'sqlite:///hospital_crm.db'  # Use SQLite for local development
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    from models import db
    db.init_app(app)
    
    # Initialize Flask-Login
    from flask_login import LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return db.session.get(User, int(user_id))
    
    # Register blueprints
    try:
        from routes.auth import auth_bp
        from routes.main import main_bp
        from routes.patients import patients_bp
        from routes.appointments import appointments_bp
        from routes.billing import billing_bp
        from routes.api import api_bp
        
        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(main_bp)
        app.register_blueprint(patients_bp, url_prefix='/patients')
        app.register_blueprint(appointments_bp, url_prefix='/appointments')
        app.register_blueprint(billing_bp, url_prefix='/billing')
        app.register_blueprint(api_bp, url_prefix='/api')
    except ImportError as e:
        print(f"Warning: Could not import some blueprints: {e}")
        # Create basic routes if blueprints fail
        create_basic_routes(app)
    
    # Create database tables and default data
    with app.app_context():
        try:
            db.create_all()
            create_default_data()
            print("✅ Database initialized successfully!")
        except Exception as e:
            print(f"❌ Database initialization error: {e}")
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        try:
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            return {
                'status': 'healthy',
                'database': 'connected',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }, 200
        except Exception as e:
            return {
                'status': 'unhealthy',
                'database': 'disconnected',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }, 500
    
    return app

def create_basic_routes(app):
    """Create basic routes if blueprints are not available"""
    from flask import render_template, redirect, url_for, request, flash
    from flask_login import login_user, logout_user, login_required, current_user
    
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return render_template('dashboard/main.html', stats={}, recent_activities=[])
        return redirect(url_for('login'))
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            from models import User
            username = request.form.get('username')
            password = request.form.get('password')
            
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password) and user.is_active:
                login_user(user)
                user.last_login = datetime.now(timezone.utc)
                from models import db
                db.session.commit()
                flash(f'Welcome back, {user.full_name}!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password.', 'error')
        
        return render_template('auth/login.html')
    
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out successfully.', 'info')
        return redirect(url_for('login'))

def create_default_data():
    """Create default users and system settings"""
    from models import db, User, UserRole, SystemSetting, TreatmentPackage
    
    try:
        # Create super admin if not exists
        if not User.query.filter_by(username='superadmin').first():
            super_admin = User(
                username='superadmin',
                email='admin@hospital.com',
                first_name='Super',
                last_name='Admin',
                role=UserRole.SUPER_ADMIN,
                phone='+1234567890'
            )
            super_admin.set_password('admin123')
            db.session.add(super_admin)
        
        # Create default doctor
        if not User.query.filter_by(username='doctor').first():
            doctor = User(
                username='doctor',
                email='doctor@hospital.com',
                first_name='Dr. John',
                last_name='Smith',
                role=UserRole.DOCTOR,
                phone='+1234567891'
            )
            doctor.set_password('doctor123')
            db.session.add(doctor)
        
        # Create staff user
        if not User.query.filter_by(username='staff').first():
            staff = User(
                username='staff',
                email='staff@hospital.com',
                first_name='Staff',
                last_name='Member',
                role=UserRole.STAFF,
                phone='+1234567892'
            )
            staff.set_password('staff123')
            db.session.add(staff)
        
        # Create default treatment packages
        if not TreatmentPackage.query.first():
            packages = [
                {
                    'name': 'Physiotherapy Basic Package',
                    'description': 'Basic physiotherapy sessions for general treatment',
                    'total_sessions': 10,
                    'price_per_session': 500.0,
                    'total_price': 4500.0,
                    'validity_days': 90
                },
                {
                    'name': 'Physiotherapy Premium Package',
                    'description': 'Premium physiotherapy sessions with advanced treatment',
                    'total_sessions': 20,
                    'price_per_session': 600.0,
                    'total_price': 10800.0,
                    'validity_days': 120
                }
            ]
            
            for pkg_data in packages:
                package = TreatmentPackage(**pkg_data)
                db.session.add(package)
        
        db.session.commit()
        print("✅ Default data created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating default data: {e}")
        db.session.rollback()

if __name__ == '__main__':
    app = create_app()
    print("🏥 Starting Dr. Payal's Hospital CRM...")
    print("📱 Access the application at: http://localhost:5000")
    print("👤 Login credentials:")
    print("   Super Admin: superadmin / admin123")
    print("   Doctor: doctor / doctor123")
    print("   Staff: staff / staff123")
    app.run(debug=True, host='0.0.0.0', port=5000)
