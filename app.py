"""
Smart Attendance System - Flask Backend
Author: Generated for Production Use
"""

import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from models.database import db
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.teacher import teacher_bp
from routes.student import student_bp
from routes.attendance import attendance_bp
from routes.face import face_bp
from routes.geofence import geofence_bp

load_dotenv()

# Path to frontend folder (one level up from backend)
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend')

def create_app():
    app = Flask(__name__)

    # ─── Configuration ────────────────────────────────────────────────────────
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'smart-attendance-secret-2024')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-smart-attend-2024')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL', f"sqlite:///{os.path.join(os.path.dirname(__file__), 'attendance.db')}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.config['FACE_DATA_DIR'] = os.path.join(os.path.dirname(__file__), 'face_data')

    os.makedirs(app.config['FACE_DATA_DIR'], exist_ok=True)

    # ─── Extensions ───────────────────────────────────────────────────────────
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    JWTManager(app)
    db.init_app(app)

    # ─── Blueprints ───────────────────────────────────────────────────────────
    app.register_blueprint(auth_bp,       url_prefix='/api/auth')
    app.register_blueprint(admin_bp,      url_prefix='/api/admin')
    app.register_blueprint(teacher_bp,    url_prefix='/api/teacher')
    app.register_blueprint(student_bp,    url_prefix='/api/student')
    app.register_blueprint(attendance_bp, url_prefix='/api/attendance')
    app.register_blueprint(face_bp,       url_prefix='/api/face')
    app.register_blueprint(geofence_bp,   url_prefix='/api/geofence')

    # ─── Serve Frontend HTML ──────────────────────────────────────────────────
    @app.route('/')
    def serve_frontend():
        return send_from_directory(FRONTEND_DIR, 'index.html')

    # ─── Create Tables & Seed Admin ───────────────────────────────────────────
    with app.app_context():
        db.create_all()
        seed_default_admin()

    return app


def seed_default_admin():
    """Create default admin if not exists."""
    from models.user import User
    import bcrypt
    if not User.query.filter_by(role='admin').first():
        hashed = bcrypt.hashpw(b'admin@123', bcrypt.gensalt()).decode('utf-8')
        admin = User(
            name='System Administrator',
            email='admin@college.edu',
            password=hashed,
            role='admin',
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        print("[SEED] Default admin created: admin@college.edu / admin@123")


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
