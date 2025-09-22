# app.py - Main Application Entry Point for Hospital CRM

import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_, func, extract
from datetime import date, datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL',
        'postgresql://hospital_user:hospital_password_2024@localhost:5432/hospital_crm'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize database
    from models import db
    db.init_app(app)

    # Initialize Flask-Migrate
    migrate = Migrate(app, db)

    # Flask-Login setup
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))

    # Configure logging
    configure_logging(app)

    # Create database tables and default data
    with app.app_context():
        create_default_data()

    # Register error handlers
    register_error_handlers(app)

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
                'timestamp': datetime.utcnow().isoformat(),
                'version': '1.0.0'
            }), 200
        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'database': 'disconnected',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }), 500

    return app

def configure_logging(app):
    """Configure application logging"""
    if not app.debug and not app.testing:
        # Production logging
        if not os.path.exists('logs'):
            os.mkdir('logs')

        file_handler = logging.FileHandler('logs/hospital_crm.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Hospital CRM startup')

def create_default_data():
    """Create default users and system settings"""
    from models import db, User, UserRole, SystemSetting, TreatmentPackage

    try:
        # Create tables
        db.create_all()

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

        db.session.commit()
        print("✅ Default data created successfully!")

    except Exception as e:
        print(f"❌ Error creating default data: {e}")
        db.session.rollback()

def register_error_handlers(app):
    """Register error handlers"""
    @app.errorhandler(404)
    def not_found_error(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Not found'}), 404
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        from models import db
        db.session.rollback()
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Internal server error'}), 500
        return render_template('errors/500.html'), 500

    # Legacy routes for backward compatibility
    @app.route('/')
    def home():
        from models import Patient
        query = request.args.get('query')

        if query:
            search = "%{}%".format(query)
            patients = Patient.query.filter(
                or_(
                    Patient.first_name.ilike(search),
                    Patient.last_name.ilike(search),
                    Patient.phone.ilike(search)
                )
            ).all()
        else:
            patients = Patient.query.filter_by(is_active=True).all()

        return render_template('index.html', patients=patients)

    # Login route
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        from models import User
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username).first()

            if user and user.check_password(password) and user.is_active:
                login_user(user)
                user.last_login = datetime.utcnow()
                db.session.commit()
                flash(f'Welcome back, {user.full_name}!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password.', 'danger')
        return render_template('login.html')

    # Logout route
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('home'))

    @app.route('/add_patient', methods=['POST'])
    @login_required
    def add_patient():
        from models import Patient
        if request.method == 'POST':
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            phone = request.form['phone']
            email = request.form.get('email')
            address = request.form.get('address')

            # Generate patient ID
            patient_count = Patient.query.count()
            patient_id = f"P{patient_count + 1:06d}"

            new_patient = Patient(
                patient_id=patient_id,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                email=email,
                address=address
            )
            db.session.add(new_patient)
            db.session.commit()
            flash('Patient added successfully!')
            return redirect(url_for('home'))

@app.route('/add_visit/<int:patient_id>', methods=['POST'])
def add_visit(patient_id):
    if request.method == 'POST':
        visit_type = request.form['visit_type']
        date_of_visit = date.fromisoformat(request.form['date_of_visit'])
        days_left = request.form['days_left']
        remarks = request.form['remarks']
        package = request.form['package']
        bill_amount = request.form['bill_amount']
        payment_status = request.form['payment_status']
        mode_of_payment = request.form['mode_of_payment']
        new_visit = Visit(
            patient_id=patient_id, visit_type=visit_type, date_of_visit=date_of_visit,
            days_left=days_left, remarks=remarks
        )
        new_billing = Billing(
            package=package, bill_amount=float(bill_amount), payment_status=payment_status,
            mode_of_payment=mode_of_payment
        )
        new_visit.billing = new_billing
        db.session.add(new_visit)
        db.session.commit()
        flash('Visit added successfully!')
        return redirect(url_for('home'))

@app.route('/edit_patient/<int:id>')
def edit_patient(id):
    patient = db.session.get(Patient, id)
    if patient is None:
        return redirect(url_for('home'))
    return render_template('edit.html', patient=patient)

@app.route('/update_patient/<int:id>', methods=['POST'])
def update_patient(id):
    patient = db.session.get(Patient, id)
    if patient is None:
        return redirect(url_for('home'))
    patient.name = request.form['name']
    patient.age = request.form['age']
    patient.phone_number = request.form['phone_number']
    patient.address = request.form['address']
    db.session.commit()
    flash('Patient updated successfully!')
    return redirect(url_for('home'))

@app.route('/delete_patient/<int:id>', methods=['POST'])
def delete_patient(id):
    patient = db.session.get(Patient, id)
    if patient:
        db.session.delete(patient)
        db.session.commit()
        flash('Patient deleted successfully!')
    return redirect(url_for('home'))

@app.route('/edit_visit/<int:id>')
def edit_visit(id):
    visit = db.session.get(Visit, id)
    if visit is None:
        return redirect(url_for('home'))
    return render_template('edit_visit.html', visit=visit)

