# services/appointment_service.py - Appointment Management Service

from datetime import datetime, date, time, timedelta
from models import (
    db, Appointment, Patient, User, OnlineConsultation,
    AppointmentStatus, VisitType, ConsultationStatus, UserRole
)
from services.whatsapp_service import WhatsAppService
import logging

logger = logging.getLogger(__name__)

class AppointmentService:
    def __init__(self):
        self.whatsapp_service = WhatsAppService()
    
    def create_appointment(self, patient_id, doctor_id, appointment_date, appointment_time, 
                          visit_type, reason=None, created_by_id=None):
        """Create a new appointment"""
        try:
            # Validate inputs
            if not self.is_valid_appointment_time(doctor_id, appointment_date, appointment_time):
                return None, "The selected time slot is not available."
            
            # Create appointment
            appointment = Appointment(
                patient_id=patient_id,
                doctor_id=doctor_id,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                visit_type=visit_type,
                reason=reason,
                created_by_id=created_by_id,
                status=AppointmentStatus.PENDING
            )
            
            db.session.add(appointment)
            db.session.commit()
            
            # Send confirmation message
            self.whatsapp_service.send_appointment_confirmation(appointment)
            
            logger.info(f"Appointment created: {appointment.id}")
            return appointment, "Appointment created successfully."
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating appointment: {str(e)}")
            return None, f"Error creating appointment: {str(e)}"
    
    def confirm_appointment(self, appointment_id, confirmed_by_id):
        """Confirm a pending appointment"""
        try:
            appointment = Appointment.query.get(appointment_id)
            if not appointment:
                return False, "Appointment not found."
            
            if appointment.status != AppointmentStatus.PENDING:
                return False, "Appointment is not in pending status."
            
            appointment.status = AppointmentStatus.CONFIRMED
            appointment.confirmed_at = datetime.utcnow()
            
            # Create online consultation if needed
            if appointment.visit_type == VisitType.ONLINE:
                self.create_online_consultation(appointment)
            
            db.session.commit()
            
            # Send confirmation message
            self.whatsapp_service.send_appointment_confirmation(appointment)
            
            logger.info(f"Appointment confirmed: {appointment.id}")
            return True, "Appointment confirmed successfully."
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error confirming appointment: {str(e)}")
            return False, f"Error confirming appointment: {str(e)}"
    
    def cancel_appointment(self, appointment_id, cancellation_reason, cancelled_by_id):
        """Cancel an appointment"""
        try:
            appointment = Appointment.query.get(appointment_id)
            if not appointment:
                return False, "Appointment not found."
            
            if appointment.status == AppointmentStatus.COMPLETED:
                return False, "Cannot cancel a completed appointment."
            
            appointment.status = AppointmentStatus.CANCELLED
            appointment.cancelled_at = datetime.utcnow()
            appointment.cancellation_reason = cancellation_reason
            
            # Cancel online consultation if exists
            if appointment.consultation:
                appointment.consultation.status = ConsultationStatus.CANCELLED
            
            db.session.commit()
            
            logger.info(f"Appointment cancelled: {appointment.id}")
            return True, "Appointment cancelled successfully."
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error cancelling appointment: {str(e)}")
            return False, f"Error cancelling appointment: {str(e)}"
    
    def reschedule_appointment(self, appointment_id, new_date, new_time, rescheduled_by_id):
        """Reschedule an appointment"""
        try:
            appointment = Appointment.query.get(appointment_id)
            if not appointment:
                return False, "Appointment not found."
            
            if appointment.status == AppointmentStatus.COMPLETED:
                return False, "Cannot reschedule a completed appointment."
            
            # Validate new time slot
            if not self.is_valid_appointment_time(appointment.doctor_id, new_date, new_time, appointment.id):
                return False, "The new time slot is not available."
            
            # Update appointment
            old_date = appointment.appointment_date
            old_time = appointment.appointment_time
            
            appointment.appointment_date = new_date
            appointment.appointment_time = new_time
            appointment.status = AppointmentStatus.CONFIRMED
            
            # Update online consultation if exists
            if appointment.consultation:
                appointment.consultation.status = ConsultationStatus.SCHEDULED
            
            db.session.commit()
            
            # Send notification
            self.whatsapp_service.send_appointment_confirmation(appointment)
            
            logger.info(f"Appointment rescheduled: {appointment.id} from {old_date} {old_time} to {new_date} {new_time}")
            return True, "Appointment rescheduled successfully."
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error rescheduling appointment: {str(e)}")
            return False, f"Error rescheduling appointment: {str(e)}"
    
    def is_valid_appointment_time(self, doctor_id, appointment_date, appointment_time, exclude_appointment_id=None):
        """Check if the appointment time is valid and available"""
        # Check if it's a working day and time
        if not self.is_working_time(appointment_date, appointment_time):
            return False
        
        # Check for conflicts with existing appointments
        query = Appointment.query.filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == appointment_date,
            Appointment.appointment_time == appointment_time,
            Appointment.status.in_([AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED])
        )
        
        if exclude_appointment_id:
            query = query.filter(Appointment.id != exclude_appointment_id)
        
        existing_appointment = query.first()
        return existing_appointment is None
    
    def is_working_time(self, appointment_date, appointment_time):
        """Check if the appointment is within working hours and days"""
        # Check if it's a working day (Monday to Saturday)
        if appointment_date.weekday() == 6:  # Sunday
            return False
        
        # Check working hours (9 AM to 6 PM)
        working_start = time(9, 0)
        working_end = time(18, 0)
        
        return working_start <= appointment_time <= working_end
    
    def get_available_slots(self, doctor_id, date_requested, duration_minutes=30):
        """Get available appointment slots for a doctor on a specific date"""
        if not self.is_working_time(date_requested, time(9, 0)):
            return []
        
        # Define working hours
        start_time = datetime.combine(date_requested, time(9, 0))
        end_time = datetime.combine(date_requested, time(18, 0))
        
        # Get existing appointments for the day
        existing_appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == date_requested,
            Appointment.status.in_([AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED])
        ).all()
        
        # Generate all possible slots
        available_slots = []
        current_time = start_time
        
        while current_time + timedelta(minutes=duration_minutes) <= end_time:
            slot_time = current_time.time()
            
            # Check if slot is available
            is_available = True
            for appointment in existing_appointments:
                if appointment.appointment_time == slot_time:
                    is_available = False
                    break
            
            if is_available:
                available_slots.append(slot_time)
            
            current_time += timedelta(minutes=duration_minutes)
        
        return available_slots
    
    def create_online_consultation(self, appointment):
        """Create online consultation for an appointment"""
        try:
            # Generate meeting details (in a real implementation, integrate with video service)
            meeting_id = f"meeting_{appointment.id}_{datetime.utcnow().strftime('%Y%m%d%H%M')}"
            meeting_url = f"https://meet.clinic.com/room/{meeting_id}"
            meeting_password = f"clinic{appointment.id}"
            
            consultation = OnlineConsultation(
                appointment_id=appointment.id,
                patient_id=appointment.patient_id,
                doctor_id=appointment.doctor_id,
                meeting_url=meeting_url,
                meeting_id=meeting_id,
                meeting_password=meeting_password,
                status=ConsultationStatus.SCHEDULED
            )
            
            db.session.add(consultation)
            db.session.commit()
            
            logger.info(f"Online consultation created: {consultation.id}")
            return consultation
            
        except Exception as e:
            logger.error(f"Error creating online consultation: {str(e)}")
            return None
    
    def send_appointment_reminders(self):
        """Send appointment reminders for tomorrow's appointments"""
        try:
            tomorrow = date.today() + timedelta(days=1)
            
            appointments = Appointment.query.filter(
                Appointment.appointment_date == tomorrow,
                Appointment.status == AppointmentStatus.CONFIRMED,
                Appointment.reminder_sent == False
            ).all()
            
            sent_count = 0
            for appointment in appointments:
                if self.whatsapp_service.send_appointment_reminder(appointment):
                    appointment.reminder_sent = True
                    sent_count += 1
            
            db.session.commit()
            logger.info(f"Sent {sent_count} appointment reminders")
            return sent_count
            
        except Exception as e:
            logger.error(f"Error sending appointment reminders: {str(e)}")
            return 0
    
    def get_doctor_schedule(self, doctor_id, start_date, end_date):
        """Get doctor's schedule for a date range"""
        appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date >= start_date,
            Appointment.appointment_date <= end_date,
            Appointment.status.in_([AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED])
        ).order_by(Appointment.appointment_date, Appointment.appointment_time).all()
        
        schedule = {}
        for appointment in appointments:
            date_str = appointment.appointment_date.strftime('%Y-%m-%d')
            if date_str not in schedule:
                schedule[date_str] = []
            
            schedule[date_str].append({
                'id': appointment.id,
                'time': appointment.appointment_time.strftime('%H:%M'),
                'patient': appointment.patient.full_name,
                'type': appointment.visit_type.value,
                'status': appointment.status.value,
                'reason': appointment.reason
            })
        
        return schedule
    
    def get_appointment_statistics(self, start_date=None, end_date=None):
        """Get appointment statistics"""
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()
        
        query = Appointment.query.filter(
            Appointment.appointment_date >= start_date,
            Appointment.appointment_date <= end_date
        )
        
        total_appointments = query.count()
        confirmed_appointments = query.filter(Appointment.status == AppointmentStatus.CONFIRMED).count()
        pending_appointments = query.filter(Appointment.status == AppointmentStatus.PENDING).count()
        cancelled_appointments = query.filter(Appointment.status == AppointmentStatus.CANCELLED).count()
        completed_appointments = query.filter(Appointment.status == AppointmentStatus.COMPLETED).count()
        
        # Appointments by visit type
        clinic_visits = query.filter(Appointment.visit_type == VisitType.CLINIC).count()
        home_visits = query.filter(Appointment.visit_type == VisitType.HOME).count()
        online_visits = query.filter(Appointment.visit_type == VisitType.ONLINE).count()
        
        return {
            'total': total_appointments,
            'confirmed': confirmed_appointments,
            'pending': pending_appointments,
            'cancelled': cancelled_appointments,
            'completed': completed_appointments,
            'clinic_visits': clinic_visits,
            'home_visits': home_visits,
            'online_visits': online_visits
        }
