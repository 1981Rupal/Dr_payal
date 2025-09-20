# services/billing_service.py - Billing and Payment Management Service

from datetime import datetime, date, timedelta
from models import (
    db, Billing, Payment, Visit, Patient, PatientPackage, TreatmentPackage,
    PaymentStatus, VisitType
)
from services.whatsapp_service import WhatsAppService
import uuid
import logging

logger = logging.getLogger(__name__)

class BillingService:
    def __init__(self):
        self.whatsapp_service = WhatsAppService()
    
    def create_bill(self, visit_id, items=None, patient_package_id=None, discount_amount=0, tax_rate=0):
        """Create a bill for a visit"""
        try:
            visit = Visit.query.get(visit_id)
            if not visit:
                return None, "Visit not found."
            
            # Check if bill already exists
            existing_bill = Billing.query.filter_by(visit_id=visit_id).first()
            if existing_bill:
                return existing_bill, "Bill already exists for this visit."
            
            # Calculate bill amount
            subtotal = 0
            
            if patient_package_id:
                # Using package session
                patient_package = PatientPackage.query.get(patient_package_id)
                if not patient_package or patient_package.sessions_remaining <= 0:
                    return None, "Invalid package or no sessions remaining."
                
                subtotal = patient_package.package.price_per_session
                
                # Deduct session from package
                patient_package.sessions_remaining -= 1
                if patient_package.sessions_remaining <= 0:
                    patient_package.is_active = False
            
            else:
                # Regular billing based on visit type
                if visit.visit_type == VisitType.CLINIC:
                    subtotal = 500.0  # Default clinic visit price
                elif visit.visit_type == VisitType.HOME:
                    subtotal = 800.0  # Default home visit price
                elif visit.visit_type == VisitType.ONLINE:
                    subtotal = 400.0  # Default online consultation price
                else:
                    subtotal = 500.0  # Default price
            
            # Apply additional items if provided
            if items:
                for item in items:
                    subtotal += item.get('amount', 0)
            
            # Calculate tax and total
            tax_amount = subtotal * (tax_rate / 100)
            total_amount = subtotal - discount_amount + tax_amount
            
            # Generate bill number
            bill_number = self.generate_bill_number()
            
            # Create billing record
            billing = Billing(
                visit_id=visit_id,
                patient_package_id=patient_package_id,
                bill_number=bill_number,
                subtotal=subtotal,
                discount_amount=discount_amount,
                tax_amount=tax_amount,
                total_amount=total_amount,
                payment_status=PaymentStatus.PENDING
            )
            
            db.session.add(billing)
            db.session.commit()
            
            # Send bill notification
            self.whatsapp_service.send_bill_notification(billing)
            
            logger.info(f"Bill created: {billing.id} for visit {visit_id}")
            return billing, "Bill created successfully."
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating bill: {str(e)}")
            return None, f"Error creating bill: {str(e)}"
    
    def process_payment(self, billing_id, amount, payment_method, transaction_id=None, notes=None):
        """Process a payment for a bill"""
        try:
            billing = Billing.query.get(billing_id)
            if not billing:
                return None, "Bill not found."
            
            # Calculate total paid amount
            total_paid = sum(payment.amount for payment in billing.payments)
            remaining_amount = billing.total_amount - total_paid
            
            if amount > remaining_amount:
                return None, f"Payment amount exceeds remaining balance of ₹{remaining_amount:.2f}"
            
            # Create payment record
            payment = Payment(
                billing_id=billing_id,
                patient_id=billing.visit.patient_id,
                amount=amount,
                payment_method=payment_method,
                transaction_id=transaction_id,
                notes=notes
            )
            
            db.session.add(payment)
            
            # Update billing status
            new_total_paid = total_paid + amount
            if new_total_paid >= billing.total_amount:
                billing.payment_status = PaymentStatus.PAID
            elif new_total_paid > 0:
                billing.payment_status = PaymentStatus.PARTIAL
            
            db.session.commit()
            
            logger.info(f"Payment processed: ₹{amount} for bill {billing_id}")
            return payment, "Payment processed successfully."
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error processing payment: {str(e)}")
            return None, f"Error processing payment: {str(e)}"
    
    def generate_bill_number(self):
        """Generate unique bill number"""
        today = date.today()
        prefix = f"BILL{today.strftime('%Y%m%d')}"
        
        # Find the last bill number for today
        last_bill = Billing.query.filter(
            Billing.bill_number.like(f"{prefix}%")
        ).order_by(Billing.bill_number.desc()).first()
        
        if last_bill:
            # Extract sequence number and increment
            last_sequence = int(last_bill.bill_number[-4:])
            new_sequence = last_sequence + 1
        else:
            new_sequence = 1
        
        return f"{prefix}{new_sequence:04d}"
    
    def create_patient_package(self, patient_id, package_id, start_date=None):
        """Create a patient package subscription"""
        try:
            package = TreatmentPackage.query.get(package_id)
            if not package or not package.is_active:
                return None, "Package not found or inactive."
            
            patient = Patient.query.get(patient_id)
            if not patient:
                return None, "Patient not found."
            
            if not start_date:
                start_date = date.today()
            
            expiry_date = start_date + timedelta(days=package.validity_days)
            
            # Create patient package
            patient_package = PatientPackage(
                patient_id=patient_id,
                package_id=package_id,
                sessions_remaining=package.total_sessions,
                start_date=start_date,
                expiry_date=expiry_date
            )
            
            db.session.add(patient_package)
            db.session.commit()
            
            logger.info(f"Patient package created: {patient_package.id}")
            return patient_package, "Package subscription created successfully."
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating patient package: {str(e)}")
            return None, f"Error creating patient package: {str(e)}"
    
    def get_patient_outstanding_balance(self, patient_id):
        """Get total outstanding balance for a patient"""
        outstanding_bills = db.session.query(
            db.func.sum(Billing.total_amount - db.func.coalesce(
                db.session.query(db.func.sum(Payment.amount))
                .filter(Payment.billing_id == Billing.id)
                .scalar_subquery(), 0
            ))
        ).join(Visit).filter(
            Visit.patient_id == patient_id,
            Billing.payment_status.in_([PaymentStatus.PENDING, PaymentStatus.PARTIAL])
        ).scalar()
        
        return outstanding_bills or 0
    
    def get_revenue_statistics(self, start_date=None, end_date=None):
        """Get revenue statistics for a date range"""
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()
        
        # Total revenue
        total_revenue = db.session.query(db.func.sum(Payment.amount)).filter(
            Payment.payment_date >= start_date,
            Payment.payment_date <= end_date
        ).scalar() or 0
        
        # Revenue by payment method
        revenue_by_method = db.session.query(
            Payment.payment_method,
            db.func.sum(Payment.amount)
        ).filter(
            Payment.payment_date >= start_date,
            Payment.payment_date <= end_date
        ).group_by(Payment.payment_method).all()
        
        # Outstanding amount
        outstanding_amount = db.session.query(
            db.func.sum(Billing.total_amount - db.func.coalesce(
                db.session.query(db.func.sum(Payment.amount))
                .filter(Payment.billing_id == Billing.id)
                .scalar_subquery(), 0
            ))
        ).filter(
            Billing.payment_status.in_([PaymentStatus.PENDING, PaymentStatus.PARTIAL])
        ).scalar() or 0
        
        # Revenue by visit type
        revenue_by_visit_type = db.session.query(
            Visit.visit_type,
            db.func.sum(Payment.amount)
        ).join(Billing).join(Payment).filter(
            Payment.payment_date >= start_date,
            Payment.payment_date <= end_date
        ).group_by(Visit.visit_type).all()
        
        return {
            'total_revenue': total_revenue,
            'revenue_by_method': dict(revenue_by_method),
            'outstanding_amount': outstanding_amount,
            'revenue_by_visit_type': {vt.value: amount for vt, amount in revenue_by_visit_type}
        }
    
    def get_package_usage_statistics(self):
        """Get package usage statistics"""
        # Active packages
        active_packages = PatientPackage.query.filter_by(is_active=True).count()
        
        # Expired packages
        expired_packages = PatientPackage.query.filter(
            PatientPackage.expiry_date < date.today()
        ).count()
        
        # Packages expiring soon (within 7 days)
        expiring_soon = PatientPackage.query.filter(
            PatientPackage.is_active == True,
            PatientPackage.expiry_date <= date.today() + timedelta(days=7),
            PatientPackage.expiry_date >= date.today()
        ).count()
        
        # Package utilization
        package_stats = db.session.query(
            TreatmentPackage.name,
            db.func.count(PatientPackage.id).label('total_sold'),
            db.func.sum(TreatmentPackage.total_price).label('total_revenue')
        ).join(PatientPackage).group_by(TreatmentPackage.id, TreatmentPackage.name).all()
        
        return {
            'active_packages': active_packages,
            'expired_packages': expired_packages,
            'expiring_soon': expiring_soon,
            'package_stats': [
                {
                    'name': stat.name,
                    'total_sold': stat.total_sold,
                    'total_revenue': stat.total_revenue
                }
                for stat in package_stats
            ]
        }
    
    def send_payment_reminders(self):
        """Send payment reminders for overdue bills"""
        try:
            # Get overdue bills (older than 7 days)
            overdue_date = date.today() - timedelta(days=7)
            
            overdue_bills = db.session.query(Billing).join(Visit).filter(
                Visit.date_of_visit <= overdue_date,
                Billing.payment_status.in_([PaymentStatus.PENDING, PaymentStatus.PARTIAL])
            ).all()
            
            sent_count = 0
            for billing in overdue_bills:
                # Calculate outstanding amount
                total_paid = sum(payment.amount for payment in billing.payments)
                outstanding = billing.total_amount - total_paid
                
                if outstanding > 0:
                    patient = billing.visit.patient
                    message = f"""
💰 Payment Reminder

Hello {patient.full_name},

You have an outstanding payment:

🧾 Bill No: {billing.bill_number}
📅 Visit Date: {billing.visit.date_of_visit.strftime('%B %d, %Y')}
💵 Outstanding Amount: ₹{outstanding:.2f}

Please make the payment at your earliest convenience.

Thank you!
Dr. Payal's Clinic
                    """.strip()
                    
                    phone_number = patient.whatsapp_number or patient.phone
                    if self.whatsapp_service.send_message(
                        phone_number, message, 'payment_reminder', patient.id
                    ):
                        sent_count += 1
            
            logger.info(f"Sent {sent_count} payment reminders")
            return sent_count
            
        except Exception as e:
            logger.error(f"Error sending payment reminders: {str(e)}")
            return 0
    
    def check_package_expiry(self):
        """Check for packages expiring soon and send notifications"""
        try:
            # Get packages expiring in 7 days
            expiry_date = date.today() + timedelta(days=7)
            
            expiring_packages = PatientPackage.query.filter(
                PatientPackage.is_active == True,
                PatientPackage.expiry_date <= expiry_date,
                PatientPackage.expiry_date >= date.today()
            ).all()
            
            sent_count = 0
            for patient_package in expiring_packages:
                if self.whatsapp_service.send_package_expiry_reminder(patient_package):
                    sent_count += 1
            
            logger.info(f"Sent {sent_count} package expiry reminders")
            return sent_count
            
        except Exception as e:
            logger.error(f"Error checking package expiry: {str(e)}")
            return 0
