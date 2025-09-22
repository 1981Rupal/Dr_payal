# routes/main.py - Main application routes

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy import or_, func, extract
from datetime import date, datetime, timedelta
from models import (
    db, Patient, Appointment, Visit, Billing, Payment, User, 
    AppointmentStatus, PaymentStatus, UserRole, VisitType
)

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page - redirect to dashboard if logged in"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard with statistics and recent activities"""
    stats = {}
    recent_activities = []
    
    try:
        if current_user.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
            # Admin dashboard with full statistics
            today = date.today()
            this_month = today.replace(day=1)
            
            stats = {
                'total_patients': Patient.query.filter_by(is_active=True).count(),
                'appointments_today': Appointment.query.filter_by(
                    appointment_date=today
                ).count(),
                'pending_appointments': Appointment.query.filter_by(
                    status=AppointmentStatus.PENDING
                ).count(),
                'revenue_this_month': db.session.query(func.sum(Payment.amount)).filter(
                    Payment.payment_date >= this_month
                ).scalar() or 0,
                'pending_payments': Billing.query.filter_by(
                    payment_status=PaymentStatus.PENDING
                ).count()
            }
            
            # Recent appointments
            recent_activities = Appointment.query.filter(
                Appointment.appointment_date >= today - timedelta(days=7)
            ).order_by(Appointment.created_at.desc()).limit(10).all()
            
        elif current_user.role == UserRole.DOCTOR:
            # Doctor dashboard
            today = date.today()
            stats = {
                'my_appointments_today': Appointment.query.filter_by(
                    doctor_id=current_user.id,
                    appointment_date=today
                ).count(),
                'my_patients': Patient.query.join(Appointment).filter(
                    Appointment.doctor_id == current_user.id
                ).distinct().count(),
                'completed_today': Appointment.query.filter_by(
                    doctor_id=current_user.id,
                    appointment_date=today,
                    status=AppointmentStatus.COMPLETED
                ).count()
            }
            
            # Doctor's recent appointments
            recent_activities = Appointment.query.filter_by(
                doctor_id=current_user.id
            ).filter(
                Appointment.appointment_date >= today - timedelta(days=7)
            ).order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc()).limit(10).all()
            
        elif current_user.role == UserRole.STAFF:
            # Staff dashboard
            today = date.today()
            stats = {
                'appointments_today': Appointment.query.filter_by(
                    appointment_date=today
                ).count(),
                'pending_appointments': Appointment.query.filter_by(
                    status=AppointmentStatus.PENDING
                ).count(),
                'pending_payments': Billing.query.filter_by(
                    payment_status=PaymentStatus.PENDING
                ).count(),
                'new_patients_week': Patient.query.filter(
                    Patient.created_at >= today - timedelta(days=7)
                ).count()
            }
            
            # Recent appointments
            recent_activities = Appointment.query.filter_by(
                appointment_date=today
            ).order_by(Appointment.appointment_time).limit(10).all()
    
    except Exception as e:
        flash(f'Error loading dashboard data: {str(e)}', 'error')
        stats = {}
        recent_activities = []
    
    return render_template('dashboard/main.html', 
                         stats=stats, 
                         recent_activities=recent_activities,
                         user_role=current_user.role)

