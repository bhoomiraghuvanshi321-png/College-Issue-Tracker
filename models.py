from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'Student', 'Faculty', 'DeptAdmin', 'SubDeptAdmin'
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    
    # Relationships
    tickets = db.relationship('Ticket', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'department_id': self.department_id
        }

class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    
    # Relationships
    sub_departments = db.relationship('SubDepartment', backref='department', lazy=True)
    users = db.relationship('User', backref='user_department', lazy=True)
    tickets = db.relationship('Ticket', backref='ticket_department', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }

class SubDepartment(db.Model):
    __tablename__ = 'sub_departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    
    # Relationships
    tickets = db.relationship('Ticket', backref='ticket_sub_department', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'department_id': self.department_id
        }

class Ticket(db.Model):
    __tablename__ = 'tickets'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), nullable=False) # 'Low', 'Medium', 'High', 'Urgent'
    status = db.Column(db.String(20), nullable=False, default='Pending') # 'Pending', 'In Review', 'In Progress', 'Resolved', 'Rejected'
    file_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    sub_department_id = db.Column(db.Integer, db.ForeignKey('sub_departments.id'), nullable=True)
    
    # Relationships
    comments = db.relationship('Comment', backref='ticket', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'status': self.status,
            'file_path': self.file_path,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'user_id': self.user_id,
            'author_name': self.author.name if self.author else None,
            'department_id': self.department_id,
            'department_name': self.ticket_department.name if self.ticket_department else None,
            'sub_department_id': self.sub_department_id,
            'sub_department_name': self.ticket_sub_department.name if self.ticket_sub_department else None
        }

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    file_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'file_path': self.file_path,
            'created_at': self.created_at.isoformat(),
            'user_id': self.user_id,
            'author_name': self.author.name if self.author else None,
            'ticket_id': self.ticket_id
        }
