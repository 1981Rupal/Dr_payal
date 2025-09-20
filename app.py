# app.py

# Imports
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from datetime import date
from sqlalchemy import func, extract
from twilio.rest import Client
import os
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_super_secret_key_here'

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://clinic_user:clinic_password@localhost/drpayal_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User model for authentication
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
# User loader callback for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Database Models
class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    visits = db.relationship('Visit', backref='patient', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Patient {self.name}>'

class Visit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    visit_type = db.Column(db.String(50), nullable=False)
    date_of_visit = db.Column(db.Date, nullable=False)
    days_left = db.Column(db.Integer, nullable=True)
    remarks = db.Column(db.Text)
    billing = db.relationship('Billing', backref='visit', uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Visit {self.id} for Patient {self.patient_id}>'

class Billing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    visit_id = db.Column(db.Integer, db.ForeignKey('visit.id'), nullable=False)
    package = db.Column(db.String(100))
    bill_amount = db.Column(db.Float)
    payment_status = db.Column(db.String(50))
    mode_of_payment = db.Column(db.String(50))
    
    def __repr__(self):
        return f'<Billing {self.id}>'

# Helper function to create tables (uncomment once to use)
def create_tables():
    with app.app_context():
        db.create_all()
        # Add a default user for testing
        if not User.query.filter_by(username='admin').first():
            user = User(username='admin')
            user.set_password('1234')
            db.session.add(user)
            db.session.commit()
            print("Default admin user created with username 'admin' and password '1234'")
        print("Database tables created!")

# Routes
@app.route('/')
def home():
    query = request.args.get('query')
    
    if query:
        search = "%{}%".format(query)
        patients = db.session.query(Patient).filter(
            or_(
                Patient.name.ilike(search),
                Patient.phone_number.ilike(search)
            )
        ).all()
    else:
        patients = db.session.query(Patient).all()
        
    return render_template('index.html', patients=patients)

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html')

# Logout route
@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/add_patient', methods=['POST'])
def add_patient():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        phone_number = request.form['phone_number']
        address = request.form['address']
        new_patient = Patient(name=name, age=age, phone_number=phone_number, address=address)
        db.session.add(new_patient)
        db.session.commit()
        flash('Patient added successfully!')
        return redirect(url_for('home'))

@app.route('/add_visit/<int:patient_id>', methods=['POST'])
def add_visit(patient_id):
    if request.method == 'POST':
        visit_type = request.form['visit_type']
        date_of_visit = date.fromisoformat(request.form['date_of_visit'])
        days_left = request.form['days_left']
        remarks = request.form['remarks']
        package = request.form['package']
        bill_amount = request.form['bill_amount']
        payment_status = request.form['payment_status']
        mode_of_payment = request.form['mode_of_payment']
        new_visit = Visit(
            patient_id=patient_id, visit_type=visit_type, date_of_visit=date_of_visit,
            days_left=days_left, remarks=remarks
        )
        new_billing = Billing(
            package=package, bill_amount=float(bill_amount), payment_status=payment_status,
            mode_of_payment=mode_of_payment
        )
        new_visit.billing = new_billing
        db.session.add(new_visit)
        db.session.commit()
        flash('Visit added successfully!')
        return redirect(url_for('home'))

@app.route('/edit_patient/<int:id>')
def edit_patient(id):
    patient = db.session.get(Patient, id)
    if patient is None:
        return redirect(url_for('home'))
    return render_template('edit.html', patient=patient)

@app.route('/update_patient/<int:id>', methods=['POST'])
def update_patient(id):
    patient = db.session.get(Patient, id)
    if patient is None:
        return redirect(url_for('home'))
    patient.name = request.form['name']
    patient.age = request.form['age']
    patient.phone_number = request.form['phone_number']
    patient.address = request.form['address']
    db.session.commit()
    flash('Patient updated successfully!')
    return redirect(url_for('home'))

@app.route('/delete_patient/<int:id>', methods=['POST'])
def delete_patient(id):
    patient = db.session.get(Patient, id)
    if patient:
        db.session.delete(patient)
        db.session.commit()
        flash('Patient deleted successfully!')
    return redirect(url_for('home'))

@app.route('/edit_visit/<int:id>')
def edit_visit(id):
    visit = db.session.get(Visit, id)
    if visit is None:
        return redirect(url_for('home'))
    return render_template('edit_visit.html', visit=visit)

@app.route('/update_visit/<int:id>', methods=['POST'])
def update_visit(id):
    visit = db.session.get(Visit, id)
    if visit is None:
        return redirect(url_for('home'))

    visit.visit_type = request.form['visit_type']
    visit.date_of_visit = date.fromisoformat(request.form['date_of_visit'])
    visit.days_left = request.form['days_left']
    visit.remarks = request.form['remarks']
    
    if visit.billing:
        visit.billing.package = request.form['package']
        visit.billing.bill_amount = float(request.form['bill_amount'])
        visit.billing.payment_status = request.form['payment_status']
        visit.billing.mode_of_payment = request.form['mode_of_payment']
    else:
        new_billing = Billing(
            package=request.form['package'],
            bill_amount=float(request.form['bill_amount']),
            payment_status=request.form['payment_status'],
            mode_of_payment=request.form['mode_of_payment']
        )
        visit.billing = new_billing

    db.session.commit()
    flash('Visit updated successfully!')
    return redirect(url_for('home'))

@app.route('/delete_visit/<int:id>', methods=['POST'])
def delete_visit(id):
    visit = db.session.get(Visit, id)
    if visit:
        db.session.delete(visit)
        db.session.commit()
        flash('Visit deleted successfully!')
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Patient Counts by Day, Week, and Month
    daily_visits_rows = db.session.query(
        Visit.date_of_visit,
        func.count(Visit.id)
    ).group_by(Visit.date_of_visit).order_by(Visit.date_of_visit).all()
    
    weekly_visits_rows = db.session.query(
        extract('year', Visit.date_of_visit),
        extract('week', Visit.date_of_visit),
        func.count(Visit.id)
    ).group_by(
        extract('year', Visit.date_of_visit),
        extract('week', Visit.date_of_visit)
    ).order_by(
        extract('year', Visit.date_of_visit),
        extract('week', Visit.date_of_visit)
    ).all()
    
    monthly_visits_rows = db.session.query(
        extract('year', Visit.date_of_visit),
        extract('month', Visit.date_of_visit),
        func.count(Visit.id)
    ).group_by(
        extract('year', Visit.date_of_visit),
        extract('month', Visit.date_of_visit)
    ).order_by(
        extract('year', Visit.date_of_visit),
        extract('month', Visit.date_of_visit)
    ).all()
    
    # Financial Data (Total Earnings) by Day, Week, and Month
    daily_earnings_rows = db.session.query(
        Visit.date_of_visit,
        func.sum(Billing.bill_amount)
    ).join(Billing).group_by(Visit.date_of_visit).order_by(Visit.date_of_visit).all()

    weekly_earnings_rows = db.session.query(
        extract('year', Visit.date_of_visit),
        extract('week', Visit.date_of_visit),
        func.sum(Billing.bill_amount)
    ).join(Billing).group_by(
        extract('year', Visit.date_of_visit),
        extract('week', Visit.date_of_visit)
    ).order_by(
        extract('year', Visit.date_of_visit),
        extract('week', Visit.date_of_visit)
    ).all()

    monthly_earnings_rows = db.session.query(
        extract('year', Visit.date_of_visit),
        extract('month', Visit.date_of_visit),
        func.sum(Billing.bill_amount)
    ).join(Billing).group_by(
        extract('year', Visit.date_of_visit),
        extract('month', Visit.date_of_visit)
    ).order_by(
        extract('year', Visit.date_of_visit),
        extract('month', Visit.date_of_visit)
    ).all()

    # NEW: Convert SQLAlchemy Row objects to serializable lists
    daily_visits = [list(row) for row in daily_visits_rows]
    weekly_visits = [list(row) for row in weekly_visits_rows]
    monthly_visits = [list(row) for row in monthly_visits_rows]
    daily_earnings = [list(row) for row in daily_earnings_rows]
    weekly_earnings = [list(row) for row in weekly_earnings_rows]
    monthly_earnings = [list(row) for row in monthly_earnings_rows]

    return render_template(
        'dashboard.html',
        daily_visits=daily_visits,
        weekly_visits=weekly_visits,
        monthly_visits=monthly_visits,
        daily_earnings=daily_earnings,
        weekly_earnings=weekly_earnings,
        monthly_earnings=monthly_earnings
    )

@app.route('/send_bill/<int:visit_id>')
def send_bill(visit_id):
    visit = db.session.get(Visit, visit_id)
    if visit and visit.patient and visit.billing:
        account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
        client = Client(account_sid, auth_token)

        to_number = f"whatsapp:{visit.patient.phone_number}"
        from_number = "whatsapp:+14155238886"

        bill_message = (
            f"Hello {visit.patient.name},\n"
            f"Here is your billing summary for your visit on {visit.date_of_visit}:\n"
            f"- Service: {visit.visit_type}\n"
            f"- Package: {visit.billing.package}\n"
            f"- Bill Amount: ₹{visit.billing.bill_amount}\n"
            f"- Payment Status: {visit.billing.payment_status}\n"
            f"Thank you for your visit!"
        )

        try:
            message = client.messages.create(
                to=to_number,
                from_=from_number,
                body=bill_message
            )
            flash(f'Message sent successfully! SID: {message.sid}')
        except Exception as e:
            flash(f'Error sending message: {e}', 'danger')

    return redirect(url_for('home'))

if __name__ == '__main__':
    # REMINDER: This line should be commented out after the first run.
    # create_tables()
    app.run(debug=True)