from flask import render_template, request, redirect, url_for, flash, session
from datetime import date, timedelta, datetime, time
from flask import Blueprint
from . import db
from .model import *
from flask import session
views = Blueprint('views', __name__)


@views.route("/")
def dashboard():
    return render_template('dashboard.html')



#------Admin Dashboard------#
@views.route("/admin")
def admin_dashboard():
    
    departments = Department.query.all() # Get all departments from the database 
    patients = PatientProfile.query.all() # Get all patients from the database
    
    # upcoming appointments
    appointments = (
        Appointment.query
        .filter_by(status='Booked')
        .filter(Appointment.date >= date.today())
        .order_by(Appointment.date, Appointment.time)
        .all()
    )
    
    return render_template('admin.html', 
                        patients=patients, 
                        departments=departments,
                        appointments=appointments)  

#------Create Doctor------#
@views.route("/admin/create_doctor", methods=['GET', 'POST'])
def create_doctor():
    departments = Department.query.all()
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        department_id = request.form.get('department_id')  
        specialization = request.form.get('specialization', '').strip()  
        qualifications = request.form.get('qualifications', '').strip()
        experience_years = request.form.get('experience_years', '').strip() or None
        contact_number = request.form.get('contact_number', '').strip()
            
        if not (name and email and password and department_id and specialization):
            flash("Please fill required fields.", "error")
            return redirect(url_for('views.create_doctor'))
        
        try:
            experience_years = int(experience_years) if experience_years else None
            department_id = int(department_id)  
        except ValueError:
            flash("Invalid input.", "error")
            return redirect(url_for('views.create_doctor'))
        
        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "error")
            return redirect(url_for('views.create_doctor'))
        
        new_user = User(name=name, email=email, role='doctor')
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        doctor_profile = DoctorProfile(
            user_id=new_user.id,
            department_id=department_id,  
            specialization=specialization,
            qualifications=qualifications,
            experience_years=experience_years,
            contact_number=contact_number
        )
        
        db.session.add(doctor_profile)
        db.session.commit()
        
        flash("Doctor created successfully!", "success")
        return redirect(url_for('views.admin_dashboard'))
    
    return render_template('create_doc.html', departments=departments)


#------Create Department------#
@views.route("/admin/create_department", methods=['GET', 'POST'])
def create_department():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        
        if not name:
            flash("Department name is required.", "error")
            return redirect(url_for('views.create_department'))
        
        if Department.query.filter_by(name=name).first():
            flash("Department already exists.", "error")
            return redirect(url_for('views.create_department'))
        
        new_department = Department(name=name, description=description)
        db.session.add(new_department)
        db.session.commit()
        
        flash("Department created successfully!", "success")
        return redirect(url_for('views.admin_dashboard'))
    
    return render_template('create_department.html')


#-------Delete Patient-------#
@views.route("/admin/patient/<int:patient_id>/delete", methods=['POST'])
def delete_patient(patient_id):
    patient_user = User.query.filter_by(id=patient_id, role='patient').first()
    if not patient_user:
        flash("Patient not found.", "error")
        return redirect(url_for('views.admin_dashboard'))
    
    db.session.delete(patient_user)
    db.session.commit()
    
    flash("Patient deleted successfully.", "success")
    return redirect(url_for('views.admin_dashboard'))


#-------Delete Department-------#
@views.route("/admin/department/<int:id>/delete", methods=['POST'])
def delete_department(id):
    department = Department.query.get(id)
    if not department:
        flash("Department not found.", "error")
        return redirect(url_for('views.admin_dashboard'))
    db.session.delete(department)
    db.session.commit()
    flash("Department deleted successfully.", "success")
    return redirect(url_for('views.admin_dashboard'))



