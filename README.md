# Hospital Management System

## Overview
A full-stack web application built using Flask to manage core hospital workflows, including doctor availability, patient appointments, and treatment records.  
The system supports role-based access control for Admin, Doctor, and Patient, ensuring secure and structured interactions across the platform.

This project focuses on backend design, database modeling, and real-world business logic rather than UI aesthetics.

---

## Key Features

### Authentication & Roles
- Secure user authentication with password hashing
- Role-based access control:
  - Admin
  - Doctor
  - Patient

### Admin Capabilities
- Create and manage departments
- Create, edit, and delete doctor profiles
- View patients and their appointment history
- View and manage upcoming appointments

### Doctor Capabilities
- Set weekly availability with predefined time slots
- View assigned and upcoming appointments
- Update appointment status (Booked / Completed / Cancelled)
- Maintain patient treatment records (diagnosis, prescription, notes)
- Access patient history for assigned appointments

### Patient Capabilities
- View departments and doctor profiles
- Book appointments based on real-time availability
- Cancel upcoming appointments
- View personal appointment history
- Edit personal profile details

---

## Tech Stack
- Backend: Python, Flask
- Database: SQLAlchemy (ORM), SQLite / MySQL
- Authentication: Flask-Login, Werkzeug Security
- Frontend: HTML, CSS, Jinja2 Templates

---

## Database Design Highlights
- Normalized relational schema
- One-to-one and one-to-many relationships
- Use of Enums for roles and appointment status
- Indexed fields for efficient querying
- Cascading deletes to maintain data integrity

Key entities:
- Users
- DoctorProfile
- PatientProfile
- Departments
- Availabilities
- Appointments
- Treatments

---

## Application Workflow
1. Admin sets up departments and doctor accounts
2. Doctors define availability slots
3. Patients book appointments based on availability
4. Doctors manage appointments and record treatments
5. Patients and admins can view appointment history

All workflows are enforced at the backend level to prevent unauthorized actions.

---

## Setup Instructions

## Setup

```bash
git clone https://github.com/23f3000591-Harshad/Hospital_Management_System.git
cd Hospital_Management_System

python -m venv venv
source venv/bin/activate    # Linux / macOS
venv\Scripts\activate       # Windows

pip install -r requirements.txt
flask run
pip install -r requirements.txt
flask run
