from flask import render_template, flash, redirect, url_for, request, jsonify, send_file
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash
from datetime import datetime
import pandas as pd
import os

from main_excel import app
from excel_models import User, Unit, StatusChange, PartRequest, Notification
from forms import LoginForm, RegisterUnitForm, UpdateStatusForm, PartRequestForm, UpdatePartRequestForm, UserForm

# Variables globales
EXCEL_FILE = 'workshop_database.xlsx'

# Inyectar la fecha actual en todas las plantillas
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# Ruta principal
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.department == 'traffic_control':
            return redirect(url_for('traffic_control_dashboard'))
        elif current_user.department == 'workshop':
            return redirect(url_for('workshop_dashboard'))
        elif current_user.department == 'warehouse':
            return redirect(url_for('warehouse_dashboard'))
        elif current_user.department == 'admin':
            return redirect(url_for('manage_users'))
    return redirect(url_for('login'))

# Rutas de autenticación
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        success, user = User.validate_login(form.username.data, form.password.data)
        if success and user:
            login_user(user)
            flash(f'Bienvenido, {user.username}!', 'success')
            next_page = request.args.get('next')
            # Validar que next_page es una URL relativa para prevenir redirecciones abiertas
            if next_page and not next_page.startswith('/'):
                next_page = None
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Credenciales incorrectas. Intenta de nuevo.', 'danger')
    
    return render_template('login.html', form=form, title='Iniciar Sesión')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente.', 'success')
    return redirect(url_for('login'))

# Rutas para Control de Tráfico
@app.route('/traffic_control/dashboard')
@login_required
def traffic_control_dashboard():
    if current_user.department not in ['traffic_control', 'admin']:
        flash('Acceso denegado. No tienes permiso para ver esta página.', 'danger')
        return redirect(url_for('index'))
    
    # Obtener unidades pendientes
    registered_units = Unit.get_by_status('registered')
    
    # Obtener unidades completadas que no han sido recibidas
    completed_units = Unit.get_by_status('completed')
    
    return render_template('traffic_control/dashboard.html', 
                           registered_units=registered_units,
                           completed_units=completed_units)

@app.route('/traffic_control/register_unit', methods=['GET', 'POST'])
@login_required
def register_unit():
    if current_user.department not in ['traffic_control', 'admin']:
        flash('Acceso denegado. No tienes permiso para ver esta página.', 'danger')
        return redirect(url_for('index'))
    
    form = RegisterUnitForm()
    if form.validate_on_submit():
        # Crear nueva unidad
        success, unit_id = Unit.create(
            form.unit_number.data,
            form.description.data,
            form.operator_name.data,
            current_user.id
        )
        
        if success:
            # Obtener la unidad creada
            unit = Unit.get_by_id(unit_id)
            
            # Crear notificaciones
            Notification.create_for_unit_register(unit, current_user)
            
            flash(f'Unidad {unit.unit_number} registrada correctamente.', 'success')
            return redirect(url_for('traffic_control_dashboard'))
        else:
            flash(f'Error al registrar la unidad: {unit_id}', 'danger')
    
    return render_template('traffic_control/register_unit.html', form=form)

@app.route('/traffic_control/imprimir-reporte/<int:unit_id>')
@login_required
def imprimir_reporte(unit_id):
    # Verificar permisos
    if current_user.department not in ['traffic_control', 'admin', 'workshop']:
        flash('Acceso denegado. No tienes permiso para ver esta página.', 'danger')
        return redirect(url_for('index'))
    
    # Obtener datos de la unidad
    unit = Unit.get_by_id(unit_id)
    
    # Formato de fecha actual para el reporte
    fecha_actual = datetime.now().strftime('%d/%m/%Y')
    
    # Renderizar plantilla de impresión
    return render_template('traffic_control/reporte_impresion.html', 
                          unit=unit, 
                          fecha_actual=fecha_actual)