@app.route('/update_visit/<int:id>', methods=['POST'])
def update_visit(id):
    visit = db.session.get(Visit, id)
    if visit is None:
        return redirect(url_for('home'))

    visit.visit_type = request.form['visit_type']
    visit.date_of_visit = date.fromisoformat(request.form['date_of_visit'])
    visit.days_left = request.form['days_left']
    visit.remarks = request.form['remarks']
    
    if visit.billing:
        visit.billing.package = request.form['package']
        visit.billing.bill_amount = float(request.form['bill_amount'])
        visit.billing.payment_status = request.form['payment_status']
        visit.billing.mode_of_payment = request.form['mode_of_payment']
    else:
        new_billing = Billing(
            package=request.form['package'],
            bill_amount=float(request.form['bill_amount']),
            payment_status=request.form['payment_status'],
            mode_of_payment=request.form['mode_of_payment']
        )
        visit.billing = new_billing

    db.session.commit()
    flash('Visit updated successfully!')
    return redirect(url_for('home'))

@app.route('/delete_visit/<int:id>', methods=['POST'])
def delete_visit(id):
    visit = db.session.get(Visit, id)
    if visit:
        db.session.delete(visit)
        db.session.commit()
        flash('Visit deleted successfully!')
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Patient Counts by Day, Week, and Month
    daily_visits_rows = db.session.query(
        Visit.date_of_visit,
        func.count(Visit.id)
    ).group_by(Visit.date_of_visit).order_by(Visit.date_of_visit).all()
    
    weekly_visits_rows = db.session.query(
        extract('year', Visit.date_of_visit),
        extract('week', Visit.date_of_visit),
        func.count(Visit.id)
    ).group_by(
        extract('year', Visit.date_of_visit),
        extract('week', Visit.date_of_visit)
    ).order_by(
        extract('year', Visit.date_of_visit),
        extract('week', Visit.date_of_visit)
    ).all()
    
    monthly_visits_rows = db.session.query(
        extract('year', Visit.date_of_visit),
        extract('month', Visit.date_of_visit),
        func.count(Visit.id)
    ).group_by(
        extract('year', Visit.date_of_visit),
        extract('month', Visit.date_of_visit)
    ).order_by(
        extract('year', Visit.date_of_visit),
        extract('month', Visit.date_of_visit)
    ).all()
    
    # Financial Data (Total Earnings) by Day, Week, and Month
    daily_earnings_rows = db.session.query(
        Visit.date_of_visit,
        func.sum(Billing.bill_amount)
    ).join(Billing).group_by(Visit.date_of_visit).order_by(Visit.date_of_visit).all()

    weekly_earnings_rows = db.session.query(
        extract('year', Visit.date_of_visit),
        extract('week', Visit.date_of_visit),
        func.sum(Billing.bill_amount)
    ).join(Billing).group_by(
        extract('year', Visit.date_of_visit),
        extract('week', Visit.date_of_visit)
    ).order_by(
        extract('year', Visit.date_of_visit),
        extract('week', Visit.date_of_visit)
    ).all()

    monthly_earnings_rows = db.session.query(
        extract('year', Visit.date_of_visit),
        extract('month', Visit.date_of_visit),
        func.sum(Billing.bill_amount)
    ).join(Billing).group_by(
        extract('year', Visit.date_of_visit),
        extract('month', Visit.date_of_visit)
    ).order_by(
        extract('year', Visit.date_of_visit),
        extract('month', Visit.date_of_visit)
    ).all()

    # NEW: Convert SQLAlchemy Row objects to serializable lists
    daily_visits = [list(row) for row in daily_visits_rows]
    weekly_visits = [list(row) for row in weekly_visits_rows]
    monthly_visits = [list(row) for row in monthly_visits_rows]
    daily_earnings = [list(row) for row in daily_earnings_rows]
    weekly_earnings = [list(row) for row in weekly_earnings_rows]
    monthly_earnings = [list(row) for row in monthly_earnings_rows]

    return render_template(
        'dashboard.html',
        daily_visits=daily_visits,
        weekly_visits=weekly_visits,
        monthly_visits=monthly_visits,
        daily_earnings=daily_earnings,
        weekly_earnings=weekly_earnings,
        monthly_earnings=monthly_earnings
    )

@app.route('/send_bill/<int:visit_id>')
def send_bill(visit_id):
    visit = db.session.get(Visit, visit_id)
    if visit and visit.patient and visit.billing:
        account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
        client = Client(account_sid, auth_token)

        to_number = f"whatsapp:{visit.patient.phone_number}"
        from_number = "whatsapp:+14155238886"

        bill_message = (
            f"Hello {visit.patient.name},\n"
            f"Here is your billing summary for your visit on {visit.date_of_visit}:\n"
            f"- Service: {visit.visit_type}\n"
            f"- Package: {visit.billing.package}\n"
            f"- Bill Amount: ₹{visit.billing.bill_amount}\n"
            f"- Payment Status: {visit.billing.payment_status}\n"
            f"Thank you for your visit!"
        )

        try:
            message = client.messages.create(
                to=to_number,
                from_=from_number,
                body=bill_message
            )
            flash(f'Message sent successfully! SID: {message.sid}')
        except Exception as e:
            flash(f'Error sending message: {e}', 'danger')

    return redirect(url_for('home'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        from models import Patient, Appointment, AppointmentStatus, UserRole

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
            }

        # Get recent appointments
        recent_appointments = Appointment.query.filter_by(
            appointment_date=date.today()
        ).order_by(Appointment.appointment_time).limit(5).all()

        return render_template('dashboard.html', stats=stats, recent_appointments=recent_appointments)

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)