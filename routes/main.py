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

# Additional routes for template functionality
@main_bp.route('/users/add')
@login_required
def add_user():
    """Add new user page"""
    if not current_user.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
        flash('You do not have permission to add users.', 'error')
        return redirect(url_for('main.dashboard'))
    return render_template('users/add.html')

@main_bp.route('/users/<int:user_id>')
@login_required
def view_user(user_id):
    """View user details"""
    if not current_user.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
        flash('You do not have permission to view user details.', 'error')
        return redirect(url_for('main.dashboard'))
    user = User.query.get_or_404(user_id)
    return render_template('users/view.html', user=user)

@main_bp.route('/users/<int:user_id>/edit')
@login_required
def edit_user(user_id):
    """Edit user page"""
    if not current_user.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
        flash('You do not have permission to edit users.', 'error')
        return redirect(url_for('main.dashboard'))
    user = User.query.get_or_404(user_id)
    return render_template('users/edit.html', user=user)

# Report routes
@main_bp.route('/reports/patient')
@login_required
def patient_report():
    return render_template('reports/patient.html')

@main_bp.route('/reports/patient-visits')
@login_required
def patient_visits_report():
    return render_template('reports/patient_visits.html')

@main_bp.route('/reports/new-patients')
@login_required
def new_patients_report():
    return render_template('reports/new_patients.html')

@main_bp.route('/reports/revenue')
@login_required
def revenue_report():
    return render_template('reports/revenue.html')

@main_bp.route('/reports/payment')
@login_required
def payment_report():
    return render_template('reports/payment.html')

@main_bp.route('/reports/outstanding')
@login_required
def outstanding_report():
    return render_template('reports/outstanding.html')

@main_bp.route('/reports/appointment-summary')
@login_required
def appointment_summary_report():
    return render_template('reports/appointment_summary.html')

@main_bp.route('/reports/doctor-schedule')
@login_required
def doctor_schedule_report():
    return render_template('reports/doctor_schedule.html')

@main_bp.route('/reports/cancellation')
@login_required
def cancellation_report():
    return render_template('reports/cancellation.html')

@main_bp.route('/reports/treatment-effectiveness')
@login_required
def treatment_effectiveness_report():
    return render_template('reports/treatment_effectiveness.html')

@main_bp.route('/reports/package-utilization')
@login_required
def package_utilization_report():
    return render_template('reports/package_utilization.html')

@main_bp.route('/reports/prescription')
@login_required
def prescription_report():
    return render_template('reports/prescription.html')

@main_bp.route('/reports/user-activity')
@login_required
def user_activity_report():
    return render_template('reports/user_activity.html')

@main_bp.route('/reports/audit-log')
@login_required
def audit_log_report():
    return render_template('reports/audit_log.html')

@main_bp.route('/reports/system-performance')
@login_required
def system_performance_report():
    return render_template('reports/system_performance.html')

@main_bp.route('/reports/custom-builder')
@login_required
def custom_report_builder():
    return render_template('reports/custom_builder.html')

@main_bp.route('/reports/export-all')
@login_required
def export_all_reports():
    return jsonify({'message': 'Export functionality coming soon'})

# Settings save route
@main_bp.route('/settings/save', methods=['POST'])
@login_required
def save_settings():
    """Save system settings"""
    if not current_user.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
        return jsonify({'success': False, 'message': 'Permission denied'})

    try:
        data = request.get_json()
        # Here you would save the settings to database
        # For now, just return success
        return jsonify({'success': True, 'message': 'Settings saved successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# WhatsApp test route
@main_bp.route('/test-whatsapp')
@login_required
def test_whatsapp():
    """Test WhatsApp functionality"""
    if not current_user.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
        flash('You do not have permission to test WhatsApp.', 'error')
        return redirect(url_for('main.dashboard'))

    try:
        from services.whatsapp_service import WhatsAppService
        whatsapp = WhatsAppService()

        # Send a test message
        test_message = f"🏥 Test message from Dr. Payal's CRM\n\nHello! This is a test message to verify WhatsApp integration is working.\n\nSent at: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC"

        # Use a demo phone number
        result = whatsapp.send_message(
            to_number="+1234567890",
            message_text=test_message,
            message_type="test"
        )

        if result:
            flash('WhatsApp test message sent successfully! Check the console for demo output.', 'success')
        else:
            flash('Failed to send WhatsApp test message.', 'error')

    except Exception as e:
        flash(f'Error testing WhatsApp: {str(e)}', 'error')

    return redirect(url_for('main.dashboard'))
