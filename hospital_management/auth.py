from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .model import *
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)


#register link
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        age = request.form.get('age')
        gender = request.form.get('gender', '').strip()
        password = request.form['password']
        confirm = request.form['confirm_password']
        
        
        if password != confirm:
            flash("Passwords do not match!", category="error")
            
        if len(password) < 6:
            flash("Password must be at least 6 characters long.", category="error")
            return redirect(url_for('auth.register'))
        
        existing = User.query.filter_by(email=email).first()
        if existing:
            flash("Email already registered. Try logging in.", category="error")
            return redirect(url_for('auth.register'))
        else:
            new_user = User(name=name, email=email, role='patient')
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.flush()
            
            patient_profile = PatientProfile(user_id=new_user.id, age=age, gender=gender or None)
            db.session.add(patient_profile)
            db.session.commit()
            flash("Registration successful!", category="success")
            return redirect(url_for('auth.login'))        

    return render_template("register.html")



#login link
@auth.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        if not email or not password:
            flash("Provide both email and password.", "error")
            return redirect(url_for('auth.login'))
    
        user = User.query.filter_by(email=email).first()
        if user:
            if user.check_password(password):
                if user.role == 'admin':
                    flash("Logged in successfully!", category="success")
                    session['user_id'] = user.id
                    session['user_role'] = user.role
                    session['user_name'] = user.name
                    session['user_email'] = user.email
                    return redirect(url_for('views.admin_dashboard'))
                
                elif user.role == 'doctor':
                    flash("Logged in successfully!", category="success")
                    session['user_id'] = user.id
                    session['user_role'] = user.role
                    session['user_name'] = user.name
                    session['user_email'] = user.email
                    return redirect(url_for('views.doctor_dashboard'))
                
                else:
                    flash("Logged in successfully!", category="success")
                    session['user_id'] = user.id
                    session['user_role'] = user.role
                    session['user_name'] = user.name
                    session['user_email'] = user.email
                    return redirect(url_for('views.patient_dashboard'))
                
            else:
                flash("Incorrect password, try again.", category="error")
                
        else:
            flash("Email does not exist.", category="error")
            
    return render_template('login.html')


#logout
@auth.route('/logout')
def logout():
    print("SESSION BEFORE:", dict(session))
    session.pop('user_id', None)
    session.pop('user_role', None)
    session.pop('user_name', None)
    session.pop('user_email', None)
    session.modified = True
    print("SESSION AFTER:", dict(session))
    flash("Logged out successfully!", category="success")
    return redirect(url_for('views.dashboard'))