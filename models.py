from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    department = db.Column(db.String(50), nullable=False)  # 'traffic_control', 'workshop', 'warehouse', 'admin'
    
    # Activities performed by this user
    registrations = db.relationship('Unit', backref='registered_by', foreign_keys='Unit.registered_by_id')
    status_changes = db.relationship('StatusChange', backref='changed_by')
    parts_requests = db.relationship('PartRequest', backref='requested_by')
    
    def __repr__(self):
        return f'<User {self.username}>'

class Unit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unit_number = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    operator_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    current_status = db.Column(db.String(50), default='registered')  # registered, in_workshop, waiting_parts, completed
    
    # User who registered the unit
    registered_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    status_changes = db.relationship('StatusChange', backref='unit', lazy='dynamic')
    part_requests = db.relationship('PartRequest', backref='unit', lazy='dynamic')
    
    def __repr__(self):
        return f'<Unit {self.unit_number}>'
    
    def get_status_display(self):
        status_map = {
            'registered': 'Registrada',
            'in_workshop': 'En Taller',
            'waiting_parts': 'Esperando Repuestos',
            'completed': 'Completada'
        }
        return status_map.get(self.current_status, self.current_status.title())
    
    def get_active_part_requests(self):
        return PartRequest.query.filter_by(unit_id=self.id, status='pending').all()

class StatusChange(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'), nullable=False)
    old_status = db.Column(db.String(50), nullable=False)
    new_status = db.Column(db.String(50), nullable=False)
    notes = db.Column(db.Text)
    changed_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<StatusChange {self.old_status} → {self.new_status}>'

class PartRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'), nullable=False)
    part_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    status = db.Column(db.String(50), default='pending')  # pending, available, installed
    requested_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = db.Column(db.Text)
    
    def __repr__(self):
        return f'<PartRequest {self.part_name}>'
    
    def get_status_display(self):
        status_map = {
            'pending': 'Pendiente',
            'available': 'Disponible',
            'installed': 'Instalada'
        }
        return status_map.get(self.status, self.status.title())