#-------Delete Doctor-------#
@views.route("/admin/doctor/<int:doctor_id>/delete", methods=['POST'])
def delete_doctor(doctor_id):
    doctor_profile = DoctorProfile.query.get(doctor_id)
    if not doctor_profile:
        flash("Doctor not found.", "error")
        return redirect(url_for('views.admin_dashboard'))
    
    user = doctor_profile.user
    db.session.delete(user)
    db.session.commit()
    
    flash("Doctor deleted successfully.", "success")
    return redirect(url_for('views.admin_dashboard'))


#--------Edit Doctor--------#
@views.route("/admin/doctor/<int:doctor_id>/edit", methods=['GET', 'POST'])
def edit_doctor(doctor_id):
    doctor_profile = DoctorProfile.query.get_or_404(doctor_id)
    departments = Department.query.all()
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        department_id = request.form.get('department_id')
        specialization = request.form.get('specialization', '').strip()
        qualifications = request.form.get('qualifications', '').strip()
        experience_years = request.form.get('experience_years', '').strip() or None
        contact_number = request.form.get('contact_number', '').strip()
        
        if not (name and email and specialization):
            flash("Please fill required fields.", "error")
            return redirect(url_for('views.edit_doctor', doctor_id=doctor_id))
        
        try:
            experience_years = int(experience_years) if experience_years else None
        except ValueError:
            flash("Experience must be a number.", "error")
            return redirect(url_for('views.edit_doctor', doctor_id=doctor_id))
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.id != doctor_profile.user_id:
            flash("Email already registered.", "error")
            return redirect(url_for('views.edit_doctor', doctor_id=doctor_id))
        
        doctor_profile.user.name = name
        doctor_profile.user.email = email
        doctor_profile.department_id = department_id
        doctor_profile.specialization = specialization
        doctor_profile.qualifications = qualifications
        doctor_profile.experience_years = experience_years
        doctor_profile.contact_number = contact_number
        
        db.session.commit()
        
        flash("Doctor updated successfully!", "success")
        return redirect(url_for('views.admin_dashboard'))
    
    return render_template('edit_doctor.html', doctor=doctor_profile, departments=departments)



#-------view department details-------#
@views.route("/admin/department/<int:id>")
def view_department(id):
    department = Department.query.get(id)
    doctors = department.doctors
    return render_template('view_department.html', department=department, doctors=doctors)


#------View Patient History------#
@views.route("/admin/patient/<int:patient_id>/history")
def view_patient_history(patient_id):
    patient_profile = PatientProfile.query.filter_by(user_id=patient_id).first()
    if not patient_profile:
        flash("Patient not found.", "error")
        return redirect(url_for('views.admin_dashboard'))
    
    appointments = Appointment.query.filter_by(patient_id=patient_profile.id).all()
    return render_template('patient_history.html', patient=patient_profile, appointments=appointments)

#--------------------------------------------------------------------------------------------------------------------------------------------------

#--------------Doctor Routes starts from here------------------------#

#---------------------------------------------------------------------------------------------------------------------------------------------------

@views.route("/doctor/dashboard", methods=['GET'])
def doctor_dashboard():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))

    user = User.query.get(user_id)
    # if not user or user.role != "doctor":
    #     flash("Access denied.", "error")
    #     return redirect(url_for("views.dashboard"))

    doctor_profile = DoctorProfile.query.filter_by(user_id=user.id).first()
    if not doctor_profile:
        flash("Doctor profile not found.", "error")
        return redirect(url_for("views.dashboard"))

    # upcoming appointments (Booked and today+/future)
    upcoming = (
        Appointment.query
        .filter_by(doctor_id=doctor_profile.id)
        .filter(Appointment.status == 'Booked')
        .filter(Appointment.date >= date.today())
        .order_by(Appointment.date, Appointment.time)
        .all()
    )

    # assigned patients (unique patients who have appointments with this doctor OR all patients)
    patient_ids = {a.patient_id for a in Appointment.query.filter_by(doctor_id=doctor_profile.id).all()}
    assigned_patients = []
    if patient_ids:
        assigned_patients = PatientProfile.query.filter(PatientProfile.id.in_(list(patient_ids))).all()

    return render_template(
        "doctor.html",
        doctor=doctor_profile,
        upcoming=upcoming,
        assigned_patients=assigned_patients
    )


