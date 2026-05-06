"""
Validation utilities for form data
"""
import re
from email_validator import validate_email, EmailNotValidError


def validate_email_format(email):
    """
    Validate email format using email-validator library
    
    Args:
        email (str): Email address to validate
        
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    if not email or not isinstance(email, str):
        return False, "Email is required"
    
    email = email.strip().lower()
    
    try:
        valid = validate_email(email)
        return True, None
    except EmailNotValidError as e:
        return False, f"Invalid email format: {str(e)}"


def validate_password(password, confirm_password=None, min_length=8):
    """
    Validate password strength
    
    Args:
        password (str): Password to validate
        confirm_password (str): Confirmation password (optional)
        min_length (int): Minimum password length
        
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    if not password or not isinstance(password, str):
        return False, "Password is required"
    
    if len(password) < min_length:
        return False, f"Password must be at least {min_length} characters long"
    
    if confirm_password is not None:
        if password != confirm_password:
            return False, "Passwords do not match"
    
    return True, None


def validate_full_name(full_name, min_length=2):
    """
    Validate full name
    
    Args:
        full_name (str): Full name to validate
        min_length (int): Minimum name length
        
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    if not full_name or not isinstance(full_name, str):
        return False, "Full name is required"
    
    full_name = full_name.strip()
    
    if len(full_name) < min_length:
        return False, f"Full name must be at least {min_length} characters long"
    
    if not re.match(r"^[a-zA-Z\s\-']+$", full_name):
        return False, "Full name can only contain letters, spaces, hyphens, and apostrophes"
    
    return True, None


def validate_required_fields(data, required_fields):
    """
    Validate that all required fields are present in data
    
    Args:
        data (dict): Data dictionary to validate
        required_fields (list): List of required field names
        
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
    if not data:
        return False, "Request body is required"
    
    missing_fields = [field for field in required_fields if not data.get(field)]
    
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    
    return True, None


def sanitize_email(email):
    """
    Sanitize email address
    
    Args:
        email (str): Email to sanitize
        
    Returns:
        str: Sanitized email
    """
    return email.strip().lower() if email else None


def sanitize_string(value):
    """
    Sanitize string input
    
    Args:
        value (str): String to sanitize
        
    Returns:
        str: Sanitized string
    """
    return value.strip() if isinstance(value, str) else None
