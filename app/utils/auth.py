from functools import wraps

import bcrypt
from flask import jsonify, session, g


def hash_password(password):
    if not password or not isinstance(password, str):
        raise ValueError("Password must be a non-empty string")
    
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    return hashed.decode('utf-8')


def verify_password(password, hashed_password):
    try:
        if not password or not hashed_password:
            return False
        
        return bcrypt.checkpw(
            password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except (ValueError, TypeError):
        return False


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        admin_id = session.get('admin_id')
        if not admin_id:
            return jsonify({'error': 'Unauthorized'}), 401

        g.admin_id = admin_id
        g.admin_email = session.get('admin_email')
        g.admin_full_name = session.get('admin_full_name')
        g.remember_me = session.get('remember_me', False)
        return f(*args, **kwargs)

    return decorated_function
