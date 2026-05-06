from flask import Blueprint

auth_bp = Blueprint('auth', __name__)
admin_bp = Blueprint('admin', __name__)

from app.routes import auth, admin, admin_auth