@app.route('/traffic_control/vista-previa-reporte')
@login_required
def vista_previa_reporte():
    """Vista previa del reporte sin crear unidad"""
    if current_user.department not in ['traffic_control', 'admin', 'workshop']:
        flash('Acceso denegado. No tienes permiso para ver esta página.', 'danger')
        return redirect(url_for('index'))
    
    # Datos de ejemplo para la vista previa
    class UnitPreview:
        pass
    
    unit = UnitPreview()
    unit.unit_number = request.args.get('unit_number', 'MOTORISTA')
    unit.operator_name = request.args.get('operator_name', 'OPERADOR')
    unit.description = request.args.get('description', 'DESCRIPCIÓN DEL PROBLEMA')
    
    # Formato de fecha actual
    fecha_actual = datetime.now().strftime('%d/%m/%Y')
    
    return render_template('traffic_control/reporte_impresion.html', 
                          unit=unit, 
                          fecha_actual=fecha_actual)

@app.route('/traffic_control/confirm_completion/<int:unit_id>', methods=['GET', 'POST'])
@login_required
def confirm_completion(unit_id):
    if current_user.department not in ['traffic_control', 'admin']:
        flash('Acceso denegado. No tienes permiso para ver esta página.', 'danger')
        return redirect(url_for('index'))
    
    unit = Unit.get_by_id(unit_id)
    if not unit:
        flash('Unidad no encontrada.', 'danger')
        return redirect(url_for('traffic_control_dashboard'))
    
    form = UpdateStatusForm()
    if request.method == 'GET':
        form.unit_id.data = unit.id
        form.new_status.data = 'received'
    
    if form.validate_on_submit():
        old_status = unit.current_status
        
        # Actualizar estado de la unidad
        success, _ = unit.update_status('received', current_user.id, form.notes.data)
        
        if success:
            # Crear notificación para el cambio de estado
            Notification.create_for_status_change(unit, old_status, 'received', current_user)
            
            flash(f'Unidad {unit.unit_number} marcada como recibida.', 'success')
            return redirect(url_for('traffic_control_dashboard'))
        else:
            flash('Error al actualizar el estado de la unidad.', 'danger')
    
    return render_template('traffic_control/confirm_completion.html', unit=unit, form=form)

# Rutas para Taller
@app.route('/workshop/dashboard')
@login_required
def workshop_dashboard():
    if current_user.department not in ['workshop', 'admin']:
        flash('Acceso denegado. No tienes permiso para ver esta página.', 'danger')
        return redirect(url_for('index'))
    
    # Obtener unidades en diferentes estados
    registered_units = Unit.get_by_status('registered')
    in_workshop_units = Unit.get_by_status('in_workshop')
    waiting_parts_units = Unit.get_by_status('waiting_parts')
    
    return render_template('workshop/dashboard.html',
                           registered_units=registered_units,
                           in_workshop_units=in_workshop_units,
                           waiting_parts_units=waiting_parts_units)

@app.route('/unit/<int:unit_id>', methods=['GET', 'POST'])
@login_required
def unit_details(unit_id):
    # Obtener la unidad
    unit = Unit.get_by_id(unit_id)
    if not unit:
        flash('Unidad no encontrada.', 'danger')
        return redirect(url_for('index'))
    
    # Obtener solicitudes de piezas y cambios de estado
    part_requests = PartRequest.get_by_unit(unit_id)
    status_changes = StatusChange.get_by_unit(unit_id)
    
    # Formularios
    status_form = UpdateStatusForm()
    part_form = PartRequestForm()
    
    # Pre-cargar ID de unidad en los formularios
    status_form.unit_id.data = unit.id
    part_form.unit_id.data = unit.id
    
    # Limitar opciones de estado según el departamento
    if current_user.department == 'workshop':
        status_form.new_status.choices = [
            ('in_workshop', 'En Taller'),
            ('waiting_parts', 'Esperando Repuestos'),
            ('completed', 'Completada')
        ]
    
    # Manejar formulario de cambio de estado
    if status_form.validate_on_submit() and 'submit_status' in request.form:
        old_status = unit.current_status
        new_status = status_form.new_status.data
        
        # Verificar permisos según departamento
        if current_user.department == 'workshop' and new_status not in ['in_workshop', 'waiting_parts', 'completed']:
            flash('No tienes permiso para cambiar a este estado.', 'danger')
        elif current_user.department == 'traffic_control' and new_status not in ['received']:
            flash('No tienes permiso para cambiar a este estado.', 'danger')
        else:
            # Actualizar estado
            success, _ = unit.update_status(new_status, current_user.id, status_form.notes.data)
            
            if success:
                # Crear notificación para el cambio de estado
                Notification.create_for_status_change(unit, old_status, new_status, current_user)
                
                flash(f'Estado de la unidad actualizado a "{unit.get_status_display()}".', 'success')
                return redirect(url_for('unit_details', unit_id=unit.id))
            else:
                flash('Error al actualizar el estado de la unidad.', 'danger')
    
    # Manejar formulario de solicitud de piezas
    if part_form.validate_on_submit() and 'submit_part' in request.form:
        if current_user.department not in ['workshop', 'admin']:
            flash('No tienes permiso para solicitar piezas.', 'danger')
        else:
            # Crear solicitud de pieza
            success, request_id = PartRequest.create(
                unit_id,
                part_form.part_name.data,
                part_form.quantity.data,
                current_user.id,
                part_form.notes.data
            )
            
            if success:
                flash('Solicitud de pieza creada correctamente.', 'success')
                return redirect(url_for('unit_details', unit_id=unit.id))
            else:
                flash('Error al crear la solicitud de pieza.', 'danger')
    
    return render_template('unit_details.html',
                           unit=unit,
                           part_requests=part_requests,
                           status_changes=status_changes,
                           status_form=status_form,
                           part_form=part_form)