@views.route("/doctor/appointment/<int:appointment_id>/update", methods=['GET','POST'])
def update_appointment(appointment_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))
    user = User.query.get(user_id)
    if not user or user.role != "doctor":
        flash("Access denied.", "error")
        return redirect(url_for("views.dashboard"))

    appointment = Appointment.query.get_or_404(appointment_id)
    doctor_profile = DoctorProfile.query.filter_by(user_id=user.id).first()
    if appointment.doctor_id != doctor_profile.id:
        flash("You are not allowed to update that appointment.", "error")
        return redirect(url_for("views.doctor_dashboard"))

    if request.method == "POST":
        # allow updating date/time or patient history/treatment etc.
        new_date = request.form.get("date")
        new_time = request.form.get("time")
        notes = request.form.get("notes", "").strip()

        try:
            if new_date:
                appointment.date = datetime.strptime(new_date, "%Y-%m-%d").date()
            if new_time:
                appointment.time = datetime.strptime(new_time, "%H:%M").time()
        except ValueError:
            flash("Invalid date/time format.", "error")
            return redirect(url_for("views.doctor_dashboard"))

        # optionally save notes to Treatment if one exists or create a treatment record
        if notes:
            if appointment.treatment:
                appointment.treatment.notes = notes
            else:
                t = Treatment(appointment_id=appointment.id, notes=notes)
                db.session.add(t)

        db.session.commit()
        flash("Appointment updated.", "success")
        return redirect(url_for("views.doctor_dashboard"))

    # GET: render a simple edit page
    return render_template("edit_appointment.html", appointment=appointment)



# Mark appointment as complete
@views.route("/doctor/appointment/<int:appointment_id>/complete", methods=['POST'])
def complete_appointment(appointment_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))
    user = User.query.get(user_id)
    if not user or user.role != "doctor":
        flash("Access denied.", "error")
        return redirect(url_for("views.dashboard"))

    appointment = Appointment.query.get_or_404(appointment_id)
    doctor_profile = DoctorProfile.query.filter_by(user_id=user.id).first()
    if appointment.doctor_id != doctor_profile.id:
        flash("You are not allowed to update that appointment.", "error")
        return redirect(url_for("views.doctor_dashboard"))

    appointment.status = "Completed"
    db.session.commit()
    flash("Appointment marked as completed.", "success")
    return redirect(url_for("views.doctor_dashboard"))


# Cancel appointment
@views.route("/doctor/appointment/<int:appointment_id>/cancel", methods=['POST'])
def doctor_cancel_appointment(appointment_id): 
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))
    user = User.query.get(user_id)
    if not user or user.role != "doctor":
        flash("Access denied.", "error")
        return redirect(url_for("views.dashboard"))

    appointment = Appointment.query.get_or_404(appointment_id)
    doctor_profile = DoctorProfile.query.filter_by(user_id=user.id).first()
    if appointment.doctor_id != doctor_profile.id:
        flash("You are not allowed to cancel that appointment.", "error")
        return redirect(url_for("views.doctor_dashboard"))

    appointment.status = "Cancelled"
    db.session.commit()
    flash("Appointment cancelled.", "success")
    return redirect(url_for("views.doctor_dashboard"))


