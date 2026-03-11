from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..app import db, cache
from ..models import User, Patient, Doctor, Department, Appointment, DoctorAvailability
from datetime import date, datetime, timedelta
from functools import wraps
from celery import shared_task
import csv, io

patient_bp = Blueprint('patient', __name__)

def patient_required(f):
    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if not user or user.role != 'patient':
            return jsonify({'error': 'Patient access required'}), 403
        return f(user, *args, **kwargs)
    return decorated

@patient_bp.route('/dashboard', methods=['GET'])
@patient_required
def dashboard(user):
    patient = user.patient_profile
    today = date.today()
    upcoming = Appointment.query.filter_by(patient_id=patient.id).filter(
        Appointment.date >= today, Appointment.status == 'Booked').count()
    total = Appointment.query.filter_by(patient_id=patient.id).count()
    completed = Appointment.query.filter_by(patient_id=patient.id, status='Completed').count()

    depts = Department.query.all()
    return jsonify({
        'patient': patient.to_dict(),
        'upcoming_appointments': upcoming,
        'total_appointments': total,
        'completed_appointments': completed,
        'departments': [d.to_dict() for d in depts]
    })

@patient_bp.route('/profile', methods=['PUT'])
@patient_required
def update_profile(user):
    patient = user.patient_profile
    data = request.get_json()
    patient.full_name = data.get('full_name', patient.full_name)
    patient.phone = data.get('phone', patient.phone)
    patient.address = data.get('address', patient.address)
    patient.blood_group = data.get('blood_group', patient.blood_group)
    patient.emergency_contact = data.get('emergency_contact', patient.emergency_contact)
    if data.get('date_of_birth'):
        patient.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
    patient.gender = data.get('gender', patient.gender)
    db.session.commit()
    return jsonify(patient.to_dict())

@patient_bp.route('/doctors', methods=['GET'])
@patient_required
@cache.cached(timeout=120, key_prefix='patient_doctors')
def get_doctors(user):
    q = request.args.get('q', '')
    dept_id = request.args.get('department_id')
    query = Doctor.query.filter_by(is_available=True)
    if q:
        query = query.filter(
            db.or_(
                Doctor.full_name.ilike(f'%{q}%'),
                Doctor.specialization.ilike(f'%{q}%')
            )
        )
    if dept_id:
        query = query.filter_by(department_id=dept_id)
    doctors = query.all()
    return jsonify([d.to_dict() for d in doctors])

@patient_bp.route('/doctors/<int:doc_id>/availability', methods=['GET'])
@patient_required
def doctor_availability(user, doc_id):
    today = date.today()
    week_end = today + timedelta(days=7)
    avails = DoctorAvailability.query.filter_by(doctor_id=doc_id).filter(
        DoctorAvailability.date >= today,
        DoctorAvailability.date <= week_end
    ).order_by(DoctorAvailability.date).all()
    return jsonify([a.to_dict() for a in avails])

@patient_bp.route('/appointments', methods=['GET'])
@patient_required
def get_appointments(user):
    patient = user.patient_profile
    filter_type = request.args.get('filter', 'all')
    today = date.today()
    query = Appointment.query.filter_by(patient_id=patient.id)
    if filter_type == 'upcoming':
        query = query.filter(Appointment.date >= today, Appointment.status == 'Booked')
    elif filter_type == 'past':
        query = query.filter(Appointment.date < today)
    apts = query.order_by(Appointment.date.desc()).all()
    return jsonify([a.to_dict() for a in apts])

@patient_bp.route('/appointments', methods=['POST'])
@patient_required
def book_appointment(user):
    patient = user.patient_profile
    data = request.get_json()
    required = ['doctor_id', 'date', 'time']
    for f in required:
        if not data.get(f):
            return jsonify({'error': f'{f} is required'}), 400

    apt_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    if apt_date < date.today():
        return jsonify({'error': 'Cannot book past appointments'}), 400

    # Prevent double booking same doctor same slot
    existing = Appointment.query.filter_by(
        doctor_id=data['doctor_id'],
        date=apt_date,
        time=data['time'],
        status='Booked'
    ).first()
    if existing:
        return jsonify({'error': 'This slot is already booked'}), 400

    apt = Appointment(
        patient_id=patient.id,
        doctor_id=data['doctor_id'],
        date=apt_date,
        time=data['time'],
        reason=data.get('reason', ''),
        status='Booked'
    )
    db.session.add(apt)
    db.session.commit()
    return jsonify(apt.to_dict()), 201

@patient_bp.route('/appointments/<int:apt_id>', methods=['PUT'])
@patient_required
def reschedule_appointment(user, apt_id):
    patient = user.patient_profile
    apt = Appointment.query.filter_by(id=apt_id, patient_id=patient.id).first_or_404()
    if apt.status != 'Booked':
        return jsonify({'error': 'Only booked appointments can be rescheduled'}), 400
    data = request.get_json()
    if data.get('date'):
        apt.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    if data.get('time'):
        apt.time = data['time']
    db.session.commit()
    return jsonify(apt.to_dict())

@patient_bp.route('/appointments/<int:apt_id>/cancel', methods=['POST'])
@patient_required
def cancel_appointment(user, apt_id):
    patient = user.patient_profile
    apt = Appointment.query.filter_by(id=apt_id, patient_id=patient.id).first_or_404()
    if apt.status != 'Booked':
        return jsonify({'error': 'Only booked appointments can be cancelled'}), 400
    apt.status = 'Cancelled'
    db.session.commit()
    return jsonify(apt.to_dict())

@patient_bp.route('/departments', methods=['GET'])
@patient_required
@cache.cached(timeout=300, key_prefix='departments_list')
def get_departments(user):
    depts = Department.query.all()
    return jsonify([d.to_dict() for d in depts])

@patient_bp.route('/export-csv', methods=['POST'])
@patient_required
def trigger_export(user):
    patient = user.patient_profile
    from ..tasks import export_patient_csv
    task = export_patient_csv.delay(patient.id)
    return jsonify({'task_id': task.id, 'message': 'Export started, you will be notified'})

@patient_bp.route('/export-csv/<task_id>', methods=['GET'])
@patient_required
def check_export(user, task_id):
    from ..tasks import export_patient_csv
    from celery.result import AsyncResult
    result = AsyncResult(task_id)
    if result.ready():
        return jsonify({'status': 'done', 'data': result.get()})
    return jsonify({'status': result.status})