# Rutas para Almacén
@app.route('/warehouse/dashboard')
@login_required
def warehouse_dashboard():
    if current_user.department not in ['warehouse', 'admin']:
        flash('Acceso denegado. No tienes permiso para ver esta página.', 'danger')
        return redirect(url_for('index'))
    
    # Obtener unidades esperando repuestos
    waiting_units = Unit.get_by_status('waiting_parts')
    
    # Obtener solicitudes de piezas pendientes
    pending_requests = PartRequest.get_by_status('pending')
    
    return render_template('warehouse/dashboard.html',
                           waiting_units=waiting_units,
                           pending_requests=pending_requests)

@app.route('/part-request/<int:request_id>', methods=['GET', 'POST'])
@login_required
def manage_part_request(request_id):
    if current_user.department not in ['warehouse', 'workshop', 'admin']:
        flash('Acceso denegado. No tienes permiso para ver esta página.', 'danger')
        return redirect(url_for('index'))
    
    # Obtener solicitud de pieza
    part_request = PartRequest.get_by_id(request_id)
    if not part_request:
        flash('Solicitud no encontrada.', 'danger')
        return redirect(url_for('index'))
    
    # Obtener unidad relacionada
    unit = Unit.get_by_id(part_request.unit_id)
    
    # Formulario para actualizar solicitud
    form = UpdatePartRequestForm()
    
    # Precargar ID de solicitud
    form.request_id.data = part_request.id
    
    # Limitar opciones según departamento
    if current_user.department == 'warehouse':
        form.status.choices = [
            ('pending', 'Pendiente'),
            ('available', 'Disponible')
        ]
    elif current_user.department == 'workshop':
        form.status.choices = [
            ('pending', 'Pendiente'),
            ('available', 'Disponible'),
            ('installed', 'Instalada')
        ]
    
    if form.validate_on_submit():
        new_status = form.status.data
        
        # Verificar permisos según departamento
        if current_user.department == 'warehouse' and new_status not in ['pending', 'available']:
            flash('No tienes permiso para cambiar a este estado.', 'danger')
        else:
            # Actualizar estado de la solicitud
            success, _ = part_request.update_status(new_status, form.notes.data)
            
            if success:
                flash('Estado de la solicitud actualizado correctamente.', 'success')
                
                # Enviar notificación al taller si la pieza está disponible
                if new_status == 'available':
                    # Obtener usuarios del taller
                    workshop_users = [user for user in User.get_all() if user.department == 'workshop']
                    unit = Unit.get_by_id(part_request.unit_id)
                    
                    for user in workshop_users:
                        Notification.create_for_part_request(part_request, user)
                
                # Redireccionar según el departamento
                if current_user.department == 'warehouse':
                    return redirect(url_for('warehouse_dashboard'))
                else:
                    return redirect(url_for('unit_details', unit_id=part_request.unit_id))
            else:
                flash('Error al actualizar el estado de la solicitud.', 'danger')
    
    return render_template('manage_part_request.html',
                           part_request=part_request,
                           unit=unit,
                           form=form)

