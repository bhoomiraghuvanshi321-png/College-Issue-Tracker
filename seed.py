from app import create_app
from models import db, Department, SubDepartment

def seed_database():
    app = create_app()
    with app.app_context():
        # Clean existing structure (optional, but good for fresh seed)
        db.drop_all()
        db.create_all()
        
        # Departments
        depts_data = {
            'IT': ['Network', 'Hardware', 'Software', 'Lab Maintenance'],
            'Civil': ['Building Maintenance', 'Water Supply', 'Plumbing'],
            'Electrical': ['Power Supply', 'Lighting', 'AC/Cooling'],
            'Administration': ['Academics', 'Accounts', 'Student Affairs'],
            'Library': ['Book Issue/Return', 'Reading Room', 'Digital Portal'],
            'Hostel': ['Room Maintenance', 'Mess/Food', 'Cleanliness']
        }
        
        for dept_name, sub_depts in depts_data.items():
            dept = Department(name=dept_name)
            db.session.add(dept)
            db.session.commit() # Commit to get ID
            
            for sub_name in sub_depts:
                sub = SubDepartment(name=sub_name, department_id=dept.id)
                db.session.add(sub)
                
        db.session.commit()
        print("Database seeded successfully with Departments and Sub-Departments!")

if __name__ == '__main__':
    seed_database()
