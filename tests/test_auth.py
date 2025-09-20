# tests/test_auth.py - Authentication Tests

import pytest
from flask import url_for
from models import User, UserRole

class TestAuthentication:
    """Test authentication functionality"""
    
    def test_login_page_loads(self, client):
        """Test that login page loads correctly"""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'Login' in response.data
    
    def test_valid_login(self, client, test_user):
        """Test login with valid credentials"""
        response = client.post('/login', data={
            'username': test_user.username,
            'password': 'testpass'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Should redirect to dashboard after successful login
        assert b'Dashboard' in response.data or b'Welcome' in response.data
    
    def test_invalid_login(self, client, test_user):
        """Test login with invalid credentials"""
        response = client.post('/login', data={
            'username': test_user.username,
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 200
        assert b'Invalid username or password' in response.data or b'Login' in response.data
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        response = client.post('/login', data={
            'username': 'nonexistent',
            'password': 'password'
        })
        
        assert response.status_code == 200
        assert b'Invalid username or password' in response.data or b'Login' in response.data
    
    def test_logout(self, authenticated_client):
        """Test user logout"""
        response = authenticated_client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
        # Should redirect to login page after logout
        assert b'Login' in response.data
    
    def test_dashboard_requires_login(self, client):
        """Test that dashboard requires authentication"""
        response = client.get('/dashboard')
        assert response.status_code == 302  # Redirect to login
        
        # Follow redirect
        response = client.get('/dashboard', follow_redirects=True)
        assert b'Login' in response.data
    
    def test_authenticated_dashboard_access(self, authenticated_client):
        """Test dashboard access with authenticated user"""
        response = authenticated_client.get('/dashboard')
        assert response.status_code == 200
        assert b'Dashboard' in response.data or b'Welcome' in response.data

class TestRoleBasedAccess:
    """Test role-based access control"""
    
    def test_admin_access(self, app, client):
        """Test admin user access"""
        with app.app_context():
            # Create admin user
            admin = User(
                username='admin',
                email='admin@test.com',
                first_name='Admin',
                last_name='User',
                role=UserRole.ADMIN
            )
            admin.set_password('adminpass')
            from models import db
            db.session.add(admin)
            db.session.commit()
            
            # Login as admin
            client.post('/login', data={
                'username': 'admin',
                'password': 'adminpass'
            })
            
            # Admin should have access to all areas
            response = client.get('/dashboard')
            assert response.status_code == 200
    
    def test_doctor_access(self, app, client):
        """Test doctor user access"""
        with app.app_context():
            # Create doctor user
            doctor = User(
                username='doctor',
                email='doctor@test.com',
                first_name='Doctor',
                last_name='User',
                role=UserRole.DOCTOR
            )
            doctor.set_password('doctorpass')
            from models import db
            db.session.add(doctor)
            db.session.commit()
            
            # Login as doctor
            client.post('/login', data={
                'username': 'doctor',
                'password': 'doctorpass'
            })
            
            # Doctor should have access to dashboard
            response = client.get('/dashboard')
            assert response.status_code == 200
    
    def test_staff_access(self, app, client):
        """Test staff user access"""
        with app.app_context():
            # Create staff user
            staff = User(
                username='staff',
                email='staff@test.com',
                first_name='Staff',
                last_name='User',
                role=UserRole.STAFF
            )
            staff.set_password('staffpass')
            from models import db
            db.session.add(staff)
            db.session.commit()
            
            # Login as staff
            client.post('/login', data={
                'username': 'staff',
                'password': 'staffpass'
            })
            
            # Staff should have access to dashboard
            response = client.get('/dashboard')
            assert response.status_code == 200
    
    def test_patient_access(self, app, client):
        """Test patient user access"""
        with app.app_context():
            # Create patient user
            patient_user = User(
                username='patient',
                email='patient@test.com',
                first_name='Patient',
                last_name='User',
                role=UserRole.PATIENT
            )
            patient_user.set_password('patientpass')
            from models import db
            db.session.add(patient_user)
            db.session.commit()
            
            # Login as patient
            client.post('/login', data={
                'username': 'patient',
                'password': 'patientpass'
            })
            
            # Patient should have access to dashboard (patient portal)
            response = client.get('/dashboard')
            assert response.status_code == 200

class TestPasswordSecurity:
    """Test password security features"""
    
    def test_password_hashing(self, app):
        """Test that passwords are properly hashed"""
        with app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                first_name='Test',
                last_name='User',
                role=UserRole.STAFF
            )
            user.set_password('mypassword')
            
            # Password should be hashed, not stored in plain text
            assert user.password_hash != 'mypassword'
            assert user.check_password('mypassword')
            assert not user.check_password('wrongpassword')
    
    def test_password_verification(self, app):
        """Test password verification"""
        with app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                first_name='Test',
                last_name='User',
                role=UserRole.STAFF
            )
            
            # Test various password scenarios
            user.set_password('StrongPassword123!')
            assert user.check_password('StrongPassword123!')
            assert not user.check_password('strongpassword123!')  # Case sensitive
            assert not user.check_password('StrongPassword123')   # Missing character
            assert not user.check_password('')                    # Empty password

class TestSessionManagement:
    """Test session management"""
    
    def test_session_persistence(self, authenticated_client):
        """Test that session persists across requests"""
        # First request should be authenticated
        response = authenticated_client.get('/dashboard')
        assert response.status_code == 200
        
        # Second request should still be authenticated
        response = authenticated_client.get('/dashboard')
        assert response.status_code == 200
    
    def test_session_cleanup_on_logout(self, authenticated_client):
        """Test that session is cleaned up on logout"""
        # Verify authenticated access
        response = authenticated_client.get('/dashboard')
        assert response.status_code == 200
        
        # Logout
        authenticated_client.get('/logout')
        
        # Should no longer have access
        response = authenticated_client.get('/dashboard')
        assert response.status_code == 302  # Redirect to login
