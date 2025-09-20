# services/whatsapp_service.py - WhatsApp Integration Service

import os
from twilio.rest import Client
from datetime import datetime
from models import db, WhatsAppMessage, Patient, Appointment, Billing
import logging

logger = logging.getLogger(__name__)

class WhatsAppService:
    def __init__(self):
        self.account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        self.auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        self.from_number = os.environ.get('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')
        
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
        else:
            self.client = None
            logger.warning("Twilio credentials not configured. WhatsApp service disabled.")
    
    def send_message(self, to_number, message_text, message_type='general', patient_id=None):
        """Send WhatsApp message and log it"""
        if not self.client:
            logger.error("WhatsApp service not configured")
            return False
        
        try:
            # Format phone number for WhatsApp
            if not to_number.startswith('whatsapp:'):
                to_number = f"whatsapp:{to_number}"
            
            # Send message via Twilio
            message = self.client.messages.create(
                to=to_number,
                from_=self.from_number,
                body=message_text
            )
            
            # Log message in database
            whatsapp_msg = WhatsAppMessage(
                patient_id=patient_id,
                phone_number=to_number.replace('whatsapp:', ''),
                message_type=message_type,
                message_text=message_text,
                status='sent',
                twilio_sid=message.sid,
                sent_at=datetime.utcnow()
            )
            db.session.add(whatsapp_msg)
            db.session.commit()
            
            logger.info(f"WhatsApp message sent successfully. SID: {message.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send WhatsApp message: {str(e)}")
            
            # Log failed message
            whatsapp_msg = WhatsAppMessage(
                patient_id=patient_id,
                phone_number=to_number.replace('whatsapp:', '') if 'whatsapp:' in to_number else to_number,
                message_type=message_type,
                message_text=message_text,
                status='failed'
            )
            db.session.add(whatsapp_msg)
            db.session.commit()
            
            return False
    
    def send_appointment_reminder(self, appointment):
        """Send appointment reminder to patient"""
        patient = appointment.patient
        doctor = appointment.doctor
        
        message = f"""
🏥 Appointment Reminder

Hello {patient.full_name},

You have an appointment scheduled:
📅 Date: {appointment.appointment_date.strftime('%B %d, %Y')}
⏰ Time: {appointment.appointment_time.strftime('%I:%M %p')}
👨‍⚕️ Doctor: {doctor.full_name}
📍 Type: {appointment.visit_type.value.title()}

Please arrive 15 minutes early.

For any changes, please contact us.

Thank you!
Dr. Payal's Clinic
        """.strip()
        
        phone_number = patient.whatsapp_number or patient.phone
        return self.send_message(
            phone_number, 
            message, 
            'appointment_reminder', 
            patient.id
        )
    
    def send_appointment_confirmation(self, appointment):
        """Send appointment confirmation to patient"""
        patient = appointment.patient
        doctor = appointment.doctor
        
        message = f"""
✅ Appointment Confirmed

Hello {patient.full_name},

Your appointment has been confirmed:
📅 Date: {appointment.appointment_date.strftime('%B %d, %Y')}
⏰ Time: {appointment.appointment_time.strftime('%I:%M %p')}
👨‍⚕️ Doctor: {doctor.full_name}
📍 Type: {appointment.visit_type.value.title()}

Appointment ID: {appointment.uuid}

We look forward to seeing you!

Dr. Payal's Clinic
        """.strip()
        
        phone_number = patient.whatsapp_number or patient.phone
        return self.send_message(
            phone_number, 
            message, 
            'appointment_confirmation', 
            patient.id
        )
    
    def send_bill_notification(self, billing):
        """Send bill notification to patient"""
        visit = billing.visit
        patient = visit.patient
        
        message = f"""
💰 Bill Summary

Hello {patient.full_name},

Here's your bill for the visit on {visit.date_of_visit.strftime('%B %d, %Y')}:

🏥 Service: {visit.visit_type.value.title()} Visit
💵 Amount: ₹{billing.total_amount:.2f}
📋 Bill No: {billing.bill_number}
💳 Status: {billing.payment_status.value.title()}

Thank you for choosing our services!

Dr. Payal's Clinic
        """.strip()
        
        phone_number = patient.whatsapp_number or patient.phone
        return self.send_message(
            phone_number, 
            message, 
            'bill_notification', 
            patient.id
        )
    
    def send_prescription_notification(self, prescription):
        """Send prescription notification to patient"""
        patient = prescription.patient
        doctor = prescription.doctor
        
        medications_text = ""
        for med in prescription.medications:
            medications_text += f"• {med.medication_name} - {med.dosage}\n  {med.frequency} for {med.duration}\n"
        
        message = f"""
💊 Prescription

Hello {patient.full_name},

Dr. {doctor.full_name} has prescribed:

{medications_text}

📝 Instructions: {prescription.instructions or 'Follow medication schedule as prescribed'}

⚠️ Please follow the prescription carefully.

Dr. Payal's Clinic
        """.strip()
        
        phone_number = patient.whatsapp_number or patient.phone
        return self.send_message(
            phone_number, 
            message, 
            'prescription', 
            patient.id
        )
    
    def send_package_expiry_reminder(self, patient_package):
        """Send package expiry reminder"""
        patient = patient_package.patient
        package = patient_package.package
        
        days_left = (patient_package.expiry_date - datetime.now().date()).days
        
        message = f"""
⏰ Package Expiry Reminder

Hello {patient.full_name},

Your {package.name} will expire in {days_left} days.

📦 Package: {package.name}
🔢 Sessions Remaining: {patient_package.sessions_remaining}
📅 Expiry Date: {patient_package.expiry_date.strftime('%B %d, %Y')}

Please book your remaining sessions soon!

Dr. Payal's Clinic
        """.strip()
        
        phone_number = patient.whatsapp_number or patient.phone
        return self.send_message(
            phone_number, 
            message, 
            'package_expiry', 
            patient.id
        )
    
    def send_welcome_message(self, patient):
        """Send welcome message to new patient"""
        message = f"""
🎉 Welcome to Dr. Payal's Clinic!

Hello {patient.full_name},

Thank you for choosing our physiotherapy services. We're committed to helping you achieve optimal health and wellness.

📱 You can now:
• Book appointments via WhatsApp
• Receive appointment reminders
• Get prescription updates
• Track your treatment progress

For appointments, simply reply with "BOOK APPOINTMENT" or call us directly.

We look forward to serving you!

Dr. Payal's Clinic
        """.strip()
        
        phone_number = patient.whatsapp_number or patient.phone
        return self.send_message(
            phone_number, 
            message, 
            'welcome', 
            patient.id
        )
    
    def handle_incoming_message(self, from_number, message_body):
        """Handle incoming WhatsApp messages"""
        # Remove 'whatsapp:' prefix if present
        phone_number = from_number.replace('whatsapp:', '')
        
        # Find patient by phone number
        patient = Patient.query.filter(
            (Patient.phone == phone_number) | 
            (Patient.whatsapp_number == phone_number)
        ).first()
        
        # Log incoming message
        whatsapp_msg = WhatsAppMessage(
            patient_id=patient.id if patient else None,
            phone_number=phone_number,
            message_type='incoming',
            message_text=message_body,
            status='received'
        )
        db.session.add(whatsapp_msg)
        db.session.commit()
        
        # Process message with chatbot if available
        from services.chatbot_service import ChatbotService
        chatbot_service = ChatbotService()
        
        if patient:
            response = chatbot_service.process_message(patient.id, message_body, phone_number)
        else:
            response = chatbot_service.process_message(None, message_body, phone_number)
        
        # Send response
        if response:
            self.send_message(phone_number, response, 'chatbot_response', patient.id if patient else None)
        
        return True
