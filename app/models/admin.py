from app import db
from datetime import datetime


class Admin(db.Model):
    """Admin model for admin portal"""
    
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    password_reset_token = db.Column(db.String(255), nullable=True, unique=True, index=True)
    password_reset_token_expiry = db.Column(db.DateTime, nullable=True, index=True)
    
    opportunities = db.relationship(
        'Opportunity',
        backref='admin',
        lazy='dynamic',
        cascade='all, delete-orphan',
        foreign_keys='Opportunity.admin_id'
    )
    
    def __repr__(self):
        return f'<Admin {self.id}: {self.email}>'
    
    def to_dict(self, include_opportunities=False):
        """
        Convert admin object to dictionary
        
        Args:
            include_opportunities (bool): Include related opportunities
            
        Returns:
            dict: Admin data as dictionary
        """
        data = {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_opportunities:
            data['opportunities'] = [
                opp.to_dict() for opp in self.opportunities.all()
            ]
        
        return data

    def set_password_reset_token(self, token, expiry):
        """Store a password reset token and its expiry."""
        self.password_reset_token = token
        self.password_reset_token_expiry = expiry

    def clear_password_reset_token(self):
        """Clear password reset token state."""
        self.password_reset_token = None
        self.password_reset_token_expiry = None
