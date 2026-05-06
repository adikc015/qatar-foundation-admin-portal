import os
from app import create_app, db


app = create_app(os.environ.get('FLASK_ENV', 'development'))


@app.shell_context_processor
def make_shell_context():
    return {'db': db}


@app.route('/health', methods=['GET'])
def health_check():
    from flask import jsonify
    return jsonify({
        'status': 'healthy',
        'service': 'admin-portal-backend',
        'environment': os.environ.get('FLASK_ENV', 'development')
    }), 200


@app.route('/', methods=['GET'])
def index():
    from flask import jsonify
    return jsonify({
        'message': 'Admin Portal API',
        'version': '1.0.0',
        'endpoints': {
            'auth': '/api/auth',
            'admin': '/api/admin',
            'health': '/health'
        }
    }), 200


if __name__ == '__main__':
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'true').lower() == 'true'

    app.run(host=host, port=port, debug=debug)