# Ruta para el historial de una unidad
@app.route('/unit_history/<int:unit_id>')
@login_required
def unit_history(unit_id):
    # Obtener la unidad
    unit = Unit.get_by_id(unit_id)
    if not unit:
        flash('Unidad no encontrada.', 'danger')
        return redirect(url_for('index'))
    
    # Obtener solicitudes de piezas y cambios de estado
    part_requests = PartRequest.get_by_unit(unit_id)
    status_changes = StatusChange.get_by_unit(unit_id)
    
    return render_template('unit_history.html',
                           unit=unit,
                           part_requests=part_requests,
                           status_changes=status_changes)

# Ruta para historial completo
@app.route('/historical_records')
@login_required
def historical_records():
    # Obtener todas las unidades
    units = Unit.get_all()
    
    # Descargar a Excel si se solicita
    if request.args.get('download') == 'excel':
        # Crear DataFrame para Excel
        data = []
        for unit in units:
            status_changes = StatusChange.get_by_unit(unit.id)
            registered_by = unit.get_registered_by()
            
            unit_data = {
                'Número de Unidad': unit.unit_number,
                'Descripción': unit.description,
                'Operador': unit.operator_name,
                'Estado Actual': unit.get_status_display(),
                'Registrado Por': registered_by.username if registered_by else 'Desconocido',
                'Fecha de Registro': unit.created_at.strftime('%d/%m/%Y %H:%M')
            }
            
            # Añadir último cambio de estado si existe
            if status_changes:
                last_change = status_changes[0]
                changed_by = last_change.get_changed_by()
                unit_data.update({
                    'Último Cambio': last_change.get_new_status_display(),
                    'Fecha de Último Cambio': last_change.created_at.strftime('%d/%m/%Y %H:%M'),
                    'Realizado Por': changed_by.username if changed_by else 'Desconocido'
                })
            
            data.append(unit_data)
        
        # Crear Excel
        df = pd.DataFrame(data)
        excel_file = 'historico_unidades.xlsx'
        df.to_excel(excel_file, index=False)
        
        # Devolver archivo para descarga
        return send_file(excel_file, as_attachment=True)
    
    return render_template('historical_records.html', units=units)

# Rutas para administración de usuarios
@app.route('/admin/users', methods=['GET', 'POST'])
@login_required
def manage_users():
    if current_user.department != 'admin':
        flash('Acceso denegado. Solo los administradores pueden acceder a esta página.', 'danger')
        return redirect(url_for('index'))
    
    # Obtener todos los usuarios
    users = User.get_all()
    
    # Formulario para crear nuevo usuario
    form = UserForm()
    
    if form.validate_on_submit():
        # Crear nuevo usuario
        success, message_or_id = User.create(
            form.username.data,
            form.email.data,
            form.password.data,
            form.department.data
        )
        
        if success:
            flash(f'Usuario {form.username.data} creado correctamente.', 'success')
            return redirect(url_for('manage_users'))
        else:
            flash(f'Error al crear usuario: {message_or_id}', 'danger')
    
    return render_template('admin/users.html', users=users, form=form)

# Rutas para notificaciones
@app.route('/notifications')
@login_required
def notifications():
    # Obtener notificaciones del usuario actual
    user_notifications = Notification.get_by_user(current_user.id)
    
    return render_template('notifications.html', notifications=user_notifications)

@app.route('/api/unread-notifications')
@login_required
def unread_notifications():
    # Obtener notificaciones no leídas del usuario actual
    unread = Notification.get_by_user(current_user.id, unread_only=True)
    
    # Formatear para API
    result = []
    for notification in unread:
        result.append({
            'id': notification.id,
            'message': notification.message,
            'created_at': notification.created_at.strftime('%d/%m/%Y %H:%M'),
            'url': notification.get_url()
        })
    
    return jsonify({'count': len(result), 'notifications': result})

@app.route('/api/mark-notification-read/<int:notification_id>', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    notification = Notification.get_by_id(notification_id)
    
    if notification and notification.user_id == current_user.id:
        success, _ = notification.mark_as_read()
        return jsonify({'success': success})
    
    return jsonify({'success': False, 'error': 'Notificación no encontrada'}), 404

@app.route('/api/mark-all-notifications-read', methods=['POST'])
@login_required
def mark_all_notifications_read():
    success = Notification.mark_all_as_read(current_user.id)
    return jsonify({'success': success})
