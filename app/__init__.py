from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from config import config

db = SQLAlchemy()


def create_app(config_name=None):
    """
    Application factory function
    
    Args:
        config_name (str): Configuration environment name
        
    Returns:
        Flask: Configured Flask application
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)

    app.config.from_object(config.get(config_name, config['default']))

    db.init_app(app)

    CORS(app, 
         origins=app.config['CORS_ORIGINS'],
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'])

    register_error_handlers(app)

    register_blueprints(app)

    with app.app_context():
        db.create_all()
    
    return app


def register_blueprints(app):
    """Register Flask blueprints"""
    from app.routes import auth_bp, admin_bp
    from app.routes.admin_auth import admin_auth_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(admin_auth_bp, url_prefix='/api/admin/auth')


def register_error_handlers(app):
    """Register error handlers"""
    from flask import jsonify
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request'}), 400