#-----Doctor Availability-----#
@views.route("/doctor/availability", methods=['GET', 'POST'])
def doctor_availability():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))

    user = User.query.get(user_id)
    if not user or user.role != "doctor":
        flash("Access denied.", "error")
        return redirect(url_for("views.dashboard"))

    doctor = DoctorProfile.query.filter_by(user_id=user.id).first()
    if not doctor:
        flash("Doctor profile not found.", "error")
        return redirect(url_for("views.dashboard"))

    # define the 7-day window
    today = date.today()
    days = [today + timedelta(days=i) for i in range(7)]
    iso_days = [d.isoformat() for d in days]

    # preset slot mapping (easy to change)
    PRESETS = {
        "morning": (time(hour=8, minute=0), time(hour=12, minute=0)),
        "evening": (time(hour=16, minute=0), time(hour=21, minute=0)),
    }

    if request.method == "POST":
        selected = request.form.getlist("selected[]")  

        # remove existing availabilities in the 7-day window for this doctor
        Availability.query.filter(
            Availability.doctor_id == doctor.id,
            Availability.date.in_(iso_days)
        ).delete(synchronize_session=False)

        # build new Availability rows from selected
        to_add = []
        for entry in selected:
            try:
                iso, kind = entry.split("|")
                if iso not in iso_days or kind not in PRESETS:
                    continue
                st, et = PRESETS[kind]
                to_add.append(Availability(
                    doctor_id=doctor.id,
                    date=datetime.strptime(iso, "%Y-%m-%d").date(),
                    start_time=st,
                    end_time=et
                ))
            except ValueError:
                continue

        if to_add:
            db.session.add_all(to_add)
        db.session.commit()
        flash("Availability saved.", "success")
        return redirect(url_for("views.doctor_availability"))

    # GET: query existing availabilities in window and create a set for quick checks
    existing = Availability.query.filter(
        Availability.doctor_id == doctor.id,
        Availability.date.in_(iso_days)
    ).all()

    # set of strings like "YYYY-MM-DD|morning" if corresponding slot exists
    existing_set = set()
    for a in existing:
        iso = a.date.isoformat()
        for kind, (pst, pet) in PRESETS.items():
            if a.start_time == pst and a.end_time == pet:
                existing_set.add(f"{iso}|{kind}")
                break

    return render_template("doctor_availability.html",days=days,existing_set=existing_set)



# Doctor: Update patient history
@views.route("/doctor/appointment/<int:appointment_id>/update_history", methods=["GET", "POST"])
def update_patient_history(appointment_id):
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in.", "error")
        return redirect(url_for("auth.login"))

    user = User.query.get(user_id)
    if not user or user.role != "doctor":
        flash("Access denied.", "error")
        return redirect(url_for("views.dashboard"))

    
    appointment = Appointment.query.get_or_404(appointment_id)
    
    doctor_profile = DoctorProfile.query.filter_by(user_id=user.id).first()
    if not doctor_profile or appointment.doctor_id != doctor_profile.id:
        flash("You are not allowed to edit this appointment.", "error")
        return redirect(url_for("views.doctor_dashboard"))

    # find or create treatment for this appointment
    treatment = Treatment.query.filter_by(appointment_id=appointment.id).first()

    if request.method == "POST":
        visit_type = request.form.get("visit_type", "").strip()
        tests_done = request.form.get("tests_done", "").strip()
        diagnosis = request.form.get("diagnosis", "").strip()
        prescription = request.form.get("prescription", "").strip()
        medicines = request.form.get("medicines", "").strip()
        mark_complete = request.form.get("mark_complete") == "on"

        notes_parts = []
        if visit_type:
            notes_parts.append(f"Visit Type: {visit_type}")
        if tests_done:
            notes_parts.append(f"Tests: {tests_done}")
        if medicines:
            notes_parts.append(f"Medicines: {medicines}")
        notes = "\n".join(notes_parts).strip() if notes_parts else None

        try:
            if not treatment:
                treatment = Treatment(
                    appointment_id=appointment.id,
                    diagnosis=diagnosis or None,
                    prescription=prescription or None,
                    notes=notes
                )
                db.session.add(treatment)
            else:
                treatment.diagnosis = diagnosis or None
                treatment.prescription = prescription or None
                treatment.notes = notes

            if mark_complete:
                appointment.status = "Completed"

            db.session.commit()
            flash("Patient history updated successfully.", "success")
            return redirect(url_for("views.doctor_dashboard"))
        except Exception as e:
            db.session.rollback()
            flash("Could not save history. Try again.", "error")
            # optionally log e
            return redirect(url_for("views.update_patient_history", appointment_id=appointment_id))

    existing = {
        "visit_type": "",
        "tests_done": "",
        "diagnosis": treatment.diagnosis if treatment else "",
        "prescription": treatment.prescription if treatment else "",
        "medicines": ""
    }
    if treatment and treatment.notes:
        for line in treatment.notes.splitlines():
            if line.startswith("Visit Type:"):
                existing["visit_type"] = line.split(":", 1)[1].strip()
            elif line.startswith("Tests:"):
                existing["tests_done"] = line.split(":", 1)[1].strip()
            elif line.startswith("Medicines:"):
                existing["medicines"] = line.split(":", 1)[1].strip()

    return render_template(
        "update_history.html",
        appointment=appointment,
        patient=appointment.patient,      # PatientProfile
        doctor=doctor_profile,
        treatment=treatment,
        existing=existing
    )
