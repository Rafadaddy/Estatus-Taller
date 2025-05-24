from flask_login import UserMixin
from excel_db import ExcelUser, ExcelUnit, ExcelStatusChange, ExcelPartRequest, ExcelNotification
from datetime import datetime

class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data['id']
        self.username = user_data['username']
        self.email = user_data['email']
        self.password_hash = user_data['password_hash']
        self.department = user_data['department']
    
    @staticmethod
    def get_by_id(user_id):
        user_data = ExcelUser.get_by_id(int(user_id))
        if user_data:
            return User(user_data)
        return None
    
    @staticmethod
    def get_by_username(username):
        user_data = ExcelUser.get_by_username(username)
        if user_data:
            return User(user_data)
        return None
    
    @staticmethod
    def validate_login(username, password):
        success, user_data = ExcelUser.validate_login(username, password)
        if success and user_data:
            return True, User(user_data)
        return False, None
    
    @staticmethod
    def create(username, email, password, department):
        return ExcelUser.create(username, email, password, department)
    
    @staticmethod
    def get_all():
        users_data = ExcelUser.get_all()
        return [User(user_data) for user_data in users_data]


class Unit:
    def __init__(self, unit_data):
        self.id = unit_data['id']
        self.unit_number = unit_data['unit_number']
        self.description = unit_data['description']
        self.operator_name = unit_data['operator_name']
        self.current_status = unit_data['current_status']
        self.registered_by_id = unit_data['registered_by_id']
        self.created_at = unit_data['created_at']
        
        # Convertir created_at a datetime si es string
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
    
    @staticmethod
    def get_by_id(unit_id):
        unit_data = ExcelUnit.get_by_id(int(unit_id))
        if unit_data:
            return Unit(unit_data)
        return None
    
    @staticmethod
    def get_all():
        units_data = ExcelUnit.get_all()
        return [Unit(unit_data) for unit_data in units_data]
    
    @staticmethod
    def get_by_status(status):
        units_data = ExcelUnit.get_by_status(status)
        return [Unit(unit_data) for unit_data in units_data]
    
    @staticmethod
    def create(unit_number, description, operator_name, registered_by_id):
        return ExcelUnit.create(unit_number, description, operator_name, registered_by_id)
    
    def update_status(self, new_status, user_id, notes=None):
        return ExcelUnit.update_status(self.id, new_status, user_id, notes)
    
    def get_status_display(self):
        status_map = {
            'registered': 'Registrada',
            'in_workshop': 'En Taller',
            'waiting_parts': 'Esperando Repuestos',
            'completed': 'Completada',
            'received': 'Recibida por Control'
        }
        return status_map.get(self.current_status, self.current_status)
    
    def get_active_part_requests(self):
        all_requests = ExcelPartRequest.get_by_unit(self.id)
        return [part_req for part_req in all_requests if part_req['status'] != 'installed']
    
    def get_registered_by(self):
        return User.get_by_id(self.registered_by_id)


class StatusChange:
    def __init__(self, change_data):
        self.id = change_data['id']
        self.unit_id = change_data['unit_id']
        self.old_status = change_data['old_status']
        self.new_status = change_data['new_status']
        self.notes = change_data['notes']
        self.changed_by_id = change_data['changed_by_id']
        self.created_at = change_data['created_at']
        
        # Convertir created_at a datetime si es string
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
    
    @staticmethod
    def get_all():
        changes_data = ExcelStatusChange.get_all()
        return [StatusChange(change_data) for change_data in changes_data]
    
    @staticmethod
    def get_by_unit(unit_id):
        changes_data = ExcelStatusChange.get_by_unit(int(unit_id))
        return [StatusChange(change_data) for change_data in changes_data]
    
    def get_changed_by(self):
        return User.get_by_id(self.changed_by_id)
    
    def get_old_status_display(self):
        status_map = {
            'registered': 'Registrada',
            'in_workshop': 'En Taller',
            'waiting_parts': 'Esperando Repuestos',
            'completed': 'Completada',
            'received': 'Recibida por Control'
        }
        return status_map.get(self.old_status, self.old_status)
    
    def get_new_status_display(self):
        status_map = {
            'registered': 'Registrada',
            'in_workshop': 'En Taller',
            'waiting_parts': 'Esperando Repuestos',
            'completed': 'Completada',
            'received': 'Recibida por Control'
        }
        return status_map.get(self.new_status, self.new_status)


