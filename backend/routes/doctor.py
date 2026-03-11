from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..app import db
from ..models import User, Doctor, Appointment, Treatment, DoctorAvailability
from datetime import date, datetime, timedelta
from functools import wraps

doctor_bp = Blueprint('doctor', __name__)

def doctor_required(f):
    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        if not user or user.role != 'doctor':
            return jsonify({'error': 'Doctor access required'}), 403
        return f(user, *args, **kwargs)
    return decorated

@doctor_bp.route('/dashboard', methods=['GET'])
@doctor_required
def dashboard(user):
    doctor = user.doctor_profile
    today = date.today()
    week_end = today + timedelta(days=7)

    today_apts = Appointment.query.filter_by(doctor_id=doctor.id, date=today).filter(
        Appointment.status == 'Booked').count()
    week_apts = Appointment.query.filter_by(doctor_id=doctor.id).filter(
        Appointment.date >= today, Appointment.date <= week_end,
        Appointment.status == 'Booked').count()
    total_patients = db.session.query(Appointment.patient_id).filter_by(
        doctor_id=doctor.id).distinct().count()

    return jsonify({
        'doctor': doctor.to_dict(),
        'today_appointments': today_apts,
        'week_appointments': week_apts,
        'total_patients': total_patients
    })

@doctor_bp.route('/appointments', methods=['GET'])
@doctor_required
def get_appointments(user):
    doctor = user.doctor_profile
    filter_type = request.args.get('filter', 'upcoming')
    today = date.today()

    query = Appointment.query.filter_by(doctor_id=doctor.id)
    if filter_type == 'today':
        query = query.filter(Appointment.date == today)
    elif filter_type == 'upcoming':
        query = query.filter(Appointment.date >= today, Appointment.status == 'Booked')
    elif filter_type == 'past':
        query = query.filter(Appointment.date < today)

    apts = query.order_by(Appointment.date.asc(), Appointment.time.asc()).all()
    return jsonify([a.to_dict() for a in apts])

@doctor_bp.route('/appointments/<int:apt_id>/complete', methods=['POST'])
@doctor_required
def complete_appointment(user, apt_id):
    doctor = user.doctor_profile
    apt = Appointment.query.filter_by(id=apt_id, doctor_id=doctor.id).first_or_404()
    data = request.get_json()

    apt.status = 'Completed'
    if not apt.treatment:
        treatment = Treatment(
            appointment_id=apt.id,
            diagnosis=data.get('diagnosis', ''),
            prescription=data.get('prescription', ''),
            notes=data.get('notes', ''),
        )
        if data.get('next_visit'):
            from datetime import date as date_type
            treatment.next_visit = datetime.strptime(data['next_visit'], '%Y-%m-%d').date()
        db.session.add(treatment)
    else:
        apt.treatment.diagnosis = data.get('diagnosis', apt.treatment.diagnosis)
        apt.treatment.prescription = data.get('prescription', apt.treatment.prescription)
        apt.treatment.notes = data.get('notes', apt.treatment.notes)

    db.session.commit()
    return jsonify(apt.to_dict())

@doctor_bp.route('/appointments/<int:apt_id>/cancel', methods=['POST'])
@doctor_required
def cancel_appointment(user, apt_id):
    doctor = user.doctor_profile
    apt = Appointment.query.filter_by(id=apt_id, doctor_id=doctor.id).first_or_404()
    apt.status = 'Cancelled'
    db.session.commit()
    return jsonify(apt.to_dict())

@doctor_bp.route('/patients', methods=['GET'])
@doctor_required
def get_patients(user):
    doctor = user.doctor_profile
    apts = Appointment.query.filter_by(doctor_id=doctor.id).all()
    seen = set()
    patients = []
    for apt in apts:
        if apt.patient_id not in seen:
            seen.add(apt.patient_id)
            patients.append(apt.patient.to_dict())
    return jsonify(patients)

@doctor_bp.route('/patients/<int:pat_id>/history', methods=['GET'])
@doctor_required
def patient_history(user, pat_id):
    doctor = user.doctor_profile
    apts = Appointment.query.filter_by(
        doctor_id=doctor.id, patient_id=pat_id
    ).order_by(Appointment.date.desc()).all()
    return jsonify([a.to_dict() for a in apts])

@doctor_bp.route('/availability', methods=['GET'])
@doctor_required
def get_availability(user):
    doctor = user.doctor_profile
    today = date.today()
    week_end = today + timedelta(days=7)
    avails = DoctorAvailability.query.filter_by(doctor_id=doctor.id).filter(
        DoctorAvailability.date >= today,
        DoctorAvailability.date <= week_end
    ).order_by(DoctorAvailability.date).all()
    return jsonify([a.to_dict() for a in avails])

@doctor_bp.route('/availability', methods=['POST'])
@doctor_required
def set_availability(user):
    doctor = user.doctor_profile
    data = request.get_json()
    avail_date = datetime.strptime(data['date'], '%Y-%m-%d').date()

    existing = DoctorAvailability.query.filter_by(
        doctor_id=doctor.id, date=avail_date).first()
    if existing:
        existing.start_time = data.get('start_time', existing.start_time)
        existing.end_time = data.get('end_time', existing.end_time)
        existing.max_appointments = data.get('max_appointments', existing.max_appointments)
        db.session.commit()
        return jsonify(existing.to_dict())
    else:
        avail = DoctorAvailability(
            doctor_id=doctor.id,
            date=avail_date,
            start_time=data.get('start_time', '09:00'),
            end_time=data.get('end_time', '17:00'),
            max_appointments=data.get('max_appointments', 10)
        )
        db.session.add(avail)
        db.session.commit()
        return jsonify(avail.to_dict()), 201

@doctor_bp.route('/availability/<int:avail_id>', methods=['DELETE'])
@doctor_required
def delete_availability(user, avail_id):
    doctor = user.doctor_profile
    avail = DoctorAvailability.query.filter_by(id=avail_id, doctor_id=doctor.id).first_or_404()
    db.session.delete(avail)
    db.session.commit()
    return jsonify({'message': 'Deleted'})

@doctor_bp.route('/profile', methods=['PUT'])
@doctor_required
def update_profile(user):
    doctor = user.doctor_profile
    data = request.get_json()
    doctor.full_name = data.get('full_name', doctor.full_name)
    doctor.phone = data.get('phone', doctor.phone)
    doctor.bio = data.get('bio', doctor.bio)
    doctor.experience_years = data.get('experience_years', doctor.experience_years)
    db.session.commit()
    return jsonify(doctor.to_dict())
