# routes/api.py - REST API endpoints

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from models import (
    db, Patient, Appointment, Visit, Billing, Payment, User,
    AppointmentStatus, PaymentStatus, UserRole, VisitType
)

api_bp = Blueprint('api', __name__)

# Error handlers for API
@api_bp.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request', 'message': str(error)}), 400

@api_bp.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'Unauthorized', 'message': 'Authentication required'}), 401

@api_bp.errorhandler(403)
def forbidden(error):
    return jsonify({'error': 'Forbidden', 'message': 'Insufficient permissions'}), 403

@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found', 'message': 'Resource not found'}), 404

@api_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error', 'message': 'An unexpected error occurred'}), 500

# Helper function to serialize models
def serialize_patient(patient):
    """Serialize patient object to dictionary"""
    return {
        'id': patient.id,
        'patient_id': patient.patient_id,
        'first_name': patient.first_name,
        'last_name': patient.last_name,
        'full_name': patient.full_name,
        'email': patient.email,
        'phone': patient.phone,
        'age': patient.age,
        'gender': patient.gender,
        'address': patient.address,
        'city': patient.city,
        'state': patient.state,
        'created_at': patient.created_at.isoformat() if patient.created_at else None
    }

def serialize_appointment(appointment):
    """Serialize appointment object to dictionary"""
    return {
        'id': appointment.id,
        'patient': {
            'id': appointment.patient.id,
            'name': appointment.patient.full_name,
            'phone': appointment.patient.phone
        },
        'doctor': {
            'id': appointment.doctor.id,
            'name': appointment.doctor.full_name
        },
        'appointment_date': appointment.appointment_date.isoformat(),
        'appointment_time': appointment.appointment_time.strftime('%H:%M'),
        'duration_minutes': appointment.duration_minutes,
        'visit_type': appointment.visit_type.value,
        'status': appointment.status.value,
        'reason': appointment.reason,
        'notes': appointment.notes,
        'is_emergency': appointment.is_emergency,
        'created_at': appointment.created_at.isoformat()
    }

# API Routes

@api_bp.route('/patients', methods=['GET'])
@login_required
def api_get_patients():
    """Get list of patients"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    search = request.args.get('search', '')
    
    query = Patient.query.filter_by(is_active=True)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            db.or_(
                Patient.first_name.ilike(search_term),
                Patient.last_name.ilike(search_term),
                Patient.phone.ilike(search_term),
                Patient.patient_id.ilike(search_term)
            )
        )
    
    patients = query.order_by(Patient.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'patients': [serialize_patient(p) for p in patients.items],
        'pagination': {
            'page': patients.page,
            'pages': patients.pages,
            'per_page': patients.per_page,
            'total': patients.total,
            'has_next': patients.has_next,
            'has_prev': patients.has_prev
        }
    })

@api_bp.route('/patients/<int:id>', methods=['GET'])
@login_required
def api_get_patient(id):
    """Get patient details"""
    patient = Patient.query.get_or_404(id)
    
    if not patient.is_active:
        return jsonify({'error': 'Patient not found'}), 404
    
    # Get patient's recent visits and appointments
    recent_visits = Visit.query.filter_by(patient_id=id).order_by(
        Visit.date_of_visit.desc()
    ).limit(5).all()
    
    upcoming_appointments = Appointment.query.filter_by(patient_id=id).filter(
        Appointment.appointment_date >= date.today()
    ).order_by(Appointment.appointment_date, Appointment.appointment_time).limit(5).all()
    
    patient_data = serialize_patient(patient)
    patient_data.update({
        'recent_visits': [
            {
                'id': v.id,
                'date': v.date_of_visit.isoformat(),
                'visit_type': v.visit_type.value,
                'diagnosis': v.diagnosis
            } for v in recent_visits
        ],
        'upcoming_appointments': [serialize_appointment(a) for a in upcoming_appointments]
    })
    
    return jsonify(patient_data)

@api_bp.route('/appointments', methods=['GET'])
@login_required
def api_get_appointments():
    """Get list of appointments"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    date_filter = request.args.get('date')
    status_filter = request.args.get('status')
    doctor_id = request.args.get('doctor_id', type=int)
    
    # Base query based on user role
    if current_user.role == UserRole.DOCTOR:
        query = Appointment.query.filter_by(doctor_id=current_user.id)
    else:
        query = Appointment.query
    
    # Apply filters
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            query = query.filter_by(appointment_date=filter_date)
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
    
    if status_filter:
        try:
            query = query.filter_by(status=AppointmentStatus(status_filter))
        except ValueError:
            return jsonify({'error': 'Invalid status'}), 400
    
    if doctor_id and current_user.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.STAFF]:
        query = query.filter_by(doctor_id=doctor_id)
    
    appointments = query.order_by(
        Appointment.appointment_date.desc(),
        Appointment.appointment_time.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'appointments': [serialize_appointment(a) for a in appointments.items],
        'pagination': {
            'page': appointments.page,
            'pages': appointments.pages,
            'per_page': appointments.per_page,
            'total': appointments.total,
            'has_next': appointments.has_next,
            'has_prev': appointments.has_prev
        }
    })

