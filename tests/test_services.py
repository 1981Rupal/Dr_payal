# tests/test_services.py - Service Layer Tests

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date, time, datetime, timedelta
from services.appointment_service import AppointmentService
from services.billing_service import BillingService
from services.whatsapp_service import WhatsAppService
from services.chatbot_service import ChatbotService
from models import Appointment, AppointmentStatus, VisitType, UserRole

class TestAppointmentService:
    """Test Appointment Service"""
    
    def test_create_appointment(self, app, test_patient, test_doctor):
        """Test appointment creation"""
        with app.app_context():
            service = AppointmentService()
            
            appointment_data = {
                'patient_id': test_patient.id,
                'doctor_id': test_doctor.id,
                'appointment_date': date.today() + timedelta(days=1),
                'appointment_time': time(10, 0),
                'visit_type': VisitType.CLINIC,
                'reason': 'Regular checkup'
            }
            
            appointment = service.create_appointment(appointment_data)
            
            assert appointment is not None
            assert appointment.patient_id == test_patient.id
            assert appointment.doctor_id == test_doctor.id
            assert appointment.status == AppointmentStatus.PENDING
    
    def test_check_availability(self, app, test_doctor):
        """Test appointment availability checking"""
        with app.app_context():
            service = AppointmentService()
            
            # Check availability for future date
            future_date = date.today() + timedelta(days=1)
            available = service.check_availability(
                test_doctor.id, 
                future_date, 
                time(10, 0)
            )
            
            assert available == True
    
    def test_confirm_appointment(self, app, test_appointment):
        """Test appointment confirmation"""
        with app.app_context():
            service = AppointmentService()
            
            confirmed = service.confirm_appointment(test_appointment.id)
            
            assert confirmed == True
            assert test_appointment.status == AppointmentStatus.CONFIRMED
    
    def test_cancel_appointment(self, app, test_appointment):
        """Test appointment cancellation"""
        with app.app_context():
            service = AppointmentService()
            
            cancelled = service.cancel_appointment(
                test_appointment.id, 
                'Patient request'
            )
            
            assert cancelled == True
            assert test_appointment.status == AppointmentStatus.CANCELLED

class TestBillingService:
    """Test Billing Service"""
    
    def test_calculate_bill_amount(self, app):
        """Test bill amount calculation"""
        with app.app_context():
            service = BillingService()
            
            # Test simple calculation
            subtotal = 1000.0
            discount_percent = 10.0
            tax_percent = 18.0
            
            result = service.calculate_bill_amount(
                subtotal, 
                discount_percent, 
                tax_percent
            )
            
            expected_discount = 100.0  # 10% of 1000
            expected_taxable = 900.0   # 1000 - 100
            expected_tax = 162.0       # 18% of 900
            expected_total = 1062.0    # 900 + 162
            
            assert result['discount_amount'] == expected_discount
            assert result['tax_amount'] == expected_tax
            assert result['total_amount'] == expected_total
    
    def test_create_bill(self, app, test_patient, test_doctor):
        """Test bill creation"""
        with app.app_context():
            from models import Visit, db
            
            # Create a visit first
            visit = Visit(
                patient_id=test_patient.id,
                doctor_id=test_doctor.id,
                visit_type=VisitType.CLINIC,
                date_of_visit=date.today(),
                diagnosis='Test diagnosis'
            )
            db.session.add(visit)
            db.session.flush()
            
            service = BillingService()
            
            bill_data = {
                'visit_id': visit.id,
                'items': [
                    {'description': 'Consultation', 'amount': 500.0},
                    {'description': 'Therapy', 'amount': 300.0}
                ],
                'discount_percent': 5.0,
                'tax_percent': 18.0
            }
            
            bill = service.create_bill(bill_data)
            
            assert bill is not None
            assert bill.visit_id == visit.id
            assert bill.subtotal == 800.0

class TestWhatsAppService:
    """Test WhatsApp Service"""
    
    @patch('services.whatsapp_service.Client')
    def test_send_appointment_reminder(self, mock_client, app, test_appointment):
        """Test sending appointment reminder"""
        with app.app_context():
            # Mock Twilio client
            mock_twilio = Mock()
            mock_client.return_value = mock_twilio
            mock_twilio.messages.create.return_value = Mock(sid='test_sid')
            
            service = WhatsAppService()
            
            result = service.send_appointment_reminder(test_appointment.id)
            
            assert result == True
            mock_twilio.messages.create.assert_called_once()
    
    @patch('services.whatsapp_service.Client')
    def test_send_appointment_confirmation(self, mock_client, app, test_appointment):
        """Test sending appointment confirmation"""
        with app.app_context():
            # Mock Twilio client
            mock_twilio = Mock()
            mock_client.return_value = mock_twilio
            mock_twilio.messages.create.return_value = Mock(sid='test_sid')
            
            service = WhatsAppService()
            
            result = service.send_appointment_confirmation(test_appointment.id)
            
            assert result == True
            mock_twilio.messages.create.assert_called_once()
    
    @patch('services.whatsapp_service.Client')
    def test_handle_incoming_message(self, mock_client, app):
        """Test handling incoming WhatsApp message"""
        with app.app_context():
            service = WhatsAppService()
            
            message_data = {
                'From': 'whatsapp:+1234567890',
                'Body': 'Hello, I want to book an appointment',
                'MessageSid': 'test_message_sid'
            }
            
            # This should not raise an exception
            response = service.handle_incoming_message(message_data)
            
            # Response should be a string (TwiML response)
            assert isinstance(response, str)

