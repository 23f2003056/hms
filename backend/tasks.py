from celery import Celery
from celery.schedules import crontab
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os, csv, io
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

def make_celery_app():
    celery = Celery('hms_tasks')
    celery.config_from_object({
        'broker_url': 'redis://localhost:6379/1',
        'result_backend': 'redis://localhost:6379/2',
        'beat_schedule': {
            'daily-reminders': {
                'task': 'backend.tasks.send_daily_reminders',
                'schedule': crontab(hour=8, minute=0),
            },
            'monthly-report': {
                'task': 'backend.tasks.send_monthly_reports',
                'schedule': crontab(day_of_month=1, hour=6, minute=0),
            }
        }
    })
    return celery

celery_app = make_celery_app()

def send_email(to_email, subject, body_html):
    smtp_user = os.environ.get('MAIL_USERNAME', '')
    smtp_pass = os.environ.get('MAIL_PASSWORD', '')
    if not smtp_user or not smtp_pass:
        print(f"[MOCK EMAIL] To: {to_email}\nSubject: {subject}\n{body_html[:200]}")
        return True
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = smtp_user
        msg['To'] = to_email
        msg.attach(MIMEText(body_html, 'html'))
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Email failed: {e}")
        return False

@celery_app.task(name='backend.tasks.send_daily_reminders')
def send_daily_reminders():
    from backend.app import create_app, db
    from backend.models import Appointment, Patient
    app = create_app()
    with app.app_context():
        today = date.today()
        appointments = Appointment.query.filter_by(date=today, status='Booked').all()
        for apt in appointments:
            patient = apt.patient
            if patient and patient.user and patient.user.email:
                body = f"""
                <h2>Hospital Appointment Reminder</h2>
                <p>Dear {patient.full_name},</p>
                <p>This is a reminder that you have an appointment today.</p>
                <ul>
                    <li><strong>Doctor:</strong> {apt.doctor.full_name}</li>
                    <li><strong>Time:</strong> {apt.time}</li>
                    <li><strong>Date:</strong> {apt.date}</li>
                </ul>
                <p>Please arrive 10 minutes early. Get well soon!</p>
                """
                send_email(patient.user.email, "Appointment Reminder - Today", body)
        print(f"Sent {len(appointments)} reminders for {today}")
        return len(appointments)

@celery_app.task(name='backend.tasks.send_monthly_reports')
def send_monthly_reports():
    from backend.app import create_app, db
    from backend.models import Appointment, Doctor
    app = create_app()
    with app.app_context():
        today = date.today()
        last_month_start = (today - relativedelta(months=1)).replace(day=1)
        last_month_end = today.replace(day=1)

        doctors = Doctor.query.all()
        for doctor in doctors:
            if not doctor.user or not doctor.user.email:
                continue
            apts = Appointment.query.filter_by(
                doctor_id=doctor.id, status='Completed'
            ).filter(
                Appointment.date >= last_month_start,
                Appointment.date < last_month_end
            ).all()

            rows = ""
            for apt in apts:
                t = apt.treatment
                rows += f"""
                <tr>
                    <td>{apt.date}</td>
                    <td>{apt.patient.full_name if apt.patient else 'N/A'}</td>
                    <td>{t.diagnosis if t else '-'}</td>
                    <td>{t.prescription if t else '-'}</td>
                </tr>"""

            body = f"""
            <html><body style="font-family:Arial;max-width:800px;margin:auto">
            <h2>Monthly Activity Report - {last_month_start.strftime('%B %Y')}</h2>
            <p>Dear Dr. {doctor.full_name},</p>
            <p>Here is your activity summary for {last_month_start.strftime('%B %Y')}.</p>
            <p><strong>Total Completed Appointments:</strong> {len(apts)}</p>
            <table border="1" cellpadding="8" cellspacing="0" style="width:100%;border-collapse:collapse">
                <thead style="background:#f0f0f0">
                    <tr><th>Date</th><th>Patient</th><th>Diagnosis</th><th>Prescription</th></tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>
            <p>Thank you for your service!</p>
            </body></html>"""

            send_email(doctor.user.email, f"Monthly Report - {last_month_start.strftime('%B %Y')}", body)
        return f"Sent reports to {len(doctors)} doctors"

@celery_app.task(name='backend.tasks.export_patient_csv')
def export_patient_csv(patient_id):
    from backend.app import create_app, db
    from backend.models import Appointment, Patient
    app = create_app()
    with app.app_context():
        patient = Patient.query.get(patient_id)
        apts = Appointment.query.filter_by(
            patient_id=patient_id, status='Completed'
        ).order_by(Appointment.date.desc()).all()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Patient ID', 'Patient Name', 'Doctor', 'Date', 'Diagnosis', 'Prescription', 'Notes', 'Next Visit'])

        for apt in apts:
            t = apt.treatment
            writer.writerow([
                patient.id,
                patient.full_name,
                apt.doctor.full_name if apt.doctor else '',
                apt.date.isoformat(),
                t.diagnosis if t else '',
                t.prescription if t else '',
                t.notes if t else '',
                t.next_visit.isoformat() if t and t.next_visit else ''
            ])

        csv_content = output.getvalue()
        if patient.user and patient.user.email:
            body = f"""
            <h3>Your Treatment History Export</h3>
            <p>Dear {patient.full_name}, your treatment history CSV is ready.</p>
            <pre style="background:#f5f5f5;padding:15px;border-radius:5px">{csv_content[:2000]}</pre>
            """
            send_email(patient.user.email, "Your Treatment History Export", body)

        return csv_content
