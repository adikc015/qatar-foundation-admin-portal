import hashlib
import secrets
from functools import wraps
from flask import jsonify, request


def hash_password(password):
    """
    Hash password using SHA256 with salt
    
    Args:
        password (str): Plain text password
        
    Returns:
        str: Hashed password with salt
    """
    salt = secrets.token_hex(16)
    hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}${hash_obj.hex()}"


def verify_password(password, hash_with_salt):
    """
    Verify password against hash
    
    Args:
        password (str): Plain text password to verify
        hash_with_salt (str): Stored hash with salt
        
    Returns:
        bool: True if password matches, False otherwise
    """
    try:
        salt, hash_value = hash_with_salt.split('$')
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return hash_obj.hex() == hash_value
    except (ValueError, AttributeError):
        return False


def require_auth(f):
    """
    Decorator to require authentication
    
    Args:
        f: Function to decorate
        
    Returns:
        Decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'Missing authorization header'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function
