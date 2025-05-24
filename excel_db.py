import os
import pandas as pd
import numpy as np
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json
import uuid

# Definir la ruta del archivo Excel
DB_FILE = 'workshop_database.xlsx'

# Asegurar que el archivo Excel existe
def init_excel_db():
    """Inicializa la base de datos Excel si no existe"""
    if not os.path.exists(DB_FILE):
        # Crear DataFrame vacíos para cada tabla
        users_df = pd.DataFrame(columns=[
            'id', 'username', 'email', 'password_hash', 'department', 'created_at'
        ])
        
        units_df = pd.DataFrame(columns=[
            'id', 'unit_number', 'description', 'operator_name', 'current_status',
            'registered_by_id', 'created_at'
        ])
        
        status_changes_df = pd.DataFrame(columns=[
            'id', 'unit_id', 'old_status', 'new_status', 'notes',
            'changed_by_id', 'created_at'
        ])
        
        part_requests_df = pd.DataFrame(columns=[
            'id', 'unit_id', 'part_name', 'quantity', 'status',
            'requested_by_id', 'created_at', 'updated_at', 'notes'
        ])
        
        notifications_df = pd.DataFrame(columns=[
            'id', 'user_id', 'message', 'type', 'reference_id',
            'reference_type', 'is_read', 'created_at'
        ])
        
        # Crear un administrador por defecto
        admin_id = 1
        users_df = users_df.append({
            'id': admin_id,
            'username': 'admin',
            'email': 'admin@example.com',
            'password_hash': generate_password_hash('admin'),
            'department': 'admin',
            'created_at': datetime.now().isoformat()
        }, ignore_index=True)
        
        # Guardar en Excel
        with pd.ExcelWriter(DB_FILE, engine='openpyxl') as writer:
            users_df.to_excel(writer, sheet_name='users', index=False)
            units_df.to_excel(writer, sheet_name='units', index=False)
            status_changes_df.to_excel(writer, sheet_name='status_changes', index=False)
            part_requests_df.to_excel(writer, sheet_name='part_requests', index=False)
            notifications_df.to_excel(writer, sheet_name='notifications', index=False)
            
        print(f"Base de datos Excel creada en {DB_FILE}")
    else:
        print(f"Base de datos Excel ya existe en {DB_FILE}")

# Funciones para trabajar con cada entidad
class ExcelUser:
    @staticmethod
    def get_all():
        """Obtiene todos los usuarios"""
        init_excel_db()
        df = pd.read_excel(DB_FILE, sheet_name='users')
        return df.to_dict('records')
    
    @staticmethod
    def get_by_id(user_id):
        """Obtiene un usuario por su ID"""
        init_excel_db()
        df = pd.read_excel(DB_FILE, sheet_name='users')
        user = df[df['id'] == user_id]
        if user.empty:
            return None
        return user.iloc[0].to_dict()
    
    @staticmethod
    def get_by_username(username):
        """Obtiene un usuario por su nombre de usuario"""
        init_excel_db()
        df = pd.read_excel(DB_FILE, sheet_name='users')
        user = df[df['username'] == username]
        if user.empty:
            return None
        return user.iloc[0].to_dict()
    
    @staticmethod
    def get_by_email(email):
        """Obtiene un usuario por su correo electrónico"""
        init_excel_db()
        df = pd.read_excel(DB_FILE, sheet_name='users')
        user = df[df['email'] == email]
        if user.empty:
            return None
        return user.iloc[0].to_dict()
    
    @staticmethod
    def create(username, email, password, department):
        """Crea un nuevo usuario"""
        init_excel_db()
        df = pd.read_excel(DB_FILE, sheet_name='users')
        
        # Verificar si el usuario ya existe
        if not df[df['username'] == username].empty:
            return False, "El nombre de usuario ya está en uso"
        if not df[df['email'] == email].empty:
            return False, "El correo electrónico ya está en uso"
        
        # Generar ID (el máximo + 1)
        new_id = 1
        if not df.empty:
            new_id = df['id'].max() + 1
        
        # Añadir nuevo usuario
        new_user = {
            'id': new_id,
            'username': username,
            'email': email,
            'password_hash': generate_password_hash(password),
            'department': department,
            'created_at': datetime.now().isoformat()
        }
        
        df = df.append(new_user, ignore_index=True)
        
        # Guardar cambios
        with pd.ExcelWriter(DB_FILE, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='users', index=False)
            # Copiar las demás hojas
            for sheet in ['units', 'status_changes', 'part_requests', 'notifications']:
                sheet_df = pd.read_excel(DB_FILE, sheet_name=sheet)
                sheet_df.to_excel(writer, sheet_name=sheet, index=False)
        
        return True, new_id
    
    @staticmethod
    def validate_login(username, password):
        """Valida credenciales de inicio de sesión"""
        user = ExcelUser.get_by_username(username)
        if user and check_password_hash(user['password_hash'], password):
            return True, user
        return False, None


