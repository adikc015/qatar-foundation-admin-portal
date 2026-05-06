from app import db
from datetime import datetime


class Opportunity(db.Model):
    """Opportunity model for admin portal"""
    
    __tablename__ = 'opportunities'
    
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.id', ondelete='CASCADE'), nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    duration = db.Column(db.String(100), nullable=False)  # e.g., "3 months", "6 weeks"
    start_date = db.Column(db.DateTime, nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    skills = db.Column(db.String(500), nullable=True)  # Comma-separated values
    category = db.Column(db.String(100), nullable=False, index=True)
    future_opportunities = db.Column(db.Boolean, default=False, nullable=False)
    max_applicants = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f'<Opportunity {self.id}: {self.name} (Admin: {self.admin_id})>'
    
    def to_dict(self, include_admin=False):
        """
        Convert opportunity object to dictionary
        
        Args:
            include_admin (bool): Include related admin info
            
        Returns:
            dict: Opportunity data as dictionary
        """
        data = {
            'id': self.id,
            'admin_id': self.admin_id,
            'name': self.name,
            'duration': self.duration,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'description': self.description,
            'skills': self.skills.split(',') if self.skills else [],
            'category': self.category,
            'future_opportunities': self.future_opportunities,
            'max_applicants': self.max_applicants,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_admin and self.admin:
            data['admin'] = {
                'id': self.admin.id,
                'full_name': self.admin.full_name,
                'email': self.admin.email
            }
        
        return data
    
    def get_skills_list(self):
        """
        Get skills as a list instead of comma-separated string
        
        Returns:
            list: List of skills
        """
        if not self.skills:
            return []
        return [skill.strip() for skill in self.skills.split(',')]
    
    def set_skills_list(self, skills_list):
        """
        Set skills from a list
        
        Args:
            skills_list (list): List of skills
        """
        if skills_list:
            self.skills = ','.join([str(skill).strip() for skill in skills_list])
        else:
            self.skills = None
