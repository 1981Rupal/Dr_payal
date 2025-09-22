# routes/patients.py - Patient management routes

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy import or_
from datetime import datetime, date
from models import (
    db, Patient, Visit, Appointment, Billing, Payment, User,
    UserRole, VisitType, AppointmentStatus
)

patients_bp = Blueprint('patients', __name__)

@patients_bp.route('/')
@login_required
def list_patients():
    """List all patients with search and pagination"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    per_page = 20
    
    query = Patient.query.filter_by(is_active=True)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Patient.first_name.ilike(search_term),
                Patient.last_name.ilike(search_term),
                Patient.phone.ilike(search_term),
                Patient.email.ilike(search_term),
                Patient.patient_id.ilike(search_term)
            )
        )
    
    patients = query.order_by(Patient.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('patients/list.html', patients=patients, search=search)

@patients_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_patient():
    """Add new patient"""
    if request.method == 'POST':
        try:
            # Get form data
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()
            whatsapp_number = request.form.get('whatsapp_number', '').strip()
            date_of_birth = request.form.get('date_of_birth')
            gender = request.form.get('gender')
            address = request.form.get('address', '').strip()
            city = request.form.get('city', '').strip()
            state = request.form.get('state', '').strip()
            pincode = request.form.get('pincode', '').strip()
            emergency_contact_name = request.form.get('emergency_contact_name', '').strip()
            emergency_contact_phone = request.form.get('emergency_contact_phone', '').strip()
            medical_history = request.form.get('medical_history', '').strip()
            allergies = request.form.get('allergies', '').strip()
            current_medications = request.form.get('current_medications', '').strip()
            insurance_details = request.form.get('insurance_details', '').strip()
            
            # Validation
            if not first_name or not last_name or not phone:
                flash('First name, last name, and phone number are required.', 'error')
                return render_template('patients/add.html')
            
            # Check if patient with same phone already exists
            existing_patient = Patient.query.filter_by(phone=phone, is_active=True).first()
            if existing_patient:
                flash('A patient with this phone number already exists.', 'error')
                return render_template('patients/add.html')
            
            # Check email if provided
            if email:
                existing_email = Patient.query.filter_by(email=email, is_active=True).first()
                if existing_email:
                    flash('A patient with this email already exists.', 'error')
                    return render_template('patients/add.html')
            
            # Generate patient ID
            patient_count = Patient.query.count()
            patient_id = f"P{patient_count + 1:06d}"
            
            # Parse date of birth
            dob = None
            if date_of_birth:
                try:
                    dob = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
                except ValueError:
                    flash('Invalid date of birth format.', 'error')
                    return render_template('patients/add.html')
            
            # Create new patient
            new_patient = Patient(
                patient_id=patient_id,
                first_name=first_name,
                last_name=last_name,
                email=email if email else None,
                phone=phone,
                whatsapp_number=whatsapp_number if whatsapp_number else phone,
                date_of_birth=dob,
                gender=gender,
                address=address,
                city=city,
                state=state,
                pincode=pincode,
                emergency_contact_name=emergency_contact_name,
                emergency_contact_phone=emergency_contact_phone,
                medical_history=medical_history,
                allergies=allergies,
                current_medications=current_medications,
                insurance_details=insurance_details
            )
            
            db.session.add(new_patient)
            db.session.commit()
            
            flash(f'Patient {new_patient.full_name} added successfully!', 'success')
            return redirect(url_for('patients.view_patient', id=new_patient.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding patient: {str(e)}', 'error')
    
    return render_template('patients/add.html')

@patients_bp.route('/<int:id>')
@login_required
def view_patient(id):
    """View patient details"""
    patient = Patient.query.get_or_404(id)
    
    if not patient.is_active:
        flash('Patient not found.', 'error')
        return redirect(url_for('patients.list_patients'))
    
    # Get patient's visits and appointments
    visits = Visit.query.filter_by(patient_id=id).order_by(Visit.date_of_visit.desc()).all()
    appointments = Appointment.query.filter_by(patient_id=id).order_by(
        Appointment.appointment_date.desc(), 
        Appointment.appointment_time.desc()
    ).all()
    
    # Get billing information
    billings = db.session.query(Billing).join(Visit).filter(
        Visit.patient_id == id
    ).order_by(Billing.created_at.desc()).all()
    
    return render_template('patients/view.html', 
                         patient=patient, 
                         visits=visits, 
                         appointments=appointments,
                         billings=billings)

@patients_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_patient(id):
    """Edit patient information"""
    patient = Patient.query.get_or_404(id)
    
    if not patient.is_active:
        flash('Patient not found.', 'error')
        return redirect(url_for('patients.list_patients'))
    
    if request.method == 'POST':
        try:
            # Update patient information
            patient.first_name = request.form.get('first_name', '').strip()
            patient.last_name = request.form.get('last_name', '').strip()
            patient.email = request.form.get('email', '').strip() or None
            patient.phone = request.form.get('phone', '').strip()
            patient.whatsapp_number = request.form.get('whatsapp_number', '').strip()
            patient.gender = request.form.get('gender')
            patient.address = request.form.get('address', '').strip()
            patient.city = request.form.get('city', '').strip()
            patient.state = request.form.get('state', '').strip()
            patient.pincode = request.form.get('pincode', '').strip()
            patient.emergency_contact_name = request.form.get('emergency_contact_name', '').strip()
            patient.emergency_contact_phone = request.form.get('emergency_contact_phone', '').strip()
            patient.medical_history = request.form.get('medical_history', '').strip()
            patient.allergies = request.form.get('allergies', '').strip()
            patient.current_medications = request.form.get('current_medications', '').strip()
            patient.insurance_details = request.form.get('insurance_details', '').strip()
            
            # Update date of birth if provided
            date_of_birth = request.form.get('date_of_birth')
            if date_of_birth:
                try:
                    patient.date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
                except ValueError:
                    flash('Invalid date of birth format.', 'error')
                    return render_template('patients/edit.html', patient=patient)
            
            patient.updated_at = datetime.utcnow()
            db.session.commit()
            
            flash(f'Patient {patient.full_name} updated successfully!', 'success')
            return redirect(url_for('patients.view_patient', id=patient.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating patient: {str(e)}', 'error')
    
    return render_template('patients/edit.html', patient=patient)

@patients_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_patient(id):
    """Soft delete patient (admin only)"""
    if not current_user.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
        flash('You do not have permission to delete patients.', 'error')
        return redirect(url_for('patients.view_patient', id=id))
    
    patient = Patient.query.get_or_404(id)
    
    try:
        # Soft delete - mark as inactive
        patient.is_active = False
        patient.updated_at = datetime.utcnow()
        db.session.commit()
        
        flash(f'Patient {patient.full_name} has been deactivated.', 'success')
        return redirect(url_for('patients.list_patients'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting patient: {str(e)}', 'error')
        return redirect(url_for('patients.view_patient', id=id))

@patients_bp.route('/<int:id>/add-visit', methods=['GET', 'POST'])
@login_required
def add_visit(id):
    """Add new visit for patient"""
    patient = Patient.query.get_or_404(id)
    
    if not patient.is_active:
        flash('Patient not found.', 'error')
        return redirect(url_for('patients.list_patients'))
    
    if request.method == 'POST':
        try:
            # Get form data
            visit_type = request.form.get('visit_type')
            date_of_visit = request.form.get('date_of_visit')
            time_of_visit = request.form.get('time_of_visit')
            duration_minutes = request.form.get('duration_minutes', 30, type=int)
            chief_complaint = request.form.get('chief_complaint', '').strip()
            diagnosis = request.form.get('diagnosis', '').strip()
            treatment_plan = request.form.get('treatment_plan', '').strip()
            remarks = request.form.get('remarks', '').strip()
            follow_up_date = request.form.get('follow_up_date')
            
            # Validation
            if not visit_type or not date_of_visit:
                flash('Visit type and date are required.', 'error')
                return render_template('patients/add_visit.html', patient=patient)
            
            # Parse dates and times
            try:
                visit_date = datetime.strptime(date_of_visit, '%Y-%m-%d').date()
                visit_time = None
                if time_of_visit:
                    visit_time = datetime.strptime(time_of_visit, '%H:%M').time()
                
                follow_up = None
                if follow_up_date:
                    follow_up = datetime.strptime(follow_up_date, '%Y-%m-%d').date()
                    
            except ValueError:
                flash('Invalid date or time format.', 'error')
                return render_template('patients/add_visit.html', patient=patient)
            
            # Create new visit
            new_visit = Visit(
                patient_id=patient.id,
                doctor_id=current_user.id if current_user.role == UserRole.DOCTOR else None,
                visit_type=VisitType(visit_type),
                date_of_visit=visit_date,
                time_of_visit=visit_time,
                duration_minutes=duration_minutes,
                chief_complaint=chief_complaint,
                diagnosis=diagnosis,
                treatment_plan=treatment_plan,
                remarks=remarks,
                follow_up_date=follow_up
            )
            
            db.session.add(new_visit)
            db.session.commit()
            
            flash('Visit added successfully!', 'success')
            return redirect(url_for('patients.view_patient', id=patient.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding visit: {str(e)}', 'error')
    
    # Get doctors for dropdown
    doctors = User.query.filter_by(role=UserRole.DOCTOR, is_active=True).all()
    
    return render_template('patients/add_visit.html', patient=patient, doctors=doctors)

@patients_bp.route('/api/search')
@login_required
def api_search():
    """API endpoint for patient search"""
    query = request.args.get('q', '').strip()
    
    if not query or len(query) < 2:
        return jsonify([])
    
    search_term = f"%{query}%"
    patients = Patient.query.filter(
        or_(
            Patient.first_name.ilike(search_term),
            Patient.last_name.ilike(search_term),
            Patient.phone.ilike(search_term),
            Patient.patient_id.ilike(search_term)
        ),
        Patient.is_active == True
    ).limit(10).all()
    
    results = []
    for patient in patients:
        results.append({
            'id': patient.id,
            'patient_id': patient.patient_id,
            'name': patient.full_name,
            'phone': patient.phone,
            'age': patient.age
        })
    
    return jsonify(results)