class ExcelUnit:
    @staticmethod
    def get_all():
        """Obtiene todas las unidades"""
        init_excel_db()
        df = pd.read_excel(DB_FILE, sheet_name='units')
        return df.to_dict('records')
    
    @staticmethod
    def get_by_id(unit_id):
        """Obtiene una unidad por su ID"""
        init_excel_db()
        df = pd.read_excel(DB_FILE, sheet_name='units')
        unit = df[df['id'] == unit_id]
        if unit.empty:
            return None
        return unit.iloc[0].to_dict()
    
    @staticmethod
    def get_by_status(status):
        """Obtiene unidades por su estado"""
        init_excel_db()
        df = pd.read_excel(DB_FILE, sheet_name='units')
        units = df[df['current_status'] == status]
        return units.to_dict('records')
    
    @staticmethod
    def create(unit_number, description, operator_name, registered_by_id):
        """Crea una nueva unidad"""
        init_excel_db()
        df = pd.read_excel(DB_FILE, sheet_name='units')
        
        # Verificar si el número de unidad ya existe
        if not df[df['unit_number'] == unit_number].empty:
            return False, "El número de unidad ya está registrado"
        
        # Generar ID (el máximo + 1)
        new_id = 1
        if not df.empty:
            new_id = df['id'].max() + 1
        
        # Añadir nueva unidad
        new_unit = {
            'id': new_id,
            'unit_number': unit_number,
            'description': description,
            'operator_name': operator_name,
            'current_status': 'registered',
            'registered_by_id': registered_by_id,
            'created_at': datetime.now().isoformat()
        }
        
        df = df.append(new_unit, ignore_index=True)
        
        # Guardar cambios
        with pd.ExcelWriter(DB_FILE, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='units', index=False)
            # Copiar las demás hojas
            for sheet in ['users', 'status_changes', 'part_requests', 'notifications']:
                sheet_df = pd.read_excel(DB_FILE, sheet_name=sheet)
                sheet_df.to_excel(writer, sheet_name=sheet, index=False)
        
        return True, new_id
    
    @staticmethod
    def update_status(unit_id, new_status, user_id, notes=None):
        """Actualiza el estado de una unidad"""
        init_excel_db()
        units_df = pd.read_excel(DB_FILE, sheet_name='units')
        status_changes_df = pd.read_excel(DB_FILE, sheet_name='status_changes')
        
        # Verificar si la unidad existe
        unit = units_df[units_df['id'] == unit_id]
        if unit.empty:
            return False, "Unidad no encontrada"
        
        old_status = unit.iloc[0]['current_status']
        
        # Actualizar estado
        units_df.loc[units_df['id'] == unit_id, 'current_status'] = new_status
        
        # Generar ID para el cambio de estado (el máximo + 1)
        new_change_id = 1
        if not status_changes_df.empty:
            new_change_id = status_changes_df['id'].max() + 1
        
        # Registrar cambio de estado
        new_status_change = {
            'id': new_change_id,
            'unit_id': unit_id,
            'old_status': old_status,
            'new_status': new_status,
            'notes': notes if notes else "",
            'changed_by_id': user_id,
            'created_at': datetime.now().isoformat()
        }
        
        status_changes_df = status_changes_df.append(new_status_change, ignore_index=True)
        
        # Guardar cambios
        with pd.ExcelWriter(DB_FILE, engine='openpyxl') as writer:
            units_df.to_excel(writer, sheet_name='units', index=False)
            status_changes_df.to_excel(writer, sheet_name='status_changes', index=False)
            # Copiar las demás hojas
            for sheet in ['users', 'part_requests', 'notifications']:
                sheet_df = pd.read_excel(DB_FILE, sheet_name=sheet)
                sheet_df.to_excel(writer, sheet_name=sheet, index=False)
        
        return True, new_change_id