class PartRequest:
    def __init__(self, request_data):
        self.id = request_data['id']
        self.unit_id = request_data['unit_id']
        self.part_name = request_data['part_name']
        self.quantity = request_data['quantity']
        self.status = request_data['status']
        self.requested_by_id = request_data['requested_by_id']
        self.created_at = request_data['created_at']
        self.updated_at = request_data['updated_at']
        self.notes = request_data['notes']
        
        # Convertir created_at y updated_at a datetime si son strings
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.updated_at, str):
            self.updated_at = datetime.fromisoformat(self.updated_at)
    
    @staticmethod
    def get_by_id(request_id):
        request_data = ExcelPartRequest.get_by_id(int(request_id))
        if request_data:
            return PartRequest(request_data)
        return None
    
    @staticmethod
    def get_all():
        requests_data = ExcelPartRequest.get_all()
        return [PartRequest(request_data) for request_data in requests_data]
    
    @staticmethod
    def get_by_unit(unit_id):
        requests_data = ExcelPartRequest.get_by_unit(int(unit_id))
        return [PartRequest(request_data) for request_data in requests_data]
    
    @staticmethod
    def get_by_status(status):
        requests_data = ExcelPartRequest.get_by_status(status)
        return [PartRequest(request_data) for request_data in requests_data]
    
    @staticmethod
    def create(unit_id, part_name, quantity, user_id, notes=None):
        success, request_id = ExcelPartRequest.create(unit_id, part_name, quantity, user_id, notes)
        if success:
            # Crear notificación
            ExcelNotification.create_for_part_request(request_id)
        return success, request_id
    
    def update_status(self, new_status, notes=None):
        return ExcelPartRequest.update_status(self.id, new_status, notes)
    
    def get_requested_by(self):
        return User.get_by_id(self.requested_by_id)
    
    def get_unit(self):
        return Unit.get_by_id(self.unit_id)
    
    def get_status_display(self):
        status_map = {
            'pending': 'Pendiente',
            'available': 'Disponible',
            'installed': 'Instalada'
        }
        return status_map.get(self.status, self.status)


class Notification:
    def __init__(self, notification_data):
        self.id = notification_data['id']
        self.user_id = notification_data['user_id']
        self.message = notification_data['message']
        self.type = notification_data['type']
        self.reference_id = notification_data.get('reference_id')
        self.reference_type = notification_data.get('reference_type')
        self.is_read = notification_data['is_read']
        self.created_at = notification_data['created_at']
        
        # Convertir created_at a datetime si es string
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
    
    @staticmethod
    def get_by_id(notification_id):
        notification_data = ExcelNotification.get_by_id(int(notification_id))
        if notification_data:
            return Notification(notification_data)
        return None
    
    @staticmethod
    def get_by_user(user_id, limit=None, unread_only=False):
        notifications_data = ExcelNotification.get_by_user(int(user_id), limit, unread_only)
        return [Notification(notification_data) for notification_data in notifications_data]
    
    def mark_as_read(self):
        return ExcelNotification.mark_as_read(self.id)
    
    @staticmethod
    def mark_all_as_read(user_id):
        return ExcelNotification.mark_all_as_read(int(user_id))
    
    def get_url(self):
        """Genera una URL para navegar a la referencia de la notificación"""
        from flask import url_for
        
        if not self.reference_id or not self.reference_type:
            return "#"
        
        if self.reference_type == 'unit':
            return url_for('unit_details', unit_id=self.reference_id)
        elif self.reference_type == 'part_request':
            return url_for('manage_part_request', request_id=self.reference_id)
        
        return "#"
    
    @classmethod
    def create_for_status_change(cls, unit, old_status, new_status, user=None):
        return ExcelNotification.create_for_status_change(unit.id, old_status, new_status, 
                                                      user.id if user else None)
    
    @classmethod
    def create_for_unit_register(cls, unit, user=None):
        return ExcelNotification.create_for_unit_register(unit.id, 
                                                     user.id if user else None)
    
    @classmethod
    def create_for_part_request(cls, part_request, user=None):
        return ExcelNotification.create_for_part_request(part_request.id, 
                                                     user.id if user else None)

# Función para cargar un usuario para Flask-Login
def load_user(user_id):
    return User.get_by_id(user_id)