"""
Admin authentication routes
"""
import secrets
from datetime import datetime, timedelta

from flask import request, jsonify, Blueprint, session, current_app
from app import db
from app.models import Admin
from app.utils.validators import (
    validate_required_fields,
    validate_full_name,
    validate_email_format,
    validate_password,
    sanitize_email,
    sanitize_string
)
from app.utils.auth import hash_password, verify_password


admin_auth_bp = Blueprint('admin_auth', __name__)


@admin_auth_bp.route('/signup', methods=['POST'])
def admin_signup():
    """
    Admin signup endpoint
    
    Request body:
    {
        "full_name": "John Doe",
        "email": "john@example.com",
        "password": "SecurePass123",
        "confirm_password": "SecurePass123"
    }
    
    Returns:
        JSON response with success or error message
    """
    data = request.get_json()
    
    
    required_fields = ['full_name', 'email', 'password', 'confirm_password']
    is_valid, error_msg = validate_required_fields(data, required_fields)
    if not is_valid:
        return jsonify({'error': error_msg}), 400
    
    full_name = sanitize_string(data.get('full_name'))
    email = sanitize_email(data.get('email'))
    password = data.get('password')
    confirm_password = data.get('confirm_password')
    
    is_valid, error_msg = validate_full_name(full_name)
    if not is_valid:
        return jsonify({'error': error_msg}), 400
    
    is_valid, error_msg = validate_password(password, confirm_password, min_length=8)
    if not is_valid:
        return jsonify({'error': error_msg}), 400
    
    is_valid, error_msg = validate_email_format(email)
    if not is_valid:
        return jsonify({'error': error_msg}), 400
    
    existing_admin = Admin.query.filter_by(email=email).first()
    if existing_admin:
        return jsonify({'error': 'Email already registered'}), 409
    
    
    try:
        password_hash = hash_password(password)
        
        new_admin = Admin(
            full_name=full_name,
            email=email,
            password=password_hash
        )
        
        db.session.add(new_admin)
        db.session.commit()
        
        return jsonify({
            'message': 'Admin account created successfully',
            'admin': {
                'id': new_admin.id,
                'full_name': new_admin.full_name,
                'email': new_admin.email,
                'created_at': new_admin.created_at.isoformat()
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create admin account: {str(e)}'}), 500


@admin_auth_bp.route('/login', methods=['POST'])
def admin_login():
    """
    Admin login endpoint

    Request body:
    {
        "email": "john@example.com",
        "password": "SecurePass123",
        "remember_me": true
    }

    Returns:
        JSON response with success or error message
    """
    data = request.get_json()

    required_fields = ['email', 'password']
    is_valid, error_msg = validate_required_fields(data, required_fields)
    if not is_valid:
        return jsonify({'error': 'Invalid email or password'}), 401

    email = sanitize_email(data.get('email'))
    password = data.get('password')
    remember_me = bool(data.get('remember_me', False))

    admin = Admin.query.filter_by(email=email).first()
    if not admin or not verify_password(password, admin.password):
        return jsonify({'error': 'Invalid email or password'}), 401

    session.clear()
    session['admin_id'] = admin.id
    session['admin_email'] = admin.email
    session['admin_full_name'] = admin.full_name
    session['remember_me'] = remember_me
    session.permanent = True
    current_app.permanent_session_lifetime = (
        current_app.config['REMEMBER_ME_SESSION_LIFETIME']
        if remember_me
        else current_app.config['PERMANENT_SESSION_LIFETIME']
    )

    return jsonify({
        'message': 'Login successful',
        'admin': {
            'id': admin.id,
            'full_name': admin.full_name,
            'email': admin.email,
            'created_at': admin.created_at.isoformat() if admin.created_at else None
        },
        'session': {
            'admin_id': session['admin_id'],
            'remember_me': remember_me
        }
    }), 200


@admin_auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """
    Request a password reset token.

    Always returns a success message to avoid account enumeration.
    """
    data = request.get_json()
    email = sanitize_email(data.get('email')) if data else None

    if email:
        admin = Admin.query.filter_by(email=email).first()
        if admin:
            token = secrets.token_urlsafe(32)
            admin.set_password_reset_token(token, datetime.utcnow() + timedelta(hours=1))
            db.session.commit()

    return jsonify({
        'message': 'If the email exists, a password reset link has been sent.'
    }), 200


@admin_auth_bp.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    """
    Reset password using a secure token.
    """
    data = request.get_json()
    new_password = data.get('new_password') if data else None
    confirm_password = data.get('confirm_password') if data else None

    if not new_password or not confirm_password:
        return jsonify({'error': 'new_password and confirm_password are required'}), 400

    is_valid, error_msg = validate_password(new_password, confirm_password, min_length=8)
    if not is_valid:
        return jsonify({'error': error_msg}), 400

    admin = Admin.query.filter_by(password_reset_token=token).first()
    if not admin:
        return jsonify({'error': 'Invalid or expired token'}), 400

    if not admin.password_reset_token_expiry or admin.password_reset_token_expiry < datetime.utcnow():
        return jsonify({'error': 'Invalid or expired token'}), 400

    try:
        admin.password = hash_password(new_password)
        admin.clear_password_reset_token()
        db.session.commit()
        return jsonify({'message': 'Password has been reset successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to reset password: {str(e)}'}), 500


@admin_auth_bp.route('/health', methods=['GET'])
def admin_auth_health():
    """Health check endpoint for admin auth service"""
    return jsonify({
        'status': 'healthy',
        'service': 'admin-auth'
    }), 200