class ExcelStatusChange:
    @staticmethod
    def get_all():
        """Obtiene todos los cambios de estado"""
        init_excel_db()
        df = pd.read_excel(DB_FILE, sheet_name='status_changes')
        return df.to_dict('records')
    
    @staticmethod
    def get_by_unit(unit_id):
        """Obtiene cambios de estado por unidad"""
        init_excel_db()
        df = pd.read_excel(DB_FILE, sheet_name='status_changes')
        changes = df[df['unit_id'] == unit_id].sort_values(by='created_at', ascending=False)
        return changes.to_dict('records')


class ExcelPartRequest:
    @staticmethod
    def get_all():
        """Obtiene todas las solicitudes de piezas"""
        init_excel_db()
        df = pd.read_excel(DB_FILE, sheet_name='part_requests')
        return df.to_dict('records')
    
    @staticmethod
    def get_by_id(request_id):
        """Obtiene una solicitud por su ID"""
        init_excel_db()
        df = pd.read_excel(DB_FILE, sheet_name='part_requests')
        request = df[df['id'] == request_id]
        if request.empty:
            return None
        return request.iloc[0].to_dict()
    
    @staticmethod
    def get_by_unit(unit_id):
        """Obtiene solicitudes por unidad"""
        init_excel_db()
        df = pd.read_excel(DB_FILE, sheet_name='part_requests')
        requests = df[df['unit_id'] == unit_id].sort_values(by='created_at', ascending=False)
        return requests.to_dict('records')
    
    @staticmethod
    def get_by_status(status):
        """Obtiene solicitudes por estado"""
        init_excel_db()
        df = pd.read_excel(DB_FILE, sheet_name='part_requests')
        requests = df[df['status'] == status]
        return requests.to_dict('records')
    
    @staticmethod
    def create(unit_id, part_name, quantity, user_id, notes=None):
        """Crea una nueva solicitud de piezas"""
        init_excel_db()
        df = pd.read_excel(DB_FILE, sheet_name='part_requests')
        
        # Generar ID (el máximo + 1)
        new_id = 1
        if not df.empty:
            new_id = df['id'].max() + 1
        
        # Añadir nueva solicitud
        now = datetime.now().isoformat()
        new_request = {
            'id': new_id,
            'unit_id': unit_id,
            'part_name': part_name,
            'quantity': quantity,
            'status': 'pending',
            'requested_by_id': user_id,
            'created_at': now,
            'updated_at': now,
            'notes': notes if notes else ""
        }
        
        df = df.append(new_request, ignore_index=True)
        
        # Guardar cambios
        with pd.ExcelWriter(DB_FILE, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='part_requests', index=False)
            # Copiar las demás hojas
            for sheet in ['users', 'units', 'status_changes', 'notifications']:
                sheet_df = pd.read_excel(DB_FILE, sheet_name=sheet)
                sheet_df.to_excel(writer, sheet_name=sheet, index=False)
        
        return True, new_id
    
    @staticmethod
    def update_status(request_id, new_status, notes=None):
        """Actualiza el estado de una solicitud de piezas"""
        init_excel_db()
        df = pd.read_excel(DB_FILE, sheet_name='part_requests')
        
        # Verificar si la solicitud existe
        request = df[df['id'] == request_id]
        if request.empty:
            return False, "Solicitud no encontrada"
        
        # Actualizar estado y notas
        df.loc[df['id'] == request_id, 'status'] = new_status
        df.loc[df['id'] == request_id, 'updated_at'] = datetime.now().isoformat()
        
        if notes:
            df.loc[df['id'] == request_id, 'notes'] = notes
        
        # Guardar cambios
        with pd.ExcelWriter(DB_FILE, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='part_requests', index=False)
            # Copiar las demás hojas
            for sheet in ['users', 'units', 'status_changes', 'notifications']:
                sheet_df = pd.read_excel(DB_FILE, sheet_name=sheet)
                sheet_df.to_excel(writer, sheet_name=sheet, index=False)
        
        return True, request_id