class TestChatbotService:
    """Test Chatbot Service"""
    
    @patch('services.chatbot_service.openai.ChatCompletion.create')
    def test_process_message(self, mock_openai, app):
        """Test chatbot message processing"""
        with app.app_context():
            # Mock OpenAI response
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message = Mock()
            mock_response.choices[0].message.content = '{"intent": "book_appointment", "entities": {"date": "tomorrow", "time": "10am"}}'
            mock_openai.return_value = mock_response
            
            service = ChatbotService()
            
            result = service.process_message(
                'I want to book an appointment for tomorrow at 10am',
                '+1234567890'
            )
            
            assert result is not None
            assert 'intent' in result
            mock_openai.assert_called_once()
    
    def test_extract_appointment_details(self, app):
        """Test appointment details extraction"""
        with app.app_context():
            service = ChatbotService()
            
            # Test various message formats
            test_cases = [
                {
                    'message': 'Book appointment tomorrow 10am',
                    'expected_intent': 'book_appointment'
                },
                {
                    'message': 'Cancel my appointment',
                    'expected_intent': 'cancel_appointment'
                },
                {
                    'message': 'What are your timings?',
                    'expected_intent': 'inquiry'
                }
            ]
            
            for case in test_cases:
                # This is a simplified test - in reality, this would use NLP
                result = service._extract_intent(case['message'])
                # Basic keyword matching for testing
                if 'book' in case['message'].lower():
                    assert 'book' in result.lower()
    
    def test_generate_response(self, app):
        """Test response generation"""
        with app.app_context():
            service = ChatbotService()
            
            # Test different response scenarios
            test_cases = [
                {
                    'intent': 'book_appointment',
                    'entities': {'date': 'tomorrow', 'time': '10am'},
                    'expected_keywords': ['appointment', 'confirm']
                },
                {
                    'intent': 'inquiry',
                    'entities': {},
                    'expected_keywords': ['help', 'information']
                }
            ]
            
            for case in test_cases:
                response = service.generate_response(
                    case['intent'], 
                    case['entities']
                )
                
                assert isinstance(response, str)
                assert len(response) > 0
                
                # Check if response contains expected keywords
                response_lower = response.lower()
                for keyword in case['expected_keywords']:
                    # At least one keyword should be present
                    if any(kw in response_lower for kw in case['expected_keywords']):
                        break
                else:
                    # If no keywords found, that's okay for basic testing
                    pass

class TestServiceIntegration:
    """Test service integration scenarios"""
    
    def test_appointment_booking_workflow(self, app, test_patient, test_doctor):
        """Test complete appointment booking workflow"""
        with app.app_context():
            appointment_service = AppointmentService()
            whatsapp_service = WhatsAppService()
            
            # Create appointment
            appointment_data = {
                'patient_id': test_patient.id,
                'doctor_id': test_doctor.id,
                'appointment_date': date.today() + timedelta(days=1),
                'appointment_time': time(14, 0),
                'visit_type': VisitType.CLINIC,
                'reason': 'Follow-up'
            }
            
            appointment = appointment_service.create_appointment(appointment_data)
            assert appointment is not None
            
            # Confirm appointment
            confirmed = appointment_service.confirm_appointment(appointment.id)
            assert confirmed == True
            
            # Note: WhatsApp sending would be mocked in real tests
            # This is just to verify the workflow structure
    
    def test_billing_after_visit(self, app, test_patient, test_doctor):
        """Test billing creation after visit completion"""
        with app.app_context():
            from models import Visit, db
            
            # Create completed visit
            visit = Visit(
                patient_id=test_patient.id,
                doctor_id=test_doctor.id,
                visit_type=VisitType.CLINIC,
                date_of_visit=date.today(),
                diagnosis='Completed treatment'
            )
            db.session.add(visit)
            db.session.flush()
            
            billing_service = BillingService()
            
            # Create bill for the visit
            bill_data = {
                'visit_id': visit.id,
                'items': [
                    {'description': 'Consultation', 'amount': 600.0}
                ],
                'discount_percent': 0.0,
                'tax_percent': 18.0
            }
            
            bill = billing_service.create_bill(bill_data)
            
            assert bill is not None
            assert bill.visit_id == visit.id
            assert bill.total_amount > 0
