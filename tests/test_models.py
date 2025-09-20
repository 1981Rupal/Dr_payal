# tests/test_models.py - Model Tests

import pytest
from datetime import date, time, datetime
from models import (
    User, Patient, Appointment, Visit, Billing, Payment, 
    Prescription, PrescriptionMedication, TreatmentPackage, PatientPackage,
    UserRole, AppointmentStatus, PaymentStatus, VisitType
)

class TestUser:
    """Test User model"""
    
    def test_create_user(self, app):
        """Test user creation"""
        with app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                first_name='Test',
                last_name='User',
                role=UserRole.DOCTOR
            )
            user.set_password('password123')
            
            assert user.username == 'testuser'
            assert user.email == 'test@example.com'
            assert user.full_name == 'Test User'
            assert user.role == UserRole.DOCTOR
            assert user.check_password('password123')
            assert not user.check_password('wrongpassword')
    
    def test_user_roles(self, app):
        """Test user role functionality"""
        with app.app_context():
            admin = User(username='admin', email='admin@test.com', 
                        first_name='Admin', last_name='User', role=UserRole.ADMIN)
            doctor = User(username='doctor', email='doctor@test.com',
                         first_name='Doctor', last_name='User', role=UserRole.DOCTOR)
            
            assert admin.has_role(UserRole.ADMIN)
            assert not admin.has_role(UserRole.DOCTOR)
            assert doctor.has_role(UserRole.DOCTOR)
            assert not doctor.has_role(UserRole.ADMIN)
    
    def test_user_permissions(self, app):
        """Test user permission system"""
        with app.app_context():
            admin = User(username='admin', email='admin@test.com',
                        first_name='Admin', last_name='User', role=UserRole.ADMIN)
            staff = User(username='staff', email='staff@test.com',
                        first_name='Staff', last_name='User', role=UserRole.STAFF)
            patient = User(username='patient', email='patient@test.com',
                          first_name='Patient', last_name='User', role=UserRole.PATIENT)
            
            assert admin.can_access('patients')
            assert admin.can_access('billing')
            assert staff.can_access('patients')
            assert staff.can_access('billing')
            assert not patient.can_access('billing')
            assert patient.can_access('own_data')

class TestPatient:
    """Test Patient model"""
    
    def test_create_patient(self, app):
        """Test patient creation"""
        with app.app_context():
            patient = Patient(
                patient_id='P001',
                first_name='John',
                last_name='Doe',
                email='john@example.com',
                phone='+1234567890',
                date_of_birth=date(1990, 1, 1),
                gender='Male',
                address='123 Main St',
                city='Test City'
            )
            
            assert patient.patient_id == 'P001'
            assert patient.full_name == 'John Doe'
            assert patient.age == date.today().year - 1990
    
    def test_patient_age_calculation(self, app):
        """Test patient age calculation"""
        with app.app_context():
            # Patient born in 1990
            patient = Patient(
                patient_id='P002',
                first_name='Jane',
                last_name='Doe',
                date_of_birth=date(1990, 6, 15)
            )
            
            expected_age = date.today().year - 1990
            if date.today() < date(date.today().year, 6, 15):
                expected_age -= 1
            
            assert patient.age == expected_age

class TestAppointment:
    """Test Appointment model"""
    
    def test_create_appointment(self, app, test_patient, test_doctor):
        """Test appointment creation"""
        with app.app_context():
            appointment = Appointment(
                patient_id=test_patient.id,
                doctor_id=test_doctor.id,
                appointment_date=date.today(),
                appointment_time=time(10, 0),
                visit_type=VisitType.CLINIC,
                status=AppointmentStatus.PENDING,
                reason='Regular checkup'
            )
            
            assert appointment.patient_id == test_patient.id
            assert appointment.doctor_id == test_doctor.id
            assert appointment.visit_type == VisitType.CLINIC
            assert appointment.status == AppointmentStatus.PENDING

class TestBilling:
    """Test Billing model"""
    
    def test_create_billing(self, app, test_patient, test_doctor):
        """Test billing creation"""
        with app.app_context():
            # Create a visit first
            visit = Visit(
                patient_id=test_patient.id,
                doctor_id=test_doctor.id,
                visit_type=VisitType.CLINIC,
                date_of_visit=date.today(),
                diagnosis='Test diagnosis'
            )
            from models import db
            db.session.add(visit)
            db.session.flush()
            
            billing = Billing(
                visit_id=visit.id,
                bill_number='BILL001',
                subtotal=500.0,
                discount_amount=50.0,
                tax_amount=45.0,
                total_amount=495.0,
                payment_status=PaymentStatus.PENDING
            )
            
            assert billing.bill_number == 'BILL001'
            assert billing.total_amount == 495.0
            assert billing.payment_status == PaymentStatus.PENDING

class TestPrescription:
    """Test Prescription model"""
    
    def test_create_prescription(self, app, test_patient, test_doctor):
        """Test prescription creation"""
        with app.app_context():
            prescription = Prescription(
                patient_id=test_patient.id,
                doctor_id=test_doctor.id,
                prescription_date=date.today(),
                diagnosis='Test diagnosis',
                instructions='Take as prescribed'
            )
            
            # Add medication
            medication = PrescriptionMedication(
                prescription=prescription,
                medication_name='Test Medicine',
                dosage='10mg',
                frequency='Twice daily',
                duration='7 days',
                instructions='Take with food'
            )
            
            assert prescription.patient_id == test_patient.id
            assert prescription.doctor_id == test_doctor.id
            assert len(prescription.medications) == 1
            assert prescription.medications[0].medication_name == 'Test Medicine'

class TestTreatmentPackage:
    """Test Treatment Package model"""
    
    def test_create_package(self, app):
        """Test treatment package creation"""
        with app.app_context():
            package = TreatmentPackage(
                name='Basic Physiotherapy',
                description='Basic physiotherapy package',
                total_sessions=10,
                price_per_session=500.0,
                total_price=4500.0,
                validity_days=90
            )
            
            assert package.name == 'Basic Physiotherapy'
            assert package.total_sessions == 10
            assert package.total_price == 4500.0
    
    def test_patient_package_subscription(self, app, test_patient):
        """Test patient package subscription"""
        with app.app_context():
            from models import db
            
            # Create package
            package = TreatmentPackage(
                name='Premium Package',
                total_sessions=20,
                price_per_session=600.0,
                total_price=10800.0,
                validity_days=120
            )
            db.session.add(package)
            db.session.flush()
            
            # Create patient package
            patient_package = PatientPackage(
                patient_id=test_patient.id,
                package_id=package.id,
                sessions_remaining=20,
                start_date=date.today(),
                expiry_date=date.today()
            )
            
            assert patient_package.sessions_remaining == 20
            assert patient_package.is_active == True
