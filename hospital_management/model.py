from . import db
from flask_login import UserMixin

from datetime import datetime, date, time
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(300), nullable=False)
    # role = db.Column(db.String(10), nullable=False)  # 'admin','doctor','patient'
    role = db.Column(db.Enum('admin', 'doctor', 'patient', name='user_roles'), nullable=False, index=True)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # relationships (one-to-one)
    doctor_profile = db.relationship("DoctorProfile",back_populates="user", uselist=False,cascade="all, delete-orphan")
    patient_profile = db.relationship("PatientProfile",back_populates="user",uselist=False,cascade="all, delete-orphan")

    def set_password(self, pwd):
        self.password_hash = generate_password_hash(pwd)

    def check_password(self, pwd):
        return check_password_hash(self.password_hash, pwd)

class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    doctors = db.relationship('DoctorProfile', back_populates='department')
    

class DoctorProfile(db.Model):
    __tablename__ = 'doctors'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True, index=True)
    specialization = db.Column(db.String(120), nullable=False)
    qualifications = db.Column(db.String(250))
    experience_years = db.Column(db.Integer)
    contact_number = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship('User', back_populates='doctor_profile', uselist=False)
    department = db.relationship('Department', back_populates='doctors')
    availabilities = db.relationship('Availability', back_populates='doctor', cascade='all, delete-orphan')
    appointments = db.relationship('Appointment', back_populates='doctor', cascade='all, delete-orphan')

class PatientProfile(db.Model):
    __tablename__ = 'patients'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    
    user = db.relationship('User', back_populates='patient_profile', uselist=False)
    appointments = db.relationship('Appointment', back_populates='patient', cascade='all, delete-orphan')

class Availability(db.Model):
    __tablename__ = 'availabilities'
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    slot_minutes = db.Column(db.Integer, default=30)
    
    doctor = db.relationship('DoctorProfile', back_populates='availabilities')

class Appointment(db.Model):
    __tablename__ = 'appointments'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    status = db.Column(db.Enum('Booked', 'Completed', 'Cancelled', name='appointment_status'), nullable=False, default='Booked', index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    patient = db.relationship('PatientProfile', back_populates='appointments')
    doctor = db.relationship('DoctorProfile', back_populates='appointments')    
    treatment = db.relationship('Treatment', back_populates='appointment', uselist=False, cascade='all, delete-orphan')


class Treatment(db.Model):
    __tablename__ = 'treatments'
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False)
    diagnosis = db.Column(db.Text)
    prescription = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    appointment = db.relationship('Appointment', back_populates='treatment')