class ExcelNotification:
    @staticmethod
    def get_all():
        """Obtiene todas las notificaciones"""
        init_excel_db()
        df = pd.read_excel(DB_FILE, sheet_name='notifications')
        return df.to_dict('records')
    
    @staticmethod
    def get_by_id(notification_id):
        """Obtiene una notificación por su ID"""
        init_excel_db()
        df = pd.read_excel(DB_FILE, sheet_name='notifications')
        notification = df[df['id'] == notification_id]
        if notification.empty:
            return None
        return notification.iloc[0].to_dict()
    
    @staticmethod
    def get_by_user(user_id, limit=None, unread_only=False):
        """Obtiene notificaciones por usuario"""
        init_excel_db()
        df = pd.read_excel(DB_FILE, sheet_name='notifications')
        
        # Filtrar por usuario
        notifications = df[df['user_id'] == user_id]
        
        # Filtrar solo no leídas si se especifica
        if unread_only:
            notifications = notifications[notifications['is_read'] == False]
        
        # Ordenar por fecha de creación descendente
        notifications = notifications.sort_values(by='created_at', ascending=False)
        
        # Limitar resultados si se especifica
        if limit:
            notifications = notifications.head(limit)
        
        return notifications.to_dict('records')
    
    @staticmethod
    def create(user_id, message, type, reference_id=None, reference_type=None):
        """Crea una nueva notificación"""
        init_excel_db()
        df = pd.read_excel(DB_FILE, sheet_name='notifications')
        
        # Generar ID (el máximo + 1)
        new_id = 1
        if not df.empty:
            new_id = df['id'].max() + 1
        
        # Añadir nueva notificación
        new_notification = {
            'id': new_id,
            'user_id': user_id,
            'message': message,
            'type': type,
            'reference_id': reference_id if reference_id else np.nan,
            'reference_type': reference_type if reference_type else np.nan,
            'is_read': False,
            'created_at': datetime.now().isoformat()
        }
        
        df = df.append(new_notification, ignore_index=True)
        
        # Guardar cambios
        with pd.ExcelWriter(DB_FILE, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='notifications', index=False)
            # Copiar las demás hojas
            for sheet in ['users', 'units', 'status_changes', 'part_requests']:
                sheet_df = pd.read_excel(DB_FILE, sheet_name=sheet)
                sheet_df.to_excel(writer, sheet_name=sheet, index=False)
        
        return True, new_id
    
    @staticmethod
    def mark_as_read(notification_id):
        """Marca una notificación como leída"""
        init_excel_db()
        df = pd.read_excel(DB_FILE, sheet_name='notifications')
        
        # Verificar si la notificación existe
        notification = df[df['id'] == notification_id]
        if notification.empty:
            return False, "Notificación no encontrada"
        
        # Marcar como leída
        df.loc[df['id'] == notification_id, 'is_read'] = True
        
        # Guardar cambios
        with pd.ExcelWriter(DB_FILE, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='notifications', index=False)
            # Copiar las demás hojas
            for sheet in ['users', 'units', 'status_changes', 'part_requests']:
                sheet_df = pd.read_excel(DB_FILE, sheet_name=sheet)
                sheet_df.to_excel(writer, sheet_name=sheet, index=False)
        
        return True, notification_id
    
    @staticmethod
    def mark_all_as_read(user_id):
        """Marca todas las notificaciones de un usuario como leídas"""
        init_excel_db()
        df = pd.read_excel(DB_FILE, sheet_name='notifications')
        
        # Marcar todas como leídas
        df.loc[(df['user_id'] == user_id) & (df['is_read'] == False), 'is_read'] = True
        
        # Guardar cambios
        with pd.ExcelWriter(DB_FILE, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='notifications', index=False)
            # Copiar las demás hojas
            for sheet in ['users', 'units', 'status_changes', 'part_requests']:
                sheet_df = pd.read_excel(DB_FILE, sheet_name=sheet)
                sheet_df.to_excel(writer, sheet_name=sheet, index=False)
        
        return True
    
    @staticmethod
    def create_for_status_change(unit_id, old_status, new_status, user_id=None):
        """Crea notificaciones para un cambio de estado de unidad"""
        init_excel_db()
        
        # Obtener datos de la unidad
        units_df = pd.read_excel(DB_FILE, sheet_name='units')
        unit = units_df[units_df['id'] == unit_id]
        if unit.empty:
            return False, "Unidad no encontrada"
        
        unit_number = unit.iloc[0]['unit_number']
        
        # Obtener todos los usuarios
        users_df = pd.read_excel(DB_FILE, sheet_name='users')
        
        # Crear notificaciones según el departamento
        success = True
        
        # Para Control de Tráfico: Notificar cuando una unidad cambia a "completed"
        if new_status == 'completed':
            traffic_users = users_df[users_df['department'] == 'traffic_control']
            for _, traffic_user in traffic_users.iterrows():
                message = f"Unidad {unit_number} lista para recoger del taller"
                ExcelNotification.create(
                    traffic_user['id'], 
                    message, 
                    'status_change', 
                    unit_id, 
                    'unit'
                )
        
        # Para Taller: Notificar cuando una unidad se registra o cambia a "waiting_parts"
        if new_status in ['registered', 'waiting_parts']:
            workshop_users = users_df[users_df['department'] == 'workshop']
            status_text = "registrada" if new_status == 'registered' else "esperando repuestos"
            for _, workshop_user in workshop_users.iterrows():
                message = f"Unidad {unit_number} {status_text}"
                ExcelNotification.create(
                    workshop_user['id'], 
                    message, 
                    'status_change', 
                    unit_id, 
                    'unit'
                )
        
        # Para Almacén: Notificar cuando una unidad cambia a "waiting_parts"
        if new_status == 'waiting_parts':
            warehouse_users = users_df[users_df['department'] == 'warehouse']
            for _, warehouse_user in warehouse_users.iterrows():
                message = f"Unidad {unit_number} esperando repuestos"
                ExcelNotification.create(
                    warehouse_user['id'], 
                    message, 
                    'status_change', 
                    unit_id, 
                    'unit'
                )
        
        return success
    
    @staticmethod
    def create_for_unit_register(unit_id, user_id=None):
        """Crea notificaciones para el registro de una nueva unidad"""
        init_excel_db()
        
        # Obtener datos de la unidad
        units_df = pd.read_excel(DB_FILE, sheet_name='units')
        unit = units_df[units_df['id'] == unit_id]
        if unit.empty:
            return False, "Unidad no encontrada"
        
        unit_number = unit.iloc[0]['unit_number']
        
        # Obtener todos los usuarios de taller
        users_df = pd.read_excel(DB_FILE, sheet_name='users')
        workshop_users = users_df[users_df['department'] == 'workshop']
        
        # Crear notificaciones para todos los usuarios de taller
        success = True
        for _, workshop_user in workshop_users.iterrows():
            message = f"Nueva unidad registrada: {unit_number}"
            ExcelNotification.create(
                workshop_user['id'], 
                message, 
                'unit_register', 
                unit_id, 
                'unit'
            )
        
        return success
    
    @staticmethod
    def create_for_part_request(request_id, user_id=None):
        """Crea notificaciones para solicitudes de piezas"""
        init_excel_db()
        
        # Obtener datos de la solicitud
        part_requests_df = pd.read_excel(DB_FILE, sheet_name='part_requests')
        request = part_requests_df[part_requests_df['id'] == request_id]
        if request.empty:
            return False, "Solicitud no encontrada"
        
        unit_id = request.iloc[0]['unit_id']
        part_name = request.iloc[0]['part_name']
        
        # Obtener datos de la unidad
        units_df = pd.read_excel(DB_FILE, sheet_name='units')
        unit = units_df[units_df['id'] == unit_id]
        if unit.empty:
            return False, "Unidad no encontrada"
        
        unit_number = unit.iloc[0]['unit_number']
        
        # Obtener todos los usuarios de almacén
        users_df = pd.read_excel(DB_FILE, sheet_name='users')
        warehouse_users = users_df[users_df['department'] == 'warehouse']
        
        # Crear notificaciones para todos los usuarios de almacén
        success = True
        for _, warehouse_user in warehouse_users.iterrows():
            message = f"Nueva solicitud de pieza: {part_name} para unidad {unit_number}"
            ExcelNotification.create(
                warehouse_user['id'], 
                message, 
                'part_request', 
                request_id, 
                'part_request'
            )
        
        return success


# Inicializar la base de datos al importar el módulo
init_excel_db()