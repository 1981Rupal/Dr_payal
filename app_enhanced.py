# app_enhanced.py - Enhanced Hospital CRM Application

import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash
from datetime import datetime, date, timedelta
import uuid
from functools import wraps
import json

# Import our enhanced models
from models import (
    db, User, Patient, Visit, Appointment, TreatmentPackage, PatientPackage,
    Billing, Payment, Prescription, PrescriptionMedication, OnlineConsultation,
    ChatbotConversation, ChatbotMessage, WhatsAppMessage, SystemSetting, AuditLog,
    UserRole, AppointmentStatus, PaymentStatus, VisitType, ConsultationStatus
)

# Import services
from services.whatsapp_service import WhatsAppService
from services.chatbot_service import ChatbotService
from services.appointment_service import AppointmentService
from services.billing_service import BillingService

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 
        'postgresql://user:password@localhost/hospital_crm'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Flask-Login setup
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Role-based access decorator
    def role_required(*roles):
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not current_user.is_authenticated:
                    return redirect(url_for('auth.login'))
                if current_user.role not in roles:
                    flash('You do not have permission to access this page.', 'error')
                    return redirect(url_for('main.dashboard'))
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    # Initialize services
    whatsapp_service = WhatsAppService()
    chatbot_service = ChatbotService()
    appointment_service = AppointmentService()
    billing_service = BillingService()
    
    # Create tables and default data
    @app.before_first_request
    def create_tables():
        db.create_all()
        create_default_data()
    
    def create_default_data():
        """Create default users and system settings"""
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
        
        # Create default treatment packages
        if not TreatmentPackage.query.first():
            packages = [
                {
                    'name': 'Physiotherapy Basic Package',
                    'description': 'Basic physiotherapy sessions for general treatment',
                    'total_sessions': 10,
                    'price_per_session': 500.0,
                    'total_price': 4500.0,  # 10% discount
                    'validity_days': 90
                },
                {
                    'name': 'Physiotherapy Premium Package',
                    'description': 'Premium physiotherapy sessions with advanced treatment',
                    'total_sessions': 20,
                    'price_per_session': 600.0,
                    'total_price': 10800.0,  # 10% discount
                    'validity_days': 120
                },
                {
                    'name': 'Home Visit Package',
                    'description': 'Home visit physiotherapy sessions',
                    'total_sessions': 8,
                    'price_per_session': 800.0,
                    'total_price': 6000.0,  # 6.25% discount
                    'validity_days': 60
                }
            ]
            
            for pkg_data in packages:
                package = TreatmentPackage(**pkg_data)
                db.session.add(package)
        
        # Create default system settings
        default_settings = [
            ('clinic_name', 'Dr. Payal\'s Physiotherapy Clinic', 'Name of the clinic'),
            ('clinic_address', '123 Health Street, Medical City, MC 12345', 'Clinic address'),
            ('clinic_phone', '+1234567890', 'Clinic contact number'),
            ('clinic_email', 'info@drpayal.com', 'Clinic email address'),
            ('appointment_duration', '30', 'Default appointment duration in minutes'),
            ('working_hours_start', '09:00', 'Clinic opening time'),
            ('working_hours_end', '18:00', 'Clinic closing time'),
            ('working_days', 'Monday,Tuesday,Wednesday,Thursday,Friday,Saturday', 'Working days'),
            ('whatsapp_enabled', 'true', 'Enable WhatsApp notifications'),
            ('chatbot_enabled', 'true', 'Enable AI chatbot'),
            ('online_consultation_enabled', 'true', 'Enable online consultations')
        ]
        
        for key, value, description in default_settings:
            if not SystemSetting.query.filter_by(key=key).first():
                setting = SystemSetting(key=key, value=value, description=description)
                db.session.add(setting)
        
        db.session.commit()
    
    # Authentication routes
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username).first()
            
            if user and user.check_password(password) and user.is_active:
                login_user(user)
                user.last_login = datetime.utcnow()
                db.session.commit()
                
                # Log the login
                audit_log = AuditLog(
                    user_id=user.id,
                    action='login',
                    table_name='users',
                    record_id=user.id,
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent')
                )
                db.session.add(audit_log)
                db.session.commit()
                
                flash(f'Welcome back, {user.full_name}!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password.', 'error')
        
        return render_template('auth/login.html')
    
    @app.route('/logout')
    @login_required
    def logout():
        # Log the logout
        audit_log = AuditLog(
            user_id=current_user.id,
            action='logout',
            table_name='users',
            record_id=current_user.id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(audit_log)
        db.session.commit()
        
        logout_user()
        flash('You have been logged out successfully.', 'info')
        return redirect(url_for('login'))
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint for monitoring"""
        try:
            # Check database connection
            db.session.execute('SELECT 1')
            return jsonify({
                'status': 'healthy',
                'database': 'connected',
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'database': 'disconnected',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }), 500

    # Main dashboard
    @app.route('/')
    @app.route('/dashboard')
    @login_required
    def dashboard():
        # Get dashboard statistics based on user role
        stats = {}
        
        if current_user.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
            # Admin dashboard with full statistics
            stats = {
                'total_patients': Patient.query.filter_by(is_active=True).count(),
                'total_appointments_today': Appointment.query.filter_by(
                    appointment_date=date.today()
                ).count(),
                'pending_appointments': Appointment.query.filter_by(
                    status=AppointmentStatus.PENDING
                ).count(),
                'total_revenue_month': db.session.query(db.func.sum(Payment.amount)).filter(
                    db.extract('month', Payment.payment_date) == date.today().month,
                    db.extract('year', Payment.payment_date) == date.today().year
                ).scalar() or 0,
                'active_packages': PatientPackage.query.filter_by(is_active=True).count()
            }
        elif current_user.role == UserRole.DOCTOR:
            # Doctor dashboard
            stats = {
                'my_appointments_today': Appointment.query.filter_by(
                    doctor_id=current_user.id,
                    appointment_date=date.today()
                ).count(),
                'my_patients': Patient.query.join(Appointment).filter(
                    Appointment.doctor_id == current_user.id
                ).distinct().count(),
                'pending_consultations': OnlineConsultation.query.filter_by(
                    doctor_id=current_user.id,
                    status=ConsultationStatus.SCHEDULED
                ).count()
            }
        elif current_user.role == UserRole.STAFF:
            # Staff dashboard
            stats = {
                'appointments_today': Appointment.query.filter_by(
                    appointment_date=date.today()
                ).count(),
                'pending_appointments': Appointment.query.filter_by(
                    status=AppointmentStatus.PENDING
                ).count(),
                'pending_payments': Billing.query.filter_by(
                    payment_status=PaymentStatus.PENDING
                ).count()
            }
        
        # Get recent activities
        recent_appointments = Appointment.query.filter_by(
            appointment_date=date.today()
        ).order_by(Appointment.appointment_time).limit(5).all()
        
        return render_template('dashboard/main.html', stats=stats, recent_appointments=recent_appointments)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
