import os
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from werkzeug.utils import secure_filename
from models import db, Ticket, Comment, User, Department, SubDepartment

ticket_bp = Blueprint('tickets', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@ticket_bp.route('', methods=['GET'])
@jwt_required()
def get_tickets():
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get('role')
    user_dept_id = claims.get('department_id')
    
    query = Ticket.query
    
    # Filtering based on role
    if role in ['Student', 'Faculty']:
        query = query.filter_by(user_id=current_user_id)
    elif role == 'DeptAdmin':
        query = query.filter_by(department_id=user_dept_id)
    elif role == 'SubDeptAdmin':
        # Let's simplify and just scope to department for now, or filter by exact sub dept
        query = query.filter_by(department_id=user_dept_id)
        
    # Additional filters from query params
    department_id = request.args.get('department_id')
    status = request.args.get('status')
    priority = request.args.get('priority')
    
    if department_id and role not in ['DeptAdmin', 'SubDeptAdmin']:
        query = query.filter_by(department_id=department_id)
    if status:
        query = query.filter_by(status=status)
    if priority:
        query = query.filter_by(priority=priority)
        
    tickets = query.order_by(Ticket.created_at.desc()).all()
    
    return jsonify([ticket.to_dict() for ticket in tickets]), 200

@ticket_bp.route('', methods=['POST'])
@jwt_required()
def create_ticket():
    current_user_id = get_jwt_identity()
    
    title = request.form.get('title')
    description = request.form.get('description')
    department_id = request.form.get('department_id')
    sub_department_id = request.form.get('sub_department_id')
    priority = request.form.get('priority')
    
    if not title or not description or not department_id or not priority:
        return jsonify({'error': 'Missing required fields'}), 400
        
    file_path = None
    if 'file' in request.files:
        file = request.files['file']
        if file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add timestamp to ensure uniqueness
            import time
            filename = f"{int(time.time())}_{filename}"
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            file_path = filename
            
    try:
        new_ticket = Ticket(
            title=title,
            description=description,
            user_id=current_user_id,
            department_id=int(department_id),
            sub_department_id=int(sub_department_id) if sub_department_id else None,
            priority=priority,
            file_path=file_path
        )
        db.session.add(new_ticket)
        db.session.commit()
        
        return jsonify({
            'message': 'Ticket created successfully',
            'ticket': new_ticket.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create ticket', 'details': str(e)}), 500

@ticket_bp.route('/<int:ticket_id>', methods=['GET'])
@jwt_required()
def get_ticket(ticket_id):
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get('role')
    
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
        
    # Authorization check
    if role in ['Student', 'Faculty'] and ticket.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized to view this ticket'}), 403
    if role in ['DeptAdmin', 'SubDeptAdmin'] and ticket.department_id != claims.get('department_id'):
        return jsonify({'error': 'Unauthorized to view this ticket'}), 403
        
    # Include comments
    ticket_dict = ticket.to_dict()
    ticket_dict['comments'] = [comment.to_dict() for comment in ticket.comments]
    
    return jsonify(ticket_dict), 200

@ticket_bp.route('/<int:ticket_id>/status', methods=['PUT'])
@jwt_required()
def update_ticket_status(ticket_id):
    claims = get_jwt()
    role = claims.get('role')
    
    if role not in ['DeptAdmin', 'SubDeptAdmin']:
        return jsonify({'error': 'Unauthorized to update ticket status'}), 403
        
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
        
    if ticket.department_id != claims.get('department_id'):
        return jsonify({'error': 'Unauthorized to update this ticket'}), 403
        
    data = request.get_json()
    new_status = data.get('status')
    
    if not new_status:
        return jsonify({'error': 'Missing status field'}), 400
        
    valid_statuses = ['Pending', 'In Review', 'In Progress', 'Resolved', 'Rejected']
    if new_status not in valid_statuses:
        return jsonify({'error': 'Invalid status'}), 400
        
    try:
        ticket.status = new_status
        db.session.commit()
        return jsonify({
            'message': 'Ticket status updated',
            'ticket': ticket.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update status', 'details': str(e)}), 500

@ticket_bp.route('/<int:ticket_id>/comments', methods=['POST'])
@jwt_required()
def add_comment(ticket_id):
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get('role')
    
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
        
    # Authorization check
    if role in ['Student', 'Faculty'] and ticket.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized to comment on this ticket'}), 403
    if role in ['DeptAdmin', 'SubDeptAdmin'] and ticket.department_id != claims.get('department_id'):
        return jsonify({'error': 'Unauthorized to comment on this ticket'}), 403
        
    content = request.form.get('content')
    if not content and 'file' not in request.files:
        return jsonify({'error': 'Comment must have content or a file'}), 400
        
    file_path = None
    if 'file' in request.files:
        file = request.files['file']
        if file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            import time
            filename = f"{int(time.time())}_{filename}"
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            file_path = filename
            
    try:
        new_comment = Comment(
            content=content or '',
            file_path=file_path,
            ticket_id=ticket_id,
            user_id=current_user_id
        )
        db.session.add(new_comment)
        db.session.commit()
        
        return jsonify({
            'message': 'Comment added successfully',
            'comment': new_comment.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to add comment', 'details': str(e)}), 500

@ticket_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@ticket_bp.route('/departments', methods=['GET'])
def get_departments():
    departments = Department.query.all()
    return jsonify([dept.to_dict() for dept in departments]), 200

@ticket_bp.route('/departments/<int:dept_id>/sub_departments', methods=['GET'])
def get_sub_departments(dept_id):
    sub_dept = SubDepartment.query.filter_by(department_id=dept_id).all()
    return jsonify([sub.to_dict() for sub in sub_dept]), 200
