# tests/conftest.py - Test Configuration and Fixtures

import pytest
import tempfile
import os
from app_enhanced import create_app
from models import db, User, Patient, Appointment, UserRole, AppointmentStatus, VisitType
from datetime import date, time, datetime

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Create a temporary file to serve as the database
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret-key"
    })

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

@pytest.fixture
def auth(client):
    """Authentication helper."""
    class AuthActions:
        def __init__(self, client):
            self._client = client

        def login(self, username='testuser', password='testpass'):
            return self._client.post(
                '/login',
                data={'username': username, 'password': password}
            )

        def logout(self):
            return self._client.get('/logout')

    return AuthActions(client)

@pytest.fixture
def test_user(app):
    """Create a test user."""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            role=UserRole.ADMIN,
            phone='+1234567890'
        )
        user.set_password('testpass')
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def test_doctor(app):
    """Create a test doctor."""
    with app.app_context():
        doctor = User(
            username='testdoctor',
            email='doctor@example.com',
            first_name='Dr. Test',
            last_name='Doctor',
            role=UserRole.DOCTOR,
            phone='+1234567891'
        )
        doctor.set_password('doctorpass')
        db.session.add(doctor)
        db.session.commit()
        return doctor

@pytest.fixture
def test_patient(app):
    """Create a test patient."""
    with app.app_context():
        patient = Patient(
            patient_id='P001',
            first_name='Test',
            last_name='Patient',
            email='patient@example.com',
            phone='+1234567892',
            date_of_birth=date(1990, 1, 1),
            gender='Male',
            address='123 Test Street',
            city='Test City',
            state='Test State',
            pincode='12345'
        )
        db.session.add(patient)
        db.session.commit()
        return patient

@pytest.fixture
def test_appointment(app, test_patient, test_doctor):
    """Create a test appointment."""
    with app.app_context():
        appointment = Appointment(
            patient_id=test_patient.id,
            doctor_id=test_doctor.id,
            appointment_date=date.today(),
            appointment_time=time(10, 0),
            visit_type=VisitType.CLINIC,
            status=AppointmentStatus.PENDING,
            reason='Test appointment'
        )
        db.session.add(appointment)
        db.session.commit()
        return appointment

@pytest.fixture
def authenticated_client(client, test_user):
    """A client with an authenticated user."""
    client.post('/login', data={
        'username': test_user.username,
        'password': 'testpass'
    })
    return client
