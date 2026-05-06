from datetime import datetime

from flask import request, jsonify, session
from app.routes import admin_bp
from app import db
from app.models import User, Opportunity
from app.utils.auth import login_required


ALLOWED_CATEGORIES = {
    'Technology',
    'Business',
    'Design',
    'Marketing',
    'Data Science',
    'Other'
}


def _parse_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {'true', '1', 'yes', 'on'}:
            return True
        if normalized in {'false', '0', 'no', 'off'}:
            return False
    return bool(value)


@admin_bp.route('/users', methods=['GET'])
@login_required
def get_users():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        pagination = User.query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'users': [user.to_dict() for user in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify(user.to_dict()), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    data = request.get_json()
    
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if 'full_name' in data:
            user.full_name = data['full_name']
        if 'email' in data:
            user.email = data['email']
        if 'role' in data:
            user.role = data['role']
        if 'is_active' in data:
            user.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'User deleted successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard_stats():
    try:
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        admin_users = User.query.filter_by(role='admin').count()
        
        return jsonify({
            'total_users': total_users,
            'active_users': active_users,
            'admin_users': admin_users,
            'inactive_users': total_users - active_users
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/opportunities', methods=['GET'])
@login_required
def get_admin_opportunities():
    try:
        admin_id = session.get('admin_id')
        opportunities = (
            Opportunity.query
            .filter_by(admin_id=admin_id)
            .order_by(Opportunity.created_at.desc())
            .all()
        )

        if not opportunities:
            return jsonify({
                'message': 'No opportunities found for this admin',
                'opportunities': []
            }), 200

        return jsonify({
            'message': 'Opportunities fetched successfully',
            'opportunities': [opportunity.to_dict() for opportunity in opportunities]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/opportunities', methods=['POST'])
@login_required
def create_admin_opportunity():
    data = request.get_json() or {}

    required_fields = ['name', 'duration', 'start_date', 'description', 'skills', 'category', 'future_opportunities']
    missing_fields = [field for field in required_fields if data.get(field) in (None, '')]
    if missing_fields:
        return jsonify({'error': f"Missing required fields: {', '.join(missing_fields)}"}), 400

    category = str(data.get('category')).strip()
    if category not in ALLOWED_CATEGORIES:
        return jsonify({
            'error': f"Invalid category. Allowed values are: {', '.join(sorted(ALLOWED_CATEGORIES))}"
        }), 400

    try:
        start_date_value = str(data.get('start_date')).strip()
        try:
            start_date = datetime.fromisoformat(start_date_value)
        except ValueError:
            start_date = datetime.strptime(start_date_value, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Invalid start_date format. Use YYYY-MM-DD or ISO datetime format.'}), 400

    skills_value = data.get('skills')
    if isinstance(skills_value, list):
        skills = ','.join([str(skill).strip() for skill in skills_value if str(skill).strip()])
    else:
        skills = ','.join([skill.strip() for skill in str(skills_value).split(',') if skill.strip()])

    if not skills:
        return jsonify({'error': 'skills cannot be empty'}), 400

    max_applicants = data.get('max_applicants')
    if max_applicants in ('', None):
        max_applicants = None
    else:
        try:
            max_applicants = int(max_applicants)
        except (TypeError, ValueError):
            return jsonify({'error': 'max_applicants must be an integer'}), 400

    try:
        opportunity = Opportunity(
            admin_id=session.get('admin_id'),
            name=str(data.get('name')).strip(),
            duration=str(data.get('duration')).strip(),
            start_date=start_date,
            description=str(data.get('description')).strip(),
            skills=skills,
            category=category,
            future_opportunities=_parse_bool(data.get('future_opportunities')),
            max_applicants=max_applicants
        )

        db.session.add(opportunity)
        db.session.commit()

        return jsonify({
            'message': 'Opportunity created successfully',
            'opportunity': opportunity.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create opportunity: {str(e)}'}), 500


@admin_bp.route('/opportunities/<int:opportunity_id>', methods=['PUT'])
@login_required
def update_admin_opportunity(opportunity_id):
    data = request.get_json() or {}

    try:
        admin_id = session.get('admin_id')
        opportunity = Opportunity.query.filter_by(id=opportunity_id, admin_id=admin_id).first()

        if not opportunity:
            return jsonify({'error': 'Opportunity not found'}), 404

        updated_name = str(data.get('name', opportunity.name)).strip()
        updated_duration = str(data.get('duration', opportunity.duration)).strip()
        updated_description = str(data.get('description', opportunity.description)).strip()
        updated_category = str(data.get('category', opportunity.category)).strip()
        updated_future_opportunities = _parse_bool(
            data.get('future_opportunities', opportunity.future_opportunities)
        )

        if updated_category not in ALLOWED_CATEGORIES:
            return jsonify({
                'error': f"Invalid category. Allowed values are: {', '.join(sorted(ALLOWED_CATEGORIES))}"
            }), 400

        if 'start_date' in data and data.get('start_date') not in (None, ''):
            start_date_value = str(data.get('start_date')).strip()
            try:
                updated_start_date = datetime.fromisoformat(start_date_value)
            except ValueError:
                try:
                    updated_start_date = datetime.strptime(start_date_value, '%Y-%m-%d')
                except ValueError:
                    return jsonify({'error': 'Invalid start_date format. Use YYYY-MM-DD or ISO datetime format.'}), 400
        else:
            updated_start_date = opportunity.start_date

        if 'skills' in data:
            skills_value = data.get('skills')
            if isinstance(skills_value, list):
                updated_skills = ','.join([str(skill).strip() for skill in skills_value if str(skill).strip()])
            else:
                updated_skills = ','.join([skill.strip() for skill in str(skills_value).split(',') if skill.strip()])
        else:
            updated_skills = opportunity.skills

        if not updated_name or not updated_duration or not updated_description or not updated_skills:
            return jsonify({'error': 'Missing required fields'}), 400

        if 'max_applicants' in data:
            max_applicants = data.get('max_applicants')
            if max_applicants in ('', None):
                updated_max_applicants = None
            else:
                try:
                    updated_max_applicants = int(max_applicants)
                except (TypeError, ValueError):
                    return jsonify({'error': 'max_applicants must be an integer'}), 400
        else:
            updated_max_applicants = opportunity.max_applicants

        opportunity.name = updated_name
        opportunity.duration = updated_duration
        opportunity.start_date = updated_start_date
        opportunity.description = updated_description
        opportunity.skills = updated_skills
        opportunity.category = updated_category
        opportunity.future_opportunities = updated_future_opportunities
        opportunity.max_applicants = updated_max_applicants

        db.session.commit()

        return jsonify({
            'message': 'Opportunity updated successfully',
            'opportunity': opportunity.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update opportunity: {str(e)}'}), 500


@admin_bp.route('/opportunities/<int:opportunity_id>', methods=['DELETE'])
@login_required
def delete_admin_opportunity(opportunity_id):
    try:
        admin_id = session.get('admin_id')
        opportunity = Opportunity.query.filter_by(id=opportunity_id, admin_id=admin_id).first()

        if not opportunity:
            return jsonify({'error': 'Opportunity not found'}), 404

        db.session.delete(opportunity)
        db.session.commit()

        return jsonify({'message': 'Opportunity deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete opportunity: {str(e)}'}), 500


@admin_bp.route('/opportunities/<int:opportunity_id>', methods=['GET'])
@login_required
def get_admin_opportunity(opportunity_id):
    try:
        admin_id = session.get('admin_id')
        opportunity = Opportunity.query.filter_by(id=opportunity_id, admin_id=admin_id).first()

        if not opportunity:
            return jsonify({'error': 'Opportunity not found'}), 404

        return jsonify({
            'message': 'Opportunity fetched successfully',
            'opportunity': opportunity.to_dict()
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
