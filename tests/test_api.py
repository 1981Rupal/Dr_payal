# tests/test_api.py - API Endpoint Tests

import pytest
import json
from datetime import date, time, datetime
from models import Patient, Appointment, User, UserRole, AppointmentStatus, VisitType

class TestAPIEndpoints:
    """Test API endpoints"""
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'status' in data
        assert 'timestamp' in data
        assert data['status'] == 'healthy'
    
    def test_api_patients_list(self, authenticated_client, test_patient):
        """Test GET /api/patients"""
        response = authenticated_client.get('/api/patients')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'patients' in data
        assert 'pagination' in data
        assert len(data['patients']) >= 1
        
        # Check patient data structure
        patient = data['patients'][0]
        assert 'id' in patient
        assert 'patient_id' in patient
        assert 'full_name' in patient
        assert 'phone' in patient
    
    def test_api_patients_search(self, authenticated_client, test_patient):
        """Test patient search API"""
        response = authenticated_client.get('/api/patients?search=Test')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert len(data['patients']) >= 1
        
        # Search should find our test patient
        found = any(p['first_name'] == 'Test' for p in data['patients'])
        assert found
    
    def test_api_patient_detail(self, authenticated_client, test_patient):
        """Test GET /api/patients/<id>"""
        response = authenticated_client.get(f'/api/patients/{test_patient.id}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['id'] == test_patient.id
        assert data['patient_id'] == test_patient.patient_id
        assert data['full_name'] == test_patient.full_name
        assert 'recent_visits' in data
        assert 'upcoming_appointments' in data
    
    def test_api_patient_not_found(self, authenticated_client):
        """Test patient not found"""
        response = authenticated_client.get('/api/patients/99999')
        assert response.status_code == 404
    
    def test_api_appointments_list(self, authenticated_client, test_appointment):
        """Test GET /api/appointments"""
        response = authenticated_client.get('/api/appointments')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'appointments' in data
        assert 'pagination' in data
        assert len(data['appointments']) >= 1
        
        # Check appointment data structure
        appointment = data['appointments'][0]
        assert 'id' in appointment
        assert 'patient' in appointment
        assert 'doctor' in appointment
        assert 'appointment_date' in appointment
        assert 'status' in appointment
    
    def test_api_appointments_filter_by_date(self, authenticated_client, test_appointment):
        """Test appointment filtering by date"""
        today = date.today().strftime('%Y-%m-%d')
        response = authenticated_client.get(f'/api/appointments?date={today}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        # Should find today's appointments
        assert len(data['appointments']) >= 1
    
    def test_api_appointments_filter_by_status(self, authenticated_client, test_appointment):
        """Test appointment filtering by status"""
        response = authenticated_client.get('/api/appointments?status=pending')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        # All returned appointments should be pending
        for appointment in data['appointments']:
            assert appointment['status'] == 'pending'
    
    def test_api_create_appointment(self, authenticated_client, test_patient, test_doctor):
        """Test POST /api/appointments"""
        appointment_data = {
            'patient_id': test_patient.id,
            'doctor_id': test_doctor.id,
            'appointment_date': '2024-12-25',
            'appointment_time': '14:30',
            'visit_type': 'clinic',
            'reason': 'Test appointment via API',
            'duration_minutes': 30
        }
        
        response = authenticated_client.post(
            '/api/appointments',
            data=json.dumps(appointment_data),
            content_type='application/json'
        )
        assert response.status_code == 201
        
        data = json.loads(response.data)
        assert 'message' in data
        assert 'appointment' in data
        assert data['appointment']['reason'] == 'Test appointment via API'
    
    def test_api_create_appointment_missing_data(self, authenticated_client):
        """Test appointment creation with missing data"""
        appointment_data = {
            'patient_id': 1,
            # Missing required fields
        }
        
        response = authenticated_client.post(
            '/api/appointments',
            data=json.dumps(appointment_data),
            content_type='application/json'
        )
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_api_create_appointment_invalid_patient(self, authenticated_client, test_doctor):
        """Test appointment creation with invalid patient"""
        appointment_data = {
            'patient_id': 99999,  # Non-existent patient
            'doctor_id': test_doctor.id,
            'appointment_date': '2024-12-25',
            'appointment_time': '14:30',
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
        assert 'Invalid patient' in data['error']
    
    def test_api_update_appointment_status(self, authenticated_client, test_appointment):
        """Test PUT /api/appointments/<id>/status"""
        response = authenticated_client.put(
            f'/api/appointments/{test_appointment.id}/status',
            data=json.dumps({'status': 'confirmed'}),
            content_type='application/json'
        )
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'message' in data
        assert data['appointment']['status'] == 'confirmed'
    
    def test_api_update_appointment_status_invalid(self, authenticated_client, test_appointment):
        """Test appointment status update with invalid status"""
        response = authenticated_client.put(
            f'/api/appointments/{test_appointment.id}/status',
            data=json.dumps({'status': 'invalid_status'}),
            content_type='application/json'
        )
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_api_dashboard_stats(self, authenticated_client, test_patient, test_appointment):
        """Test GET /api/dashboard/stats"""
        response = authenticated_client.get('/api/dashboard/stats')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        # Should contain some statistics
        assert isinstance(data, dict)
        # Stats content depends on user role
    
    def test_api_search(self, authenticated_client, test_patient):
        """Test GET /api/search"""
        response = authenticated_client.get('/api/search?q=Test')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'results' in data
        assert isinstance(data['results'], list)
        
        # Should find our test patient
        if data['results']:
            result = data['results'][0]
            assert 'type' in result
            assert 'title' in result
            assert 'url' in result
    
    def test_api_search_short_query(self, authenticated_client):
        """Test search with short query"""
        response = authenticated_client.get('/api/search?q=T')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['results'] == []  # Should return empty for short queries
    
    def test_api_unauthorized_access(self, client):
        """Test API access without authentication"""
        endpoints = [
            '/api/patients',
            '/api/appointments',
            '/api/dashboard/stats',
            '/api/search'
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 302  # Redirect to login
    
    def test_api_error_handling(self, authenticated_client):
        """Test API error handling"""
        # Test non-existent endpoint
        response = authenticated_client.get('/api/nonexistent')
        assert response.status_code == 404
        
        # Test invalid JSON
        response = authenticated_client.post(
            '/api/appointments',
            data='invalid json',
            content_type='application/json'
        )
        assert response.status_code == 400

class TestAPIPermissions:
    """Test API permissions and role-based access"""
    
    def test_doctor_can_access_own_appointments(self, client, test_doctor, test_appointment):
        """Test that doctors can access their own appointments"""
        # Login as doctor
        client.post('/auth/login', data={
            'username': test_doctor.username,
            'password': 'doctorpass'
        })
        
        response = client.get('/api/appointments')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        # Should only see appointments for this doctor
        for appointment in data['appointments']:
            assert appointment['doctor']['id'] == test_doctor.id
    
    def test_api_pagination(self, authenticated_client, app):
        """Test API pagination"""
        # Create multiple patients for pagination testing
        with app.app_context():
            from models import db
            for i in range(25):  # Create more than default page size
                patient = Patient(
                    patient_id=f'P{i:03d}',
                    first_name=f'Patient{i}',
                    last_name='Test',
                    phone=f'+123456789{i:02d}',
                    email=f'patient{i}@test.com'
                )
                db.session.add(patient)
            db.session.commit()
        
        # Test first page
        response = authenticated_client.get('/api/patients?page=1&per_page=10')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert len(data['patients']) == 10
        assert data['pagination']['page'] == 1
        assert data['pagination']['has_next'] == True
        
        # Test second page
        response = authenticated_client.get('/api/patients?page=2&per_page=10')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['pagination']['page'] == 2
        assert data['pagination']['has_prev'] == True
