from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_caching import Cache
from celery import Celery
import os

db = SQLAlchemy()
jwt = JWTManager()
cache = Cache()

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery.Task = ContextTask
    return celery

def create_app():
    app = Flask(__name__, static_folder='../frontend/dist', static_url_path='/')
    app.config['SECRET_KEY'] = 'hms-secret-key-2024'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../instance/hms.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'jwt-secret-hms-2024'
    app.config['CACHE_TYPE'] = 'RedisCache'
    app.config['CACHE_REDIS_URL'] = 'redis://localhost:6379/0'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300
    app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/1'
    app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/2'
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')

    db.init_app(app)
    jwt.init_app(app)
    cache.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    from .routes.auth import auth_bp
    from .routes.admin import admin_bp
    from .routes.doctor import doctor_bp
    from .routes.patient import patient_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(doctor_bp, url_prefix='/api/doctor')
    app.register_blueprint(patient_bp, url_prefix='/api/patient')

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        from flask import send_from_directory
        if path and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, 'index.html')

    with app.app_context():
        db.create_all()
        from .models import seed_admin
        seed_admin()

    return app
