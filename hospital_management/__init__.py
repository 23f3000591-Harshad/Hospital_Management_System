from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path

db = SQLAlchemy()

db_name = "hospital_management"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'Harshad@1207'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_name}.db'
    db.init_app(app)
    
    from .auth import auth
    from .views import views
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    
    from .model import User, Department, DoctorProfile, PatientProfile, Availability, Appointment
    
    create_database(app)

    return app

def create_database(app):
    from .model import User

    db_path = f'hospital_management/{db_name}.db' # Defines the path where we expect the DB file to be.
    if not path.exists(db_path): # If the DB file does not exist, we create it.
        with app.app_context(): # We need to be in the app context to create the DB.
            db.create_all() # Creates all tables defined by our model.
            
            
            # Create a default admin user
            admin_email = "admin@hospital.com"
            if not User.query.filter_by(email=admin_email).first():
                admin = User(name="Admin", email=admin_email, role="admin")
                admin.set_password('Admin@123')
                db.session.add(admin)
                db.session.commit()
            print('Database Created and Admin User Added!')