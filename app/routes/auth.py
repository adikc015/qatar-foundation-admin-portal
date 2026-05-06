from flask import request, jsonify
from app.routes import auth_bp
from app import db
from app.models import User
from app.utils.helpers import hash_password, verify_password
from datetime import datetime


@auth_bp.route('/register', methods=['POST'])
def register():
    """User registration endpoint"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing required fields'}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 409
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 409
    
    try:
        user = User(
            username=data['username'],
            email=data['email'],
            password_hash=hash_password(data['password']),
            full_name=data.get('full_name', ''),
            role=data.get('role', 'user')
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User created successfully',
            'user': user.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Missing username or password'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not verify_password(data['password'], user.password_hash):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'User account is inactive'}), 403
    
    try:
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """User logout endpoint"""
    return jsonify({'message': 'Logout successful'}), 200


@auth_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'auth'}), 200