''' 
____________________________________________________________
|                                                           |
|-----------------------------------------------------------|
|--------------Patient Routes starts from here--------------|
|-----------------------------------------------------------|
|___________________________________________________________|
'''


#------Patient Dashboard------#
@views.route("/patient/dashboard")
def patient_dashboard():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))

    user = User.query.get(user_id)

    if user.role != "patient":
        return redirect(url_for("views.dashboard"))

    patient_profile = PatientProfile.query.filter_by(user_id=user.id).first()
    departments = Department.query.all()

    upcoming_appointments = (
        Appointment.query
        .filter_by(patient_id=patient_profile.id, status="Booked")
        .filter(Appointment.date >= date.today())
        .order_by(Appointment.date, Appointment.time)
        .all()
    )

    return render_template("patient.html", patient=user, departments=departments, appointments=upcoming_appointments)



#------Patient Edit------#
@views.route("/patient/edit_profile", methods=['GET', 'POST'])
def patient_edit_profile():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to edit your profile.", "error")
        return redirect(url_for('auth.login'))
    
    user = User.query.get_or_404(user_id)
    # patient_profile = user.patient_profile
    patient_profile = PatientProfile.query.filter_by(user_id=user.id).first()
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        age = request.form.get('age', '').strip() or None
        gender = request.form.get('gender', '').strip()
        password = request.form.get('password', '').strip()
        
        if not name or not email:
            flash("Name and email are required.", "error")
            return redirect(url_for('views.patient_edit_profile'))
        existing_user = User.query.filter_by(email=email).first()
        
        if existing_user and existing_user.id != user.id:
            flash("Email already registered.", "error")
            return redirect(url_for('views.patient_edit_profile'))
        try:
            age = int(age) if age else None
        except ValueError:
            flash("Age must be a number.", "error")
            return redirect(url_for('views.patient_edit_profile'))
        
        user.name = name
        user.email = email
        user.set_password(password)
        patient_profile.age = age
        patient_profile.gender = gender
        db.session.commit()
        
        flash("Profile updated successfully!", "success")
        return redirect(url_for('views.patient_dashboard'))
    
    return render_template('patient_edit_profile.html', user=user, patient=patient_profile)


#-----Patient History-----#
@views.route("/patient/history")
def patient_history():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to view your history.", "error")
        return redirect(url_for('auth.login'))
    user = User.query.get_or_404(user_id)
    patient_profile = PatientProfile.query.filter_by(user_id=user.id).first()
    appointments = Appointment.query.filter_by(patient_id=patient_profile.id).all()
    return render_template('patient_history.html', patient=patient_profile, appointments=appointments)



#------View Department Details------#
@views.route("/patient/view_department/<int:department_id>")
def patient_view_department(department_id):
    department = Department.query.get_or_404(department_id)
    return render_template('patient_view_department.html', department=department)



#------View Doctor Profile------#
@views.route("/patient/doctor/<int:doctor_id>")
def view_doctor_profile(doctor_id):
    doctor_profile = DoctorProfile.query.get_or_404(doctor_id)
    return render_template('view_doctor_profile.html', doctor=doctor_profile)


