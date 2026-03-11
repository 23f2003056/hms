from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ..app import db
from ..models import User, Patient, Doctor

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401
    if not user.is_active:
        return jsonify({'error': 'Account is deactivated'}), 403

    token = create_access_token(identity=str(user.id))
    profile_id = None
    if user.role == 'doctor' and user.doctor_profile:
        profile_id = user.doctor_profile.id
    elif user.role == 'patient' and user.patient_profile:
        profile_id = user.patient_profile.id

    return jsonify({
        'access_token': token,
        'user': user.to_dict(),
        'profile_id': profile_id
    })

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    required = ['username', 'email', 'password', 'full_name']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already taken'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400

    user = User(username=data['username'], email=data['email'], role='patient')
    user.set_password(data['password'])
    db.session.add(user)
    db.session.flush()

    patient = Patient(
        user_id=user.id,
        full_name=data['full_name'],
        phone=data.get('phone', ''),
        gender=data.get('gender', ''),
        blood_group=data.get('blood_group', '')
    )
    db.session.add(patient)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({
        'access_token': token,
        'user': user.to_dict(),
        'profile_id': patient.id
    }), 201

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)
    data = user.to_dict()
    if user.role == 'doctor' and user.doctor_profile:
        data['profile'] = user.doctor_profile.to_dict()
    elif user.role == 'patient' and user.patient_profile:
        data['profile'] = user.patient_profile.to_dict()
    return jsonify(data)
