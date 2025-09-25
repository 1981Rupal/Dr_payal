# routes/billing.py - Billing and payment management routes

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date
from models import (
    db, Billing, Payment, Visit, Patient, TreatmentPackage, PatientPackage,
    PaymentStatus, UserRole
)

billing_bp = Blueprint('billing', __name__)

@billing_bp.route('/')
@login_required
def list_bills():
    """List all bills with filtering"""
    if not current_user.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.STAFF]:
        flash('You do not have permission to access billing.', 'error')
        return redirect(url_for('main.dashboard'))
    
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    patient_filter = request.args.get('patient', '')
    per_page = 20
    
    query = Billing.query.join(Visit).join(Patient)
    
    # Apply filters
    if status_filter:
        query = query.filter(Billing.payment_status == PaymentStatus(status_filter))
    
    if patient_filter:
        search_term = f"%{patient_filter}%"
        query = query.filter(
            db.or_(
                Patient.first_name.ilike(search_term),
                Patient.last_name.ilike(search_term),
                Patient.phone.ilike(search_term)
            )
        )
    
    bills = query.order_by(Billing.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('billing/list.html', 
                         bills=bills,
                         status_filter=status_filter,
                         patient_filter=patient_filter)

@billing_bp.route('/<int:id>')
@login_required
def view_bill(id):
    """View bill details"""
    if not current_user.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.STAFF]:
        flash('You do not have permission to access billing.', 'error')
        return redirect(url_for('main.dashboard'))
    
    bill = Billing.query.get_or_404(id)
    payments = Payment.query.filter_by(billing_id=id).order_by(Payment.payment_date.desc()).all()
    
    return render_template('billing/view.html', bill=bill, payments=payments)

@billing_bp.route('/create/<int:visit_id>', methods=['GET', 'POST'])
@login_required
def create_bill(visit_id):
    """Create bill for a visit"""
    if not current_user.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.STAFF]:
        flash('You do not have permission to create bills.', 'error')
        return redirect(url_for('main.dashboard'))
    
    visit = Visit.query.get_or_404(visit_id)
    
    # Check if bill already exists
    if visit.billing:
        flash('Bill already exists for this visit.', 'error')
        return redirect(url_for('billing.view_bill', id=visit.billing.id))
    
    if request.method == 'POST':
        try:
            # Get form data
            subtotal = float(request.form.get('subtotal', 0))
            discount_amount = float(request.form.get('discount_amount', 0))
            tax_amount = float(request.form.get('tax_amount', 0))
            package_id = request.form.get('package_id', type=int)
            
            # Calculate total
            total_amount = subtotal - discount_amount + tax_amount
            
            if total_amount < 0:
                flash('Total amount cannot be negative.', 'error')
                return render_template('billing/create.html', visit=visit)
            
            # Generate bill number
            bill_count = Billing.query.count()
            bill_number = f"BILL{bill_count + 1:06d}"
            
            # Create billing record
            new_bill = Billing(
                visit_id=visit_id,
                patient_package_id=package_id if package_id else None,
                bill_number=bill_number,
                subtotal=subtotal,
                discount_amount=discount_amount,
                tax_amount=tax_amount,
                total_amount=total_amount,
                payment_status=PaymentStatus.PENDING
            )
            
            db.session.add(new_bill)
            
            # If using a package, update sessions remaining
            if package_id:
                patient_package = PatientPackage.query.get(package_id)
                if patient_package and patient_package.sessions_remaining > 0:
                    patient_package.sessions_remaining -= 1
                    if patient_package.sessions_remaining == 0:
                        patient_package.is_active = False
            
            db.session.commit()
            
            flash('Bill created successfully!', 'success')
            return redirect(url_for('billing.view_bill', id=new_bill.id))
            
        except ValueError:
            flash('Invalid amount values.', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating bill: {str(e)}', 'error')
    
    # Get available packages for the patient
    patient_packages = PatientPackage.query.filter_by(
        patient_id=visit.patient_id,
        is_active=True
    ).filter(PatientPackage.sessions_remaining > 0).all()
    
    return render_template('billing/create.html', visit=visit, patient_packages=patient_packages)

@billing_bp.route('/<int:id>/add-payment', methods=['GET', 'POST'])
@login_required
def add_payment(id):
    """Add payment to a bill"""
    if not current_user.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.STAFF]:
        flash('You do not have permission to add payments.', 'error')
        return redirect(url_for('main.dashboard'))
    
    bill = Billing.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Get form data
            amount = float(request.form.get('amount', 0))
            payment_method = request.form.get('payment_method')
            transaction_id = request.form.get('transaction_id', '').strip()
            notes = request.form.get('notes', '').strip()
            
            # Validation
            if amount <= 0:
                flash('Payment amount must be greater than zero.', 'error')
                return render_template('billing/add_payment.html', bill=bill)
            
            # Calculate total paid so far
            total_paid = db.session.query(db.func.sum(Payment.amount)).filter_by(
                billing_id=id
            ).scalar() or 0
            
            if total_paid + amount > bill.total_amount:
                flash('Payment amount exceeds remaining balance.', 'error')
                return render_template('billing/add_payment.html', bill=bill)
            
            # Create payment record
            new_payment = Payment(
                billing_id=id,
                patient_id=bill.visit.patient_id,
                amount=amount,
                payment_method=payment_method,
                transaction_id=transaction_id,
                notes=notes,
                payment_date=datetime.utcnow()
            )
            
            db.session.add(new_payment)
            
            # Update bill payment status
            new_total_paid = total_paid + amount
            if new_total_paid >= bill.total_amount:
                bill.payment_status = PaymentStatus.PAID
            else:
                bill.payment_status = PaymentStatus.PARTIAL
            
            bill.updated_at = datetime.utcnow()
            db.session.commit()
            
            flash(f'Payment of ₹{amount} added successfully!', 'success')
            return redirect(url_for('billing.view_bill', id=id))
            
        except ValueError:
            flash('Invalid payment amount.', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding payment: {str(e)}', 'error')
    
    # Calculate remaining balance
    total_paid = db.session.query(db.func.sum(Payment.amount)).filter_by(
        billing_id=id
    ).scalar() or 0
    remaining_balance = bill.total_amount - total_paid
    
    return render_template('billing/add_payment.html', bill=bill, remaining_balance=remaining_balance)

@billing_bp.route('/packages')
@login_required
def list_packages():
    """List treatment packages"""
    if not current_user.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.STAFF]:
        flash('You do not have permission to access packages.', 'error')
        return redirect(url_for('main.dashboard'))
    
    packages = TreatmentPackage.query.filter_by(is_active=True).all()
    return render_template('billing/packages.html', packages=packages)

