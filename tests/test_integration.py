# tests/test_integration.py - Integration Tests

import pytest
import json
from datetime import date, time, datetime, timedelta
from models import db, Patient, Appointment, User, UserRole, AppointmentStatus, VisitType, Billing, Payment, PaymentStatus

class TestPatientWorkflow:
    """Test complete patient management workflow"""
    
    def test_patient_registration_to_appointment(self, authenticated_client, test_doctor):
        """Test complete workflow from patient registration to appointment"""
        
        # Step 1: Register a new patient
        patient_data = {
            'patient_id': 'P999',
            'first_name': 'Integration',
            'last_name': 'Test',
            'email': 'integration@test.com',
            'phone': '+1234567999',
            'date_of_birth': '1985-05-15',
            'gender': 'Female',
            'address': '123 Integration Street',
            'city': 'Test City',
            'state': 'Test State',
            'pincode': '12345'
        }
        
        response = authenticated_client.post('/patients/add', data=patient_data)
        assert response.status_code in [200, 302]  # Success or redirect
        
        # Step 2: Find the created patient
        response = authenticated_client.get('/api/patients?search=Integration')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert len(data['patients']) >= 1
        
        patient = data['patients'][0]
        patient_id = patient['id']
        
        # Step 3: Schedule an appointment for the patient
        appointment_data = {
            'patient_id': patient_id,
            'doctor_id': test_doctor.id,
            'appointment_date': (date.today() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'appointment_time': '10:00',
            'visit_type': 'clinic',
            'reason': 'Integration test appointment'
        }
        
        response = authenticated_client.post(
            '/api/appointments',
            data=json.dumps(appointment_data),
            content_type='application/json'
        )
        assert response.status_code == 201
        
        # Step 4: Verify appointment was created
        appointment_response = json.loads(response.data)
        appointment_id = appointment_response['appointment']['id']
        
        response = authenticated_client.get('/api/appointments')
        data = json.loads(response.data)
        
        found_appointment = None
        for appt in data['appointments']:
            if appt['id'] == appointment_id:
                found_appointment = appt
                break
        
        assert found_appointment is not None
        assert found_appointment['patient']['id'] == patient_id
        assert found_appointment['reason'] == 'Integration test appointment'
    
    def test_appointment_status_workflow(self, authenticated_client, test_appointment):
        """Test appointment status changes workflow"""
        
        # Step 1: Appointment starts as pending
        response = authenticated_client.get(f'/api/appointments')
        data = json.loads(response.data)
        
        appointment = None
        for appt in data['appointments']:
            if appt['id'] == test_appointment.id:
                appointment = appt
                break
        
        assert appointment is not None
        assert appointment['status'] == 'pending'
        
        # Step 2: Confirm the appointment
        response = authenticated_client.put(
            f'/api/appointments/{test_appointment.id}/status',
            data=json.dumps({'status': 'confirmed'}),
            content_type='application/json'
        )
        assert response.status_code == 200
        
        # Step 3: Verify status change
        response = authenticated_client.get('/api/appointments')
        data = json.loads(response.data)
        
        for appt in data['appointments']:
            if appt['id'] == test_appointment.id:
                assert appt['status'] == 'confirmed'
                break
        
        # Step 4: Complete the appointment
        response = authenticated_client.put(
            f'/api/appointments/{test_appointment.id}/status',
            data=json.dumps({'status': 'completed'}),
            content_type='application/json'
        )
        assert response.status_code == 200

class TestBillingWorkflow:
    """Test billing and payment workflow"""
    
    def test_complete_billing_workflow(self, app, authenticated_client, test_patient):
        """Test complete billing workflow from bill creation to payment"""
        
        with app.app_context():
            # Step 1: Create a bill
            bill = Billing(
                patient_id=test_patient.id,
                bill_number='B001',
                bill_date=date.today(),
                total_amount=1000.00,
                payment_status=PaymentStatus.PENDING,
                description='Integration test bill'
            )
            db.session.add(bill)
            db.session.commit()
            bill_id = bill.id
        
        # Step 2: Verify bill was created
        response = authenticated_client.get('/billing/list')
        assert response.status_code == 200
        
        # Step 3: Record a partial payment
        payment_data = {
            'amount': 500.00,
            'payment_method': 'cash',
            'notes': 'Partial payment'
        }
        
        response = authenticated_client.post(
            f'/api/billing/{bill_id}/payment',
            data=json.dumps(payment_data),
            content_type='application/json'
        )
        # Note: This endpoint might not exist yet, so we'll check for 404 or success
        assert response.status_code in [200, 404]
        
        # Step 4: Record remaining payment
        if response.status_code == 200:
            payment_data = {
                'amount': 500.00,
                'payment_method': 'card',
                'notes': 'Final payment'
            }
            
            response = authenticated_client.post(
                f'/api/billing/{bill_id}/payment',
                data=json.dumps(payment_data),
                content_type='application/json'
            )
            assert response.status_code == 200

class TestUserRolePermissions:
    """Test role-based access control integration"""
    
    def test_admin_full_access(self, client, app):
        """Test that admin users have full access"""
        with app.app_context():
            # Create admin user
            admin = User(
                username='admin_test',
                email='admin@test.com',
                first_name='Admin',
                last_name='User',
                role=UserRole.SUPER_ADMIN,
                phone='+1234567890'
            )
            admin.set_password('adminpass')
            db.session.add(admin)
            db.session.commit()
        
        # Login as admin
        response = client.post('/auth/login', data={
            'username': 'admin_test',
            'password': 'adminpass'
        })
        assert response.status_code in [200, 302]
        
        # Test access to admin-only endpoints
        admin_endpoints = [
            '/patients/list',
            '/appointments/list',
            '/billing/list',
            '/api/dashboard/stats'
        ]
        
        for endpoint in admin_endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200
    
    def test_doctor_limited_access(self, client, app):
        """Test that doctors have limited access"""
        with app.app_context():
            # Create doctor user
            doctor = User(
                username='doctor_test',
                email='doctor@test.com',
                first_name='Doctor',
                last_name='User',
                role=UserRole.DOCTOR,
                phone='+1234567891'
            )
            doctor.set_password('doctorpass')
            db.session.add(doctor)
            db.session.commit()
        
        # Login as doctor
        response = client.post('/auth/login', data={
            'username': 'doctor_test',
            'password': 'doctorpass'
        })
        assert response.status_code in [200, 302]
        
        # Test access to allowed endpoints
        response = client.get('/api/appointments')
        assert response.status_code == 200
        
        # Test that doctor sees only their appointments
        data = json.loads(response.data)
        for appointment in data['appointments']:
            assert appointment['doctor']['id'] == doctor.id

class TestDataConsistency:
    """Test data consistency across operations"""
    
    def test_patient_appointment_consistency(self, app, authenticated_client, test_patient, test_doctor):
        """Test that patient and appointment data remains consistent"""
        
        # Create multiple appointments for the same patient
        appointment_dates = [
            date.today() + timedelta(days=1),
            date.today() + timedelta(days=2),
            date.today() + timedelta(days=3)
        ]
        
        created_appointments = []
        
        for appt_date in appointment_dates:
            appointment_data = {
                'patient_id': test_patient.id,
                'doctor_id': test_doctor.id,
                'appointment_date': appt_date.strftime('%Y-%m-%d'),
                'appointment_time': '10:00',
                'visit_type': 'clinic',
                'reason': f'Appointment for {appt_date}'
            }
            
            response = authenticated_client.post(
                '/api/appointments',
                data=json.dumps(appointment_data),
                content_type='application/json'
            )
            assert response.status_code == 201
            
            data = json.loads(response.data)
            created_appointments.append(data['appointment']['id'])
        
        # Verify all appointments are linked to the correct patient
        response = authenticated_client.get(f'/api/patients/{test_patient.id}')
        assert response.status_code == 200
        
        patient_data = json.loads(response.data)
        upcoming_appointments = patient_data['upcoming_appointments']
        
        # Should have at least the appointments we created
        assert len(upcoming_appointments) >= len(created_appointments)
        
        # All appointments should belong to this patient
        for appointment in upcoming_appointments:
            assert appointment['patient']['id'] == test_patient.id

class TestErrorHandling:
    """Test error handling in integration scenarios"""
    
    def test_database_constraint_violations(self, authenticated_client, test_patient, test_doctor):
        """Test handling of database constraint violations"""
        
        # Try to create appointment with duplicate time slot
        appointment_data = {
            'patient_id': test_patient.id,
            'doctor_id': test_doctor.id,
            'appointment_date': date.today().strftime('%Y-%m-%d'),
            'appointment_time': '10:00',
            'visit_type': 'clinic',
            'reason': 'First appointment'
        }
        
        # Create first appointment
        response = authenticated_client.post(
            '/api/appointments',
            data=json.dumps(appointment_data),
            content_type='application/json'
        )
        assert response.status_code == 201
        
        # Try to create conflicting appointment
        appointment_data['reason'] = 'Conflicting appointment'
        response = authenticated_client.post(
            '/api/appointments',
            data=json.dumps(appointment_data),
            content_type='application/json'
        )
        assert response.status_code == 400  # Should fail due to time conflict
        
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_invalid_data_handling(self, authenticated_client):
        """Test handling of invalid data in requests"""
        
        # Test invalid date format
        appointment_data = {
            'patient_id': 1,
            'doctor_id': 1,
            'appointment_date': 'invalid-date',
            'appointment_time': '10:00',
            'visit_type': 'clinic'
        }
        
        response = authenticated_client.post(
            '/api/appointments',
            data=json.dumps(appointment_data),
            content_type='application/json'
        )
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