#------Book Appointment------#
@views.route("/patient/book_appointment/<int:doctor_id>/<int:availability_id>", methods=['GET', 'POST'])
def book_appointment(doctor_id, availability_id):
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to book an appointment.", "error")
        return redirect(url_for('auth.login'))
    
    user = User.query.get(user_id)
    if user.role != 'patient':
        flash("Only patients can book appointments.", "error")
        return redirect(url_for('views.dashboard'))
    
    patient_profile = PatientProfile.query.filter_by(user_id=user.id).first()
    doctor_profile = DoctorProfile.query.get_or_404(doctor_id)
    availability = Availability.query.get_or_404(availability_id)
    
    if request.method == 'POST':
        selected_time_str = request.form.get('selected_time')
        
        if not selected_time_str:
            flash("Please select a time slot.", "error")
            return redirect(url_for('views.book_appointment', doctor_id=doctor_id, availability_id=availability_id))
        
        # Parse the selected time
        selected_time = datetime.strptime(selected_time_str, '%H:%M').time()
        
        # Check if slot is already booked
        existing_appointment = Appointment.query.filter_by(
            doctor_id=doctor_id,
            date=availability.date,
            time=selected_time,
            status='Booked'
        ).first()
        
        if existing_appointment:
            flash("This time slot is already booked. Please select another.", "error")
            return redirect(url_for('views.book_appointment', doctor_id=doctor_id, availability_id=availability_id))
        
        # Create new appointment
        new_appointment = Appointment(
            patient_id=patient_profile.id,
            doctor_id=doctor_id,
            date=availability.date,
            time=selected_time,
            status='Booked'
        )
        
        db.session.add(new_appointment)
        db.session.commit()
        
        flash("Appointment booked successfully!", "success")
        return redirect(url_for('views.patient_dashboard'))
    
    # Generate available time slots
    available_slots = []
    current_time = datetime.combine(date.today(), availability.start_time)
    end_time = datetime.combine(date.today(), availability.end_time)
    
    while current_time < end_time:
        slot_time = current_time.time()
        
        # Check if this slot is already booked
        is_booked = Appointment.query.filter_by(
            doctor_id=doctor_id,
            date=availability.date,
            time=slot_time,
            status='Booked'
        ).first() is not None
        
        available_slots.append({
            'time': slot_time,
            'time_str': slot_time.strftime('%I:%M %p'),
            'is_booked': is_booked
        })
        
        current_time += timedelta(minutes=availability.slot_minutes)
    
    return render_template('book_appointment.html', 
                        doctor=doctor_profile, 
                        availability=availability,
                        available_slots=available_slots)
    
    
#------Cancel Appointment------#
@views.route("/patient/appointment/<int:appointment_id>/cancel", methods=['POST'])
def cancel_appointment(appointment_id):  
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to cancel appointments.", "error")
        return redirect(url_for('auth.login'))
    
    user = User.query.get(user_id)
    if user.role != 'patient':
        flash("Access denied.", "error")
        return redirect(url_for('views.dashboard'))
    
    patient_profile = PatientProfile.query.filter_by(user_id=user.id).first()
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Verify the appointment belongs to this patient
    if appointment.patient_id != patient_profile.id:
        flash("You cannot cancel this appointment.", "error")
        return redirect(url_for('views.patient_dashboard'))

    # Check if appointment can be cancelled
    if appointment.status == 'Completed':
        flash("Cannot cancel completed appointments.", "error")
        return redirect(url_for('views.patient_dashboard'))
    
    if appointment.status == 'Cancelled':
        flash("This appointment is already cancelled.", "info")
        return redirect(url_for('views.patient_dashboard'))
    
    # Cancel the appointment
    appointment.status = 'Cancelled'
    db.session.commit()
    
    flash("Appointment cancelled successfully.", "success")
    return redirect(url_for('views.patient_dashboard'))