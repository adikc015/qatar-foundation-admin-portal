import re
from email_validator import validate_email, EmailNotValidError


def validate_email_format(email):
    if not email or not isinstance(email, str):
        return False, "Email is required"
    
    email = email.strip().lower()
    
    try:
        valid = validate_email(email)
        return True, None
    except EmailNotValidError as e:
        return False, f"Invalid email format: {str(e)}"


def validate_password(password, confirm_password=None, min_length=8):
    if not password or not isinstance(password, str):
        return False, "Password is required"
    
    if len(password) < min_length:
        return False, f"Password must be at least {min_length} characters long"
    
    if confirm_password is not None:
        if password != confirm_password:
            return False, "Passwords do not match"
    
    return True, None


def validate_full_name(full_name, min_length=2):
    if not full_name or not isinstance(full_name, str):
        return False, "Full name is required"
    
    full_name = full_name.strip()
    
    if len(full_name) < min_length:
        return False, f"Full name must be at least {min_length} characters long"
    
    if not re.match(r"^[a-zA-Z\s\-']+$", full_name):
        return False, "Full name can only contain letters, spaces, hyphens, and apostrophes"
    
    return True, None


def validate_required_fields(data, required_fields):
    if not data:
        return False, "Request body is required"
    
    missing_fields = [field for field in required_fields if not data.get(field)]
    
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    
    return True, None


def sanitize_email(email):
    return email.strip().lower() if email else None


def sanitize_string(value):
    return value.strip() if isinstance(value, str) else None
