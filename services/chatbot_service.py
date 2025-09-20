# services/chatbot_service.py - AI Chatbot Service

import os
import openai
import json
import re
from datetime import datetime, date, timedelta
from models import (
    db, Patient, Appointment, User, TreatmentPackage, 
    ChatbotConversation, ChatbotMessage, AppointmentStatus, 
    VisitType, UserRole
)
import logging

logger = logging.getLogger(__name__)

class ChatbotService:
    def __init__(self):
        self.openai_api_key = os.environ.get('OPENAI_API_KEY')
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        else:
            logger.warning("OpenAI API key not configured. Chatbot service disabled.")
    
    def process_message(self, patient_id, message_text, phone_number):
        """Process incoming message and generate response"""
        if not self.openai_api_key:
            return "I'm sorry, the chatbot service is currently unavailable. Please contact our staff directly."
        
        try:
            # Get or create conversation
            conversation = self.get_or_create_conversation(patient_id, phone_number)
            
            # Log user message
            user_message = ChatbotMessage(
                conversation_id=conversation.id,
                message_type='user',
                message_text=message_text
            )
            db.session.add(user_message)
            
            # Analyze intent and extract entities
            intent, entities = self.analyze_message(message_text)
            user_message.intent = intent
            user_message.entities = json.dumps(entities)
            
            # Generate response based on intent
            response = self.generate_response(conversation, intent, entities, message_text)
            
            # Log bot response
            bot_message = ChatbotMessage(
                conversation_id=conversation.id,
                message_type='bot',
                message_text=response,
                intent=intent
            )
            db.session.add(bot_message)
            db.session.commit()
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing chatbot message: {str(e)}")
            return "I'm sorry, I encountered an error. Please try again or contact our staff directly."
    
    def get_or_create_conversation(self, patient_id, phone_number):
        """Get existing conversation or create new one"""
        # Try to find active conversation
        conversation = ChatbotConversation.query.filter_by(
            phone_number=phone_number,
            is_active=True
        ).first()
        
        if not conversation:
            # Create new conversation
            session_id = f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{phone_number[-4:]}"
            conversation = ChatbotConversation(
                patient_id=patient_id,
                phone_number=phone_number,
                session_id=session_id
            )
            db.session.add(conversation)
            db.session.commit()
        
        return conversation
    
    def analyze_message(self, message_text):
        """Analyze message to extract intent and entities"""
        message_lower = message_text.lower()
        
        # Define intent patterns
        intent_patterns = {
            'book_appointment': [
                'book appointment', 'schedule appointment', 'make appointment',
                'book', 'appointment', 'schedule', 'visit'
            ],
            'check_appointment': [
                'check appointment', 'my appointment', 'appointment status',
                'when is my appointment'
            ],
            'cancel_appointment': [
                'cancel appointment', 'cancel my appointment', 'reschedule'
            ],
            'package_inquiry': [
                'package', 'packages', 'treatment package', 'pricing',
                'cost', 'price', 'how much'
            ],
            'clinic_info': [
                'address', 'location', 'timing', 'hours', 'contact',
                'phone number', 'where are you'
            ],
            'greeting': [
                'hello', 'hi', 'hey', 'good morning', 'good afternoon',
                'good evening', 'namaste'
            ],
            'help': [
                'help', 'what can you do', 'options', 'menu'
            ]
        }
        
        # Extract entities
        entities = {}
        
        # Extract dates
        date_patterns = [
            r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b',
            r'\b(today|tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
            r'\b(\d{1,2})(st|nd|rd|th)?\s+(january|february|march|april|may|june|july|august|september|october|november|december)\b'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, message_lower)
            if matches:
                entities['date'] = matches[0]
                break
        
        # Extract times
        time_pattern = r'\b(\d{1,2}):?(\d{2})?\s*(am|pm|morning|afternoon|evening)?\b'
        time_matches = re.findall(time_pattern, message_lower)
        if time_matches:
            entities['time'] = time_matches[0]
        
        # Extract visit type
        if any(word in message_lower for word in ['home', 'home visit']):
            entities['visit_type'] = 'home'
        elif any(word in message_lower for word in ['online', 'video', 'virtual']):
            entities['visit_type'] = 'online'
        else:
            entities['visit_type'] = 'clinic'
        
        # Determine intent
        intent = 'unknown'
        for intent_name, keywords in intent_patterns.items():
            if any(keyword in message_lower for keyword in keywords):
                intent = intent_name
                break
        
        return intent, entities
    
    def generate_response(self, conversation, intent, entities, message_text):
        """Generate appropriate response based on intent"""
        patient = conversation.patient if conversation.patient_id else None
        
        if intent == 'greeting':
            if patient:
                return f"Hello {patient.full_name}! How can I help you today? You can:\n\n• Book an appointment\n• Check your appointments\n• Ask about treatment packages\n• Get clinic information"
            else:
                return "Hello! Welcome to Dr. Payal's Physiotherapy Clinic. How can I help you today?\n\n• Book an appointment\n• Get clinic information\n• Ask about treatment packages"
        
        elif intent == 'book_appointment':
            return self.handle_appointment_booking(conversation, entities)
        
        elif intent == 'check_appointment':
            return self.handle_appointment_check(conversation)
        
        elif intent == 'cancel_appointment':
            return self.handle_appointment_cancellation(conversation)
        
        elif intent == 'package_inquiry':
            return self.handle_package_inquiry()
        
        elif intent == 'clinic_info':
            return self.handle_clinic_info()
        
        elif intent == 'help':
            return self.handle_help_request()
        
        else:
            # Use OpenAI for complex queries
            return self.generate_ai_response(conversation, message_text)
    
    def handle_appointment_booking(self, conversation, entities):
        """Handle appointment booking request"""
        patient = conversation.patient
        
        if not patient:
            return "To book an appointment, I'll need your details first. Please provide your name and phone number, or contact our staff directly at [clinic_phone]."
        
        # Check if patient has pending appointments
        pending_appointments = Appointment.query.filter_by(
            patient_id=patient.id,
            status=AppointmentStatus.PENDING
        ).count()
        
        if pending_appointments > 0:
            return f"You already have {pending_appointments} pending appointment(s). Please wait for confirmation or contact our staff to modify existing appointments."
        
        # Get available doctors
        doctors = User.query.filter_by(role=UserRole.DOCTOR, is_active=True).all()
        if not doctors:
            return "I'm sorry, no doctors are currently available. Please contact our staff directly."
        
        # Create appointment request
        visit_type = VisitType.CLINIC
        if entities.get('visit_type') == 'home':
            visit_type = VisitType.HOME
        elif entities.get('visit_type') == 'online':
            visit_type = VisitType.ONLINE
        
        # For now, create a pending appointment that needs admin confirmation
        appointment_date = date.today() + timedelta(days=1)  # Default to tomorrow
        appointment_time = datetime.strptime('10:00', '%H:%M').time()  # Default time
        
        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctors[0].id,  # Assign to first available doctor
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            visit_type=visit_type,
            status=AppointmentStatus.PENDING,
            reason="Appointment requested via WhatsApp chatbot"
        )
        db.session.add(appointment)
        db.session.commit()
        
        return f"✅ Appointment request submitted!\n\nDetails:\n📅 Date: {appointment_date.strftime('%B %d, %Y')}\n⏰ Time: {appointment_time.strftime('%I:%M %p')}\n👨‍⚕️ Doctor: {doctors[0].full_name}\n📍 Type: {visit_type.value.title()}\n\n⏳ Status: Pending confirmation\n\nOur staff will confirm your appointment shortly. You'll receive a WhatsApp notification once confirmed."
    
    def handle_appointment_check(self, conversation):
        """Handle appointment status check"""
        patient = conversation.patient
        
        if not patient:
            return "To check appointments, please provide your patient details or contact our staff directly."
        
        # Get upcoming appointments
        upcoming_appointments = Appointment.query.filter(
            Appointment.patient_id == patient.id,
            Appointment.appointment_date >= date.today()
        ).order_by(Appointment.appointment_date, Appointment.appointment_time).all()
        
        if not upcoming_appointments:
            return "You don't have any upcoming appointments. Would you like to book one?"
        
        response = "📅 Your upcoming appointments:\n\n"
        for apt in upcoming_appointments:
            status_emoji = "✅" if apt.status == AppointmentStatus.CONFIRMED else "⏳"
            response += f"{status_emoji} {apt.appointment_date.strftime('%B %d, %Y')} at {apt.appointment_time.strftime('%I:%M %p')}\n"
            response += f"   👨‍⚕️ Dr. {apt.doctor.full_name}\n"
            response += f"   📍 {apt.visit_type.value.title()} Visit\n"
            response += f"   Status: {apt.status.value.title()}\n\n"
        
        return response
    
    def handle_appointment_cancellation(self, conversation):
        """Handle appointment cancellation"""
        patient = conversation.patient
        
        if not patient:
            return "To cancel appointments, please contact our staff directly with your patient details."
        
        upcoming_appointments = Appointment.query.filter(
            Appointment.patient_id == patient.id,
            Appointment.appointment_date >= date.today(),
            Appointment.status.in_([AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED])
        ).all()
        
        if not upcoming_appointments:
            return "You don't have any appointments to cancel."
        
        response = "To cancel an appointment, please contact our staff directly. Here are your upcoming appointments:\n\n"
        for apt in upcoming_appointments:
            response += f"📅 {apt.appointment_date.strftime('%B %d, %Y')} at {apt.appointment_time.strftime('%I:%M %p')}\n"
            response += f"👨‍⚕️ Dr. {apt.doctor.full_name}\n\n"
        
        return response
    
    def handle_package_inquiry(self):
        """Handle treatment package inquiry"""
        packages = TreatmentPackage.query.filter_by(is_active=True).all()
        
        if not packages:
            return "We currently don't have any active treatment packages. Please contact our staff for current pricing."
        
        response = "💰 Our Treatment Packages:\n\n"
        for pkg in packages:
            response += f"📦 {pkg.name}\n"
            response += f"   Sessions: {pkg.total_sessions}\n"
            response += f"   Price: ₹{pkg.total_price:.2f}\n"
            response += f"   Per Session: ₹{pkg.price_per_session:.2f}\n"
            response += f"   Validity: {pkg.validity_days} days\n\n"
        
        response += "For more details or to purchase a package, please contact our staff."
        return response
    
    def handle_clinic_info(self):
        """Handle clinic information request"""
        return """🏥 Dr. Payal's Physiotherapy Clinic

📍 Address: 123 Health Street, Medical City, MC 12345
📞 Phone: +1234567890
📧 Email: info@drpayal.com

🕒 Working Hours:
Monday - Saturday: 9:00 AM - 6:00 PM
Sunday: Closed

🏥 Services:
• Physiotherapy
• Home Visits
• Online Consultations
• Treatment Packages

For appointments, reply with "BOOK APPOINTMENT" or call us directly!"""
    
    def handle_help_request(self):
        """Handle help request"""
        return """🤖 How I can help you:

• 📅 Book appointments
• ✅ Check appointment status
• 💰 Get package information
• 🏥 Clinic information
• ❓ Answer general questions

Just type what you need, and I'll assist you!

For urgent matters, please call our clinic directly."""
    
    def generate_ai_response(self, conversation, message_text):
        """Generate AI response using OpenAI"""
        try:
            # Get conversation history
            recent_messages = ChatbotMessage.query.filter_by(
                conversation_id=conversation.id
            ).order_by(ChatbotMessage.created_at.desc()).limit(10).all()
            
            # Build context
            context = "You are a helpful assistant for Dr. Payal's Physiotherapy Clinic. "
            context += "You can help with appointments, clinic information, and general physiotherapy questions. "
            context += "Be friendly, professional, and concise.\n\n"
            
            # Add recent conversation
            for msg in reversed(recent_messages):
                role = "user" if msg.message_type == 'user' else "assistant"
                context += f"{role}: {msg.message_text}\n"
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": context},
                    {"role": "user", "content": message_text}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return "I'm sorry, I couldn't process your request right now. Please contact our staff directly for assistance."