@api_bp.route('/appointments', methods=['POST'])
@login_required
def api_create_appointment():
    """Create new appointment"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    required_fields = ['patient_id', 'doctor_id', 'appointment_date', 'appointment_time', 'visit_type']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    try:
        # Validate patient and doctor
        patient = Patient.query.get(data['patient_id'])
        doctor = User.query.get(data['doctor_id'])
        
        if not patient or not patient.is_active:
            return jsonify({'error': 'Invalid patient'}), 400
        
        if not doctor or doctor.role != UserRole.DOCTOR or not doctor.is_active:
            return jsonify({'error': 'Invalid doctor'}), 400
        
        # Parse date and time
        appt_date = datetime.strptime(data['appointment_date'], '%Y-%m-%d').date()
        appt_time = datetime.strptime(data['appointment_time'], '%H:%M').time()
        
        # Check for conflicts
        existing = Appointment.query.filter_by(
            doctor_id=data['doctor_id'],
            appointment_date=appt_date,
            appointment_time=appt_time
        ).filter(
            Appointment.status.in_([AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED])
        ).first()
        
        if existing:
            return jsonify({'error': 'Time slot already booked'}), 400
        
        # Create appointment
        appointment = Appointment(
            patient_id=data['patient_id'],
            doctor_id=data['doctor_id'],
            appointment_date=appt_date,
            appointment_time=appt_time,
            duration_minutes=data.get('duration_minutes', 30),
            visit_type=VisitType(data['visit_type']),
            reason=data.get('reason', ''),
            notes=data.get('notes', ''),
            is_emergency=data.get('is_emergency', False),
            created_by_id=current_user.id
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        return jsonify({
            'message': 'Appointment created successfully',
            'appointment': serialize_appointment(appointment)
        }), 201
        
    except ValueError as e:
        return jsonify({'error': f'Invalid data format: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create appointment: {str(e)}'}), 500

@api_bp.route('/appointments/<int:id>/status', methods=['PUT'])
@login_required
def api_update_appointment_status(id):
    """Update appointment status"""
    appointment = Appointment.query.get_or_404(id)
    
    # Check permissions
    if (current_user.role == UserRole.DOCTOR and appointment.doctor_id != current_user.id):
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    if not data or 'status' not in data:
        return jsonify({'error': 'Status is required'}), 400
    
    try:
        new_status = AppointmentStatus(data['status'])
        appointment.status = new_status
        
        if new_status == AppointmentStatus.CONFIRMED:
            appointment.confirmed_at = datetime.utcnow()
        elif new_status == AppointmentStatus.CANCELLED:
            appointment.cancelled_at = datetime.utcnow()
            appointment.cancellation_reason = data.get('reason', '')
        
        appointment.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Appointment status updated successfully',
            'appointment': serialize_appointment(appointment)
        })
        
    except ValueError:
        return jsonify({'error': 'Invalid status'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update appointment: {str(e)}'}), 500

@api_bp.route('/dashboard/stats', methods=['GET'])
@login_required
def api_dashboard_stats():
    """Get dashboard statistics"""
    try:
        stats = {}
        today = date.today()
        
        if current_user.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
            stats = {
                'total_patients': Patient.query.filter_by(is_active=True).count(),
                'appointments_today': Appointment.query.filter_by(appointment_date=today).count(),
                'pending_appointments': Appointment.query.filter_by(status=AppointmentStatus.PENDING).count(),
                'revenue_today': db.session.query(db.func.sum(Payment.amount)).filter(
                    db.func.date(Payment.payment_date) == today
                ).scalar() or 0
            }
        elif current_user.role == UserRole.DOCTOR:
            stats = {
                'my_appointments_today': Appointment.query.filter_by(
                    doctor_id=current_user.id,
                    appointment_date=today
                ).count(),
                'my_patients': Patient.query.join(Appointment).filter(
                    Appointment.doctor_id == current_user.id
                ).distinct().count()
            }
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': f'Failed to get stats: {str(e)}'}), 500

@api_bp.route('/search', methods=['GET'])
@login_required
def api_search():
    """Global search API"""
    query = request.args.get('q', '').strip()
    
    if not query or len(query) < 2:
        return jsonify({'results': []})
    
    search_term = f"%{query}%"
    results = []
    
    try:
        # Search patients
        patients = Patient.query.filter(
            db.or_(
                Patient.first_name.ilike(search_term),
                Patient.last_name.ilike(search_term),
                Patient.phone.ilike(search_term),
                Patient.patient_id.ilike(search_term)
            ),
            Patient.is_active == True
        ).limit(5).all()
        
        for patient in patients:
            results.append({
                'type': 'patient',
                'id': patient.id,
                'title': patient.full_name,
                'subtitle': f'Phone: {patient.phone}',
                'url': f'/patients/{patient.id}'
            })
        
        # Search appointments (based on user role)
        if current_user.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.STAFF]:
            appointments = Appointment.query.join(Patient).filter(
                db.or_(
                    Patient.first_name.ilike(search_term),
                    Patient.last_name.ilike(search_term)
                )
            ).order_by(Appointment.appointment_date.desc()).limit(5).all()
        elif current_user.role == UserRole.DOCTOR:
            appointments = Appointment.query.join(Patient).filter(
                Appointment.doctor_id == current_user.id,
                db.or_(
                    Patient.first_name.ilike(search_term),
                    Patient.last_name.ilike(search_term)
                )
            ).order_by(Appointment.appointment_date.desc()).limit(5).all()
        else:
            appointments = []
        
        for appointment in appointments:
            results.append({
                'type': 'appointment',
                'id': appointment.id,
                'title': f'Appointment with {appointment.patient.full_name}',
                'subtitle': f'{appointment.appointment_date} at {appointment.appointment_time}',
                'url': f'/appointments/{appointment.id}'
            })
        
        return jsonify({'results': results})
        
    except Exception as e:
        return jsonify({'error': f'Search failed: {str(e)}'}), 500
