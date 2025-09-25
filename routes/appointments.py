# routes/appointments.py - Appointment management routes

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from models import (
    db, Appointment, Patient, User, OnlineConsultation,
    AppointmentStatus, VisitType, UserRole, ConsultationStatus
)

appointments_bp = Blueprint('appointments', __name__)

@appointments_bp.route('/')
@login_required
def list_appointments():
    """List appointments with filtering"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    date_filter = request.args.get('date', '')
    doctor_filter = request.args.get('doctor', '', type=int)
    per_page = 20
    
    # Base query based on user role
    if current_user.role == UserRole.DOCTOR:
        query = Appointment.query.filter_by(doctor_id=current_user.id)
    elif current_user.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.STAFF]:
        query = Appointment.query
    else:
        flash('You do not have permission to view appointments.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Apply filters
    if status_filter:
        query = query.filter_by(status=AppointmentStatus(status_filter))
    
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            query = query.filter_by(appointment_date=filter_date)
        except ValueError:
            flash('Invalid date format.', 'error')
    
    if doctor_filter and current_user.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.STAFF]:
        query = query.filter_by(doctor_id=doctor_filter)
    
    appointments = query.order_by(
        Appointment.appointment_date.desc(),
        Appointment.appointment_time.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    # Get doctors for filter dropdown
    doctors = User.query.filter_by(role=UserRole.DOCTOR, is_active=True).all()

    # Calculate stats for the template
    today = date.today()
    stats = {
        'today_total': Appointment.query.filter_by(appointment_date=today).count(),
        'pending_total': Appointment.query.filter_by(status=AppointmentStatus.SCHEDULED).count(),
        'completed_total': Appointment.query.filter_by(status=AppointmentStatus.COMPLETED).count(),
        'cancelled_total': Appointment.query.filter_by(status=AppointmentStatus.CANCELLED).count()
    }

    return render_template('appointments/list.html',
                         appointments=appointments,
                         doctors=doctors,
                         stats=stats,
                         status_filter=status_filter,
                         date_filter=date_filter,
                         doctor_filter=doctor_filter)

@appointments_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_appointment():
    """Add new appointment"""
    if request.method == 'POST':
        try:
            # Get form data
            patient_id = request.form.get('patient_id', type=int)
            doctor_id = request.form.get('doctor_id', type=int)
            appointment_date = request.form.get('appointment_date')
            appointment_time = request.form.get('appointment_time')
            duration_minutes = request.form.get('duration_minutes', 30, type=int)
            visit_type = request.form.get('visit_type')
            reason = request.form.get('reason', '').strip()
            notes = request.form.get('notes', '').strip()
            is_emergency = request.form.get('is_emergency') == 'on'
            
            # Validation
            if not all([patient_id, doctor_id, appointment_date, appointment_time, visit_type]):
                flash('All required fields must be filled.', 'error')
                return render_template('appointments/add.html')
            
            # Verify patient and doctor exist
            patient = Patient.query.get(patient_id)
            doctor = User.query.get(doctor_id)
            
            if not patient or not patient.is_active:
                flash('Invalid patient selected.', 'error')
                return render_template('appointments/add.html')
            
            if not doctor or doctor.role != UserRole.DOCTOR or not doctor.is_active:
                flash('Invalid doctor selected.', 'error')
                return render_template('appointments/add.html')
            
            # Parse date and time
            try:
                appt_date = datetime.strptime(appointment_date, '%Y-%m-%d').date()
                appt_time = datetime.strptime(appointment_time, '%H:%M').time()
            except ValueError:
                flash('Invalid date or time format.', 'error')
                return render_template('appointments/add.html')
            
            # Check if appointment date is not in the past
            if appt_date < date.today():
                flash('Appointment date cannot be in the past.', 'error')
                return render_template('appointments/add.html')
            
            # Check for conflicting appointments
            existing_appointment = Appointment.query.filter_by(
                doctor_id=doctor_id,
                appointment_date=appt_date,
                appointment_time=appt_time
            ).filter(
                Appointment.status.in_([AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED])
            ).first()
            
            if existing_appointment:
                flash('Doctor already has an appointment at this time.', 'error')
                return render_template('appointments/add.html')
            
            # Create new appointment
            new_appointment = Appointment(
                patient_id=patient_id,
                doctor_id=doctor_id,
                appointment_date=appt_date,
                appointment_time=appt_time,
                duration_minutes=duration_minutes,
                visit_type=VisitType(visit_type),
                reason=reason,
                notes=notes,
                is_emergency=is_emergency,
                created_by_id=current_user.id,
                status=AppointmentStatus.PENDING
            )
            
            db.session.add(new_appointment)
            db.session.commit()
            
            flash(f'Appointment scheduled for {patient.full_name} with Dr. {doctor.full_name}!', 'success')
            return redirect(url_for('appointments.view_appointment', id=new_appointment.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating appointment: {str(e)}', 'error')
    
    # Get patients and doctors for dropdowns
    patients = Patient.query.filter_by(is_active=True).order_by(Patient.first_name).all()
    doctors = User.query.filter_by(role=UserRole.DOCTOR, is_active=True).order_by(User.first_name).all()
    
    return render_template('appointments/add.html', patients=patients, doctors=doctors)

@appointments_bp.route('/<int:id>')
@login_required
def view_appointment(id):
    """View appointment details"""
    appointment = Appointment.query.get_or_404(id)
    
    # Check permissions
    if (current_user.role == UserRole.DOCTOR and appointment.doctor_id != current_user.id):
        flash('You can only view your own appointments.', 'error')
        return redirect(url_for('appointments.list_appointments'))
    
    return render_template('appointments/view.html', appointment=appointment)

@appointments_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_appointment(id):
    """Edit appointment"""
    appointment = Appointment.query.get_or_404(id)
    
    # Check permissions
    if (current_user.role == UserRole.DOCTOR and appointment.doctor_id != current_user.id):
        flash('You can only edit your own appointments.', 'error')
        return redirect(url_for('appointments.view_appointment', id=id))
    
    if request.method == 'POST':
        try:
            # Update appointment details
            appointment.appointment_date = datetime.strptime(
                request.form.get('appointment_date'), '%Y-%m-%d'
            ).date()
            appointment.appointment_time = datetime.strptime(
                request.form.get('appointment_time'), '%H:%M'
            ).time()
            appointment.duration_minutes = request.form.get('duration_minutes', 30, type=int)
            appointment.visit_type = VisitType(request.form.get('visit_type'))
            appointment.reason = request.form.get('reason', '').strip()
            appointment.notes = request.form.get('notes', '').strip()
            appointment.is_emergency = request.form.get('is_emergency') == 'on'
            appointment.updated_at = datetime.utcnow()
            
            # Update doctor if user has permission
            if current_user.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.STAFF]:
                doctor_id = request.form.get('doctor_id', type=int)
                if doctor_id:
                    appointment.doctor_id = doctor_id
            
            db.session.commit()
            flash('Appointment updated successfully!', 'success')
            return redirect(url_for('appointments.view_appointment', id=appointment.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating appointment: {str(e)}', 'error')
    
    # Get doctors for dropdown
    doctors = User.query.filter_by(role=UserRole.DOCTOR, is_active=True).all()
    
    return render_template('appointments/edit.html', appointment=appointment, doctors=doctors)

@appointments_bp.route('/<int:id>/confirm', methods=['POST'])
@login_required
def confirm_appointment(id):
    """Confirm appointment"""
    appointment = Appointment.query.get_or_404(id)
    
    try:
        appointment.status = AppointmentStatus.CONFIRMED
        appointment.confirmed_at = datetime.utcnow()
        appointment.updated_at = datetime.utcnow()
        db.session.commit()
        
        flash('Appointment confirmed successfully!', 'success')
        
        # TODO: Send confirmation notification
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error confirming appointment: {str(e)}', 'error')
    
    return redirect(url_for('appointments.view_appointment', id=id))

@appointments_bp.route('/<int:id>/cancel', methods=['POST'])
@login_required
def cancel_appointment(id):
    """Cancel appointment"""
    appointment = Appointment.query.get_or_404(id)
    
    # Check permissions
    if (current_user.role == UserRole.DOCTOR and appointment.doctor_id != current_user.id):
        flash('You can only cancel your own appointments.', 'error')
        return redirect(url_for('appointments.view_appointment', id=id))
    
    cancellation_reason = request.form.get('cancellation_reason', '').strip()
    
    try:
        appointment.status = AppointmentStatus.CANCELLED
        appointment.cancelled_at = datetime.utcnow()
        appointment.cancellation_reason = cancellation_reason
        appointment.updated_at = datetime.utcnow()
        db.session.commit()
        
        flash('Appointment cancelled successfully!', 'success')
        
        # TODO: Send cancellation notification
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error cancelling appointment: {str(e)}', 'error')
    
    return redirect(url_for('appointments.view_appointment', id=id))

@appointments_bp.route('/<int:id>/complete', methods=['POST'])
@login_required
def complete_appointment(id):
    """Mark appointment as completed"""
    appointment = Appointment.query.get_or_404(id)
    
    # Check permissions
    if (current_user.role == UserRole.DOCTOR and appointment.doctor_id != current_user.id):
        flash('You can only complete your own appointments.', 'error')
        return redirect(url_for('appointments.view_appointment', id=id))
    
    try:
        appointment.status = AppointmentStatus.COMPLETED
        appointment.updated_at = datetime.utcnow()
        db.session.commit()
        
        flash('Appointment marked as completed!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error completing appointment: {str(e)}', 'error')
    
    return redirect(url_for('appointments.view_appointment', id=id))

@appointments_bp.route('/calendar')
@login_required
def calendar():
    """Calendar view of appointments"""
    # Get date range from query parameters
    start_date = request.args.get('start', date.today().isoformat())
    end_date = request.args.get('end', (date.today() + timedelta(days=30)).isoformat())
    
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        start = date.today()
        end = date.today() + timedelta(days=30)
    
    # Get appointments based on user role
    if current_user.role == UserRole.DOCTOR:
        appointments = Appointment.query.filter(
            Appointment.doctor_id == current_user.id,
            Appointment.appointment_date.between(start, end)
        ).all()
    else:
        appointments = Appointment.query.filter(
            Appointment.appointment_date.between(start, end)
        ).all()
    
    # Format appointments for calendar
    calendar_events = []
    for appointment in appointments:
        calendar_events.append({
            'id': appointment.id,
            'title': f'{appointment.patient.full_name} - {appointment.visit_type.value}',
            'start': f'{appointment.appointment_date}T{appointment.appointment_time}',
            'end': f'{appointment.appointment_date}T{appointment.appointment_time}',
            'status': appointment.status.value,
            'doctor': appointment.doctor.full_name,
            'patient': appointment.patient.full_name
        })
    
    return render_template('appointments/calendar.html', events=calendar_events)

@appointments_bp.route('/api/available-slots')
@login_required
def api_available_slots():
    """API endpoint to get available appointment slots"""
    doctor_id = request.args.get('doctor_id', type=int)
    date_str = request.args.get('date')
    
    if not doctor_id or not date_str:
        return jsonify({'error': 'Doctor ID and date are required'}), 400
    
    try:
        appointment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
    
    # Get existing appointments for the doctor on this date
    existing_appointments = Appointment.query.filter_by(
        doctor_id=doctor_id,
        appointment_date=appointment_date
    ).filter(
        Appointment.status.in_([AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED])
    ).all()
    
    # Generate available slots (9 AM to 6 PM, 30-minute intervals)
    available_slots = []
    start_time = datetime.combine(appointment_date, datetime.min.time().replace(hour=9))
    end_time = datetime.combine(appointment_date, datetime.min.time().replace(hour=18))
    
    current_time = start_time
    while current_time < end_time:
        slot_time = current_time.time()
        
        # Check if this slot is already booked
        is_booked = any(
            appt.appointment_time == slot_time 
            for appt in existing_appointments
        )
        
        if not is_booked:
            available_slots.append(slot_time.strftime('%H:%M'))
        
        current_time += timedelta(minutes=30)
    
    return jsonify({'available_slots': available_slots})
