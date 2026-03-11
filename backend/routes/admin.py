from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..app import db, cache
from ..models import User, Doctor, Patient, Department, Appointment, DoctorAvailability
from functools import wraps

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated

@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def dashboard():
    total_doctors = Doctor.query.count()
    total_patients = Patient.query.count()
    total_appointments = Appointment.query.count()
    booked = Appointment.query.filter_by(status='Booked').count()
    completed = Appointment.query.filter_by(status='Completed').count()
    cancelled = Appointment.query.filter_by(status='Cancelled').count()

    return jsonify({
        'total_doctors': total_doctors,
        'total_patients': total_patients,
        'total_appointments': total_appointments,
        'booked': booked,
        'completed': completed,
        'cancelled': cancelled
    })

# --- DEPARTMENTS ---
@admin_bp.route('/departments', methods=['GET'])
@admin_required
def get_departments():
    depts = Department.query.all()
    return jsonify([d.to_dict() for d in depts])

@admin_bp.route('/departments', methods=['POST'])
@admin_required
def add_department():
    data = request.get_json()
    if not data.get('name'):
        return jsonify({'error': 'Name required'}), 400
    if Department.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Department already exists'}), 400
    dept = Department(name=data['name'], description=data.get('description', ''))
    db.session.add(dept)
    db.session.commit()
    return jsonify(dept.to_dict()), 201

@admin_bp.route('/departments/<int:dept_id>', methods=['PUT'])
@admin_required
def update_department(dept_id):
    dept = Department.query.get_or_404(dept_id)
    data = request.get_json()
    dept.name = data.get('name', dept.name)
    dept.description = data.get('description', dept.description)
    db.session.commit()
    return jsonify(dept.to_dict())

@admin_bp.route('/departments/<int:dept_id>', methods=['DELETE'])
@admin_required
def delete_department(dept_id):
    dept = Department.query.get_or_404(dept_id)
    db.session.delete(dept)
    db.session.commit()
    return jsonify({'message': 'Deleted'})

# --- DOCTORS ---
@admin_bp.route('/doctors', methods=['GET'])
@admin_required
@cache.cached(timeout=60, key_prefix='admin_doctors')
def get_doctors():
    doctors = Doctor.query.all()
    return jsonify([d.to_dict() for d in doctors])

@admin_bp.route('/doctors', methods=['POST'])
@admin_required
def add_doctor():
    cache.delete('admin_doctors')
    data = request.get_json()
    required = ['username', 'email', 'password', 'full_name']
    for f in required:
        if not data.get(f):
            return jsonify({'error': f'{f} is required'}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username taken'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email taken'}), 400

    user = User(username=data['username'], email=data['email'], role='doctor')
    user.set_password(data['password'])
    db.session.add(user)
    db.session.flush()

    doctor = Doctor(
        user_id=user.id,
        full_name=data['full_name'],
        specialization=data.get('specialization', ''),
        department_id=data.get('department_id'),
        phone=data.get('phone', ''),
        experience_years=data.get('experience_years', 0),
        bio=data.get('bio', '')
    )
    db.session.add(doctor)
    db.session.commit()
    return jsonify(doctor.to_dict()), 201

@admin_bp.route('/doctors/<int:doc_id>', methods=['PUT'])
@admin_required
def update_doctor(doc_id):
    cache.delete('admin_doctors')
    doctor = Doctor.query.get_or_404(doc_id)
    data = request.get_json()
    doctor.full_name = data.get('full_name', doctor.full_name)
    doctor.specialization = data.get('specialization', doctor.specialization)
    doctor.department_id = data.get('department_id', doctor.department_id)
    doctor.phone = data.get('phone', doctor.phone)
    doctor.experience_years = data.get('experience_years', doctor.experience_years)
    doctor.bio = data.get('bio', doctor.bio)
    doctor.is_available = data.get('is_available', doctor.is_available)
    db.session.commit()
    return jsonify(doctor.to_dict())

@admin_bp.route('/doctors/<int:doc_id>', methods=['DELETE'])
@admin_required
def delete_doctor(doc_id):
    cache.delete('admin_doctors')
    doctor = Doctor.query.get_or_404(doc_id)
    user = User.query.get(doctor.user_id)
    user.is_active = False
    db.session.commit()
    return jsonify({'message': 'Doctor deactivated'})

# --- PATIENTS ---
@admin_bp.route('/patients', methods=['GET'])
@admin_required
def get_patients():
    q = request.args.get('q', '')
    query = Patient.query
    if q:
        query = query.filter(
            db.or_(
                Patient.full_name.ilike(f'%{q}%'),
                Patient.phone.ilike(f'%{q}%')
            )
        )
    patients = query.all()
    return jsonify([p.to_dict() for p in patients])

@admin_bp.route('/patients/<int:pat_id>', methods=['PUT'])
@admin_required
def update_patient(pat_id):
    patient = Patient.query.get_or_404(pat_id)
    data = request.get_json()
    patient.full_name = data.get('full_name', patient.full_name)
    patient.phone = data.get('phone', patient.phone)
    patient.address = data.get('address', patient.address)
    patient.blood_group = data.get('blood_group', patient.blood_group)
    db.session.commit()
    return jsonify(patient.to_dict())

@admin_bp.route('/patients/<int:pat_id>/blacklist', methods=['POST'])
@admin_required
def blacklist_patient(pat_id):
    patient = Patient.query.get_or_404(pat_id)
    user = User.query.get(patient.user_id)
    user.is_active = not user.is_active
    db.session.commit()
    status = 'activated' if user.is_active else 'deactivated'
    return jsonify({'message': f'Patient {status}'})

# --- APPOINTMENTS ---
@admin_bp.route('/appointments', methods=['GET'])
@admin_required
def get_appointments():
    appointments = Appointment.query.order_by(Appointment.date.desc()).all()
    return jsonify([a.to_dict() for a in appointments])

# --- SEARCH ---
@admin_bp.route('/search', methods=['GET'])
@admin_required
def search():
    q = request.args.get('q', '')
    if not q:
        return jsonify({'doctors': [], 'patients': []})
    doctors = Doctor.query.filter(
        db.or_(
            Doctor.full_name.ilike(f'%{q}%'),
            Doctor.specialization.ilike(f'%{q}%')
        )
    ).all()
    patients = Patient.query.filter(
        Patient.full_name.ilike(f'%{q}%')
    ).all()
    return jsonify({
        'doctors': [d.to_dict() for d in doctors],
        'patients': [p.to_dict() for p in patients]
    })
