from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin
import json

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
            'completed': 'Completada',
            'received': 'Recibida por Control'
        }
        return status_map.get(self.current_status, self.current_status.title())
    
    def get_active_part_requests(self):
        return PartRequest.query.filter_by(unit_id=self.id, status='pending').all()
        
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 'status_change', 'unit_register', 'part_request', etc.
    reference_id = db.Column(db.Integer, nullable=True)  # ID de la unidad, pieza, etc.
    reference_type = db.Column(db.String(50), nullable=True)  # 'unit', 'part_request', etc.
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con el usuario
    user = db.relationship('User', backref='notifications')
    
    def __repr__(self):
        return f'<Notification {self.id} - {self.type}>'
    
    def mark_as_read(self):
        self.is_read = True
        db.session.commit()
    
    def get_url(self):
        """Genera una URL para navegar a la referencia de la notificación"""
        if self.reference_type == 'unit' and self.reference_id:
            return f'/unit_history/{self.reference_id}'
        elif self.reference_type == 'part_request' and self.reference_id:
            return f'/manage_part_request/{self.reference_id}'
        return '#'
    
    @classmethod
    def create_for_status_change(cls, unit, old_status, new_status, user=None):
        """Crea notificaciones para un cambio de estado de unidad"""
        # Determinar a qué departamentos notificar basado en el nuevo estado
        departments_to_notify = []
        if new_status == 'registered':
            departments_to_notify = ['workshop', 'admin']
        elif new_status in ['in_workshop', 'waiting_parts', 'completed']:
            departments_to_notify = ['traffic_control', 'admin']
            if new_status == 'waiting_parts':
                departments_to_notify.append('warehouse')
        elif new_status == 'received':
            departments_to_notify = ['workshop', 'admin']
        
        # Crear mensaje
        status_map = {
            'registered': 'Registrada',
            'in_workshop': 'En Taller',
            'waiting_parts': 'Esperando Repuestos',
            'completed': 'Completada',
            'received': 'Recibida por Control'
        }
        old_status_display = status_map.get(old_status, old_status.title())
        new_status_display = status_map.get(new_status, new_status.title())
        
        username = user.username if user else "Sistema"
        dept = ""
        if user:
            dept_map = {
                'traffic_control': 'Control de Tráfico',
                'workshop': 'Taller',
                'warehouse': 'Almacén',
                'admin': 'Administrador'
            }
            dept = dept_map.get(user.department, user.department)
        
        message = f'La unidad {unit.unit_number} ha cambiado de estado: {old_status_display} → {new_status_display} por {username} ({dept})'
        
        # Crear notificaciones para cada usuario de los departamentos seleccionados
        users = User.query.filter(User.department.in_(departments_to_notify)).all()
        notifications = []
        
        for target_user in users:
            if user and target_user.id == user.id:
                continue  # No notificar al usuario que hizo el cambio
                
            notification = cls(
                user_id=target_user.id,
                message=message,
                type='status_change',
                reference_id=unit.id,
                reference_type='unit'
            )
            db.session.add(notification)
            notifications.append(notification)
        
        db.session.commit()
        return notifications
    
    @classmethod
    def create_for_unit_register(cls, unit, user=None):
        """Crea notificaciones para el registro de una nueva unidad"""
        message = f'Nueva unidad registrada: {unit.unit_number} - {unit.operator_name}'
        
        # Notificar a todos los usuarios del taller y admin
        users = User.query.filter(User.department.in_(['workshop', 'admin'])).all()
        notifications = []
        
        for target_user in users:
            if user and target_user.id == user.id:
                continue
                
            notification = cls(
                user_id=target_user.id,
                message=message,
                type='unit_register',
                reference_id=unit.id,
                reference_type='unit'
            )
            db.session.add(notification)
            notifications.append(notification)
        
        db.session.commit()
        return notifications
    
    @classmethod
    def create_for_part_request(cls, part_request, user=None):
        """Crea notificaciones para solicitudes de piezas"""
        unit = Unit.query.get(part_request.unit_id)
        
        username = user.username if user else "Sistema"
        dept = ""
        if user:
            dept_map = {
                'traffic_control': 'Control de Tráfico',
                'workshop': 'Taller',
                'warehouse': 'Almacén',
                'admin': 'Administrador'
            }
            dept = dept_map.get(user.department, user.department)
        
        message = f'Nueva solicitud de pieza: {part_request.part_name} (cant. {part_request.quantity}) para unidad {unit.unit_number} por {username} ({dept})'
        
        # Notificar a todos los usuarios del almacén y admin
        users = User.query.filter(User.department.in_(['warehouse', 'admin'])).all()
        notifications = []
        
        for target_user in users:
            if user and target_user.id == user.id:
                continue
                
            notification = cls(
                user_id=target_user.id,
                message=message,
                type='part_request',
                reference_id=part_request.id,
                reference_type='part_request'
            )
            db.session.add(notification)
            notifications.append(notification)
        
        db.session.commit()
        return notifications

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