@main_bp.route('/search')
@login_required
def search():
    """Global search functionality"""
    query = request.args.get('q', '').strip()
    results = {
        'patients': [],
        'appointments': [],
        'visits': []
    }
    
    if query and len(query) >= 2:
        search_term = f"%{query}%"
        
        try:
            # Search patients
            results['patients'] = Patient.query.filter(
                or_(
                    Patient.first_name.ilike(search_term),
                    Patient.last_name.ilike(search_term),
                    Patient.phone.ilike(search_term),
                    Patient.email.ilike(search_term),
                    Patient.patient_id.ilike(search_term)
                ),
                Patient.is_active == True
            ).limit(10).all()
            
            # Search appointments (if user has permission)
            if current_user.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.STAFF]:
                results['appointments'] = Appointment.query.join(Patient).filter(
                    or_(
                        Patient.first_name.ilike(search_term),
                        Patient.last_name.ilike(search_term),
                        Patient.phone.ilike(search_term)
                    )
                ).order_by(Appointment.appointment_date.desc()).limit(10).all()
            elif current_user.role == UserRole.DOCTOR:
                results['appointments'] = Appointment.query.join(Patient).filter(
                    Appointment.doctor_id == current_user.id,
                    or_(
                        Patient.first_name.ilike(search_term),
                        Patient.last_name.ilike(search_term),
                        Patient.phone.ilike(search_term)
                    )
                ).order_by(Appointment.appointment_date.desc()).limit(10).all()
            
        except Exception as e:
            flash(f'Search error: {str(e)}', 'error')
    
    if request.headers.get('Content-Type') == 'application/json':
        return jsonify(results)
    
    return render_template('search_results.html', results=results, query=query)

@main_bp.route('/users')
@login_required
def users():
    """User management page (admin only)"""
    if not current_user.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
        flash('You do not have permission to access user management.', 'error')
        return redirect(url_for('main.dashboard'))
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    users = User.query.filter_by(is_active=True).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('users/list.html', users=users)

@main_bp.route('/settings')
@login_required
def settings():
    """System settings page (admin only)"""
    if not current_user.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
        flash('You do not have permission to access system settings.', 'error')
        return redirect(url_for('main.dashboard'))
    
    from models import SystemSetting
    settings = SystemSetting.query.all()
    
    return render_template('settings/index.html', settings=settings)

@main_bp.route('/reports')
@login_required
def reports():
    """Reports and analytics page"""
    if not current_user.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.DOCTOR]:
        flash('You do not have permission to access reports.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Get date range from query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date:
        start_date = (date.today() - timedelta(days=30)).isoformat()
    if not end_date:
        end_date = date.today().isoformat()
    
    try:
        # Generate reports based on user role
        reports_data = generate_reports(current_user, start_date, end_date)
    except Exception as e:
        flash(f'Error generating reports: {str(e)}', 'error')
        reports_data = {}
    
    return render_template('reports/index.html', 
                         reports=reports_data,
                         start_date=start_date,
                         end_date=end_date)

def generate_reports(user, start_date, end_date):
    """Generate reports based on user role and date range"""
    reports = {}
    
    try:
        start = datetime.fromisoformat(start_date).date()
        end = datetime.fromisoformat(end_date).date()
        
        if user.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
            # Admin reports
            reports['appointments'] = {
                'total': Appointment.query.filter(
                    Appointment.appointment_date.between(start, end)
                ).count(),
                'completed': Appointment.query.filter(
                    Appointment.appointment_date.between(start, end),
                    Appointment.status == AppointmentStatus.COMPLETED
                ).count(),
                'cancelled': Appointment.query.filter(
                    Appointment.appointment_date.between(start, end),
                    Appointment.status == AppointmentStatus.CANCELLED
                ).count()
            }
            
            reports['revenue'] = {
                'total': db.session.query(func.sum(Payment.amount)).filter(
                    Payment.payment_date.between(start, end)
                ).scalar() or 0,
                'pending': db.session.query(func.sum(Billing.total_amount)).join(Visit).filter(
                    Visit.date_of_visit.between(start, end),
                    Billing.payment_status == PaymentStatus.PENDING
                ).scalar() or 0
            }
            
        elif user.role == UserRole.DOCTOR:
            # Doctor reports
            reports['my_appointments'] = {
                'total': Appointment.query.filter(
                    Appointment.doctor_id == user.id,
                    Appointment.appointment_date.between(start, end)
                ).count(),
                'completed': Appointment.query.filter(
                    Appointment.doctor_id == user.id,
                    Appointment.appointment_date.between(start, end),
                    Appointment.status == AppointmentStatus.COMPLETED
                ).count()
            }
    
    except Exception as e:
        print(f"Error generating reports: {e}")
    
    return reports