@billing_bp.route('/packages/add', methods=['GET', 'POST'])
@login_required
def add_package():
    """Add new treatment package"""
    if not current_user.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
        flash('You do not have permission to add packages.', 'error')
        return redirect(url_for('billing.list_packages'))
    
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            total_sessions = int(request.form.get('total_sessions', 0))
            price_per_session = float(request.form.get('price_per_session', 0))
            total_price = float(request.form.get('total_price', 0))
            validity_days = int(request.form.get('validity_days', 90))
            
            # Validation
            if not name or total_sessions <= 0 or price_per_session <= 0 or total_price <= 0:
                flash('Please fill in all required fields with valid values.', 'error')
                return render_template('billing/add_package.html')
            
            # Create new package
            new_package = TreatmentPackage(
                name=name,
                description=description,
                total_sessions=total_sessions,
                price_per_session=price_per_session,
                total_price=total_price,
                validity_days=validity_days
            )
            
            db.session.add(new_package)
            db.session.commit()
            
            flash(f'Package "{name}" created successfully!', 'success')
            return redirect(url_for('billing.list_packages'))
            
        except ValueError:
            flash('Invalid numeric values.', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating package: {str(e)}', 'error')
    
    return render_template('billing/add_package.html')

@billing_bp.route('/assign-package/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def assign_package(patient_id):
    """Assign package to patient"""
    if not current_user.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.STAFF]:
        flash('You do not have permission to assign packages.', 'error')
        return redirect(url_for('main.dashboard'))
    
    patient = Patient.query.get_or_404(patient_id)
    
    if request.method == 'POST':
        try:
            package_id = int(request.form.get('package_id'))
            start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
            
            package = TreatmentPackage.query.get_or_404(package_id)
            
            # Calculate expiry date
            from datetime import timedelta
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
            
            flash(f'Package "{package.name}" assigned to {patient.full_name}!', 'success')
            return redirect(url_for('patients.view_patient', id=patient_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error assigning package: {str(e)}', 'error')
    
    packages = TreatmentPackage.query.filter_by(is_active=True).all()
    return render_template('billing/assign_package.html', patient=patient, packages=packages)

@billing_bp.route('/reports')
@login_required
def billing_reports():
    """Billing reports and analytics"""
    if not current_user.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
        flash('You do not have permission to access billing reports.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Get date range from query parameters
    start_date = request.args.get('start_date', (date.today() - timedelta(days=30)).isoformat())
    end_date = request.args.get('end_date', date.today().isoformat())
    
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Generate billing reports
        reports = {
            'total_revenue': db.session.query(db.func.sum(Payment.amount)).filter(
                Payment.payment_date.between(start, end)
            ).scalar() or 0,
            'pending_amount': db.session.query(db.func.sum(Billing.total_amount)).join(Visit).filter(
                Visit.date_of_visit.between(start, end),
                Billing.payment_status == PaymentStatus.PENDING
            ).scalar() or 0,
            'total_bills': Billing.query.join(Visit).filter(
                Visit.date_of_visit.between(start, end)
            ).count(),
            'paid_bills': Billing.query.join(Visit).filter(
                Visit.date_of_visit.between(start, end),
                Billing.payment_status == PaymentStatus.PAID
            ).count()
        }
        
        # Payment method breakdown
        payment_methods = db.session.query(
            Payment.payment_method,
            db.func.sum(Payment.amount),
            db.func.count(Payment.id)
        ).filter(
            Payment.payment_date.between(start, end)
        ).group_by(Payment.payment_method).all()
        
        reports['payment_methods'] = [
            {'method': method, 'amount': amount, 'count': count}
            for method, amount, count in payment_methods
        ]
        
    except Exception as e:
        flash(f'Error generating reports: {str(e)}', 'error')
        reports = {}
    
    return render_template('billing/reports.html',
                         reports=reports,
                         start_date=start_date,
                         end_date=end_date)

@billing_bp.route('/packages/<int:package_id>/edit')
@login_required
def edit_package(package_id):
    """Edit treatment package"""
    if not current_user.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
        flash('You do not have permission to edit packages.', 'error')
        return redirect(url_for('main.dashboard'))
    package = TreatmentPackage.query.get_or_404(package_id)
    return render_template('billing/edit_package.html', package=package)
