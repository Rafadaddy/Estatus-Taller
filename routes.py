import logging
from datetime import datetime, timedelta
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import func

from app import app, db
from models import User, Unit, StatusChange, PartRequest
from forms import (
    LoginForm, RegisterUnitForm, UpdateStatusForm, 
    PartRequestForm, UpdatePartRequestForm, UserForm
)

# Context processor to make the current date/time available to all templates
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# Home route
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
            # Admin can see all departments
            return render_template('index.html')
    return render_template('index.html')

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page or url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Traffic Control routes
@app.route('/traffic_control/dashboard')
@login_required
def traffic_control_dashboard():
    if current_user.department not in ['traffic_control', 'admin']:
        flash('Access denied. You do not have permission to view this page.', 'danger')
        return redirect(url_for('index'))
    
    # Get recently registered units and completed units
    registered_units = Unit.query.filter_by(current_status='registered').order_by(Unit.created_at.desc()).limit(10).all()
    completed_units = Unit.query.filter_by(current_status='completed').order_by(Unit.created_at.desc()).limit(10).all()
    
    return render_template(
        'traffic_control/dashboard.html',
        registered_units=registered_units,
        completed_units=completed_units
    )

@app.route('/traffic_control/register_unit', methods=['GET', 'POST'])
@login_required
def register_unit():
    if current_user.department not in ['traffic_control', 'admin']:
        flash('Access denied. You do not have permission to view this page.', 'danger')
        return redirect(url_for('index'))
    
    form = RegisterUnitForm()
    if form.validate_on_submit():
        unit = Unit(
            unit_number=form.unit_number.data,
            description=form.description.data,
            operator_name=form.operator_name.data,
            current_status='registered',
            registered_by_id=current_user.id
        )
        db.session.add(unit)
        
        # Add initial status change record
        status_change = StatusChange(
            unit=unit,
            old_status='',
            new_status='registered',
            notes=f'Unit initially registered by {current_user.username}',
            changed_by_id=current_user.id
        )
        db.session.add(status_change)
        
        db.session.commit()
        flash(f'Unit {unit.unit_number} has been registered successfully!', 'success')
        return redirect(url_for('traffic_control_dashboard'))
    
    return render_template('traffic_control/register_unit.html', form=form)

@app.route('/traffic_control/confirm_completion/<int:unit_id>', methods=['GET', 'POST'])
@login_required
def confirm_completion(unit_id):
    if current_user.department not in ['traffic_control', 'admin']:
        flash('Access denied. You do not have permission to view this page.', 'danger')
        return redirect(url_for('index'))
    
    unit = Unit.query.get_or_404(unit_id)
    
    # Check if the unit is already completed
    if unit.current_status == 'completed':
        # Unit is completed and ready to be received by traffic control
        form = UpdateStatusForm(obj=unit)
        form.unit_id.data = unit.id
        form.new_status.data = 'received'
        
        if request.method == 'POST' and form.validate_on_submit():
            old_status = unit.current_status
            unit.current_status = 'received'
            
            # Record the status change
            status_change = StatusChange(
                unit=unit,
                old_status=old_status,
                new_status='received',
                notes=form.notes.data or 'Unidad recibida por Control de Tráfico',
                changed_by_id=current_user.id
            )
            db.session.add(status_change)
            db.session.commit()
            
            flash(f'Unidad {unit.unit_number} ha sido marcada como recibida por Control de Tráfico.', 'success')
            return redirect(url_for('traffic_control_dashboard'))
        
        return render_template('traffic_control/confirm_receipt.html', form=form, unit=unit)
    
    # Only units in workshop or pending parts can be marked as completed by workshop
    if unit.current_status not in ['in_workshop', 'waiting_parts']:
        flash('Esta unidad no está lista para ser completada.', 'warning')
        return redirect(url_for('traffic_control_dashboard'))
    
    form = UpdateStatusForm(obj=unit)
    form.unit_id.data = unit.id
    form.new_status.data = 'completed'
    
    if request.method == 'POST' and form.validate_on_submit():
        old_status = unit.current_status
        unit.current_status = 'completed'
        
        # Record the status change
        status_change = StatusChange(
            unit=unit,
            old_status=old_status,
            new_status='completed',
            notes=form.notes.data,
            changed_by_id=current_user.id
        )
        db.session.add(status_change)
        db.session.commit()
        
        flash(f'Unidad {unit.unit_number} ha sido marcada como completada!', 'success')
        return redirect(url_for('traffic_control_dashboard'))
    
    return render_template('traffic_control/confirm_completion.html', form=form, unit=unit)

# Workshop routes
@app.route('/workshop/dashboard')
@login_required
def workshop_dashboard():
    if current_user.department not in ['workshop', 'admin']:
        flash('Access denied. You do not have permission to view this page.', 'danger')
        return redirect(url_for('index'))
    
    # Get units that need workshop attention
    registered_units = Unit.query.filter_by(current_status='registered').order_by(Unit.created_at).all()
    in_workshop_units = Unit.query.filter_by(current_status='in_workshop').order_by(Unit.created_at).all()
    parts_pending_units = Unit.query.filter_by(current_status='waiting_parts').order_by(Unit.created_at).all()
    completed_units = Unit.query.filter_by(current_status='completed').order_by(Unit.created_at).all()
    received_units = Unit.query.filter_by(current_status='received').order_by(Unit.created_at).all()
    
    return render_template(
        'workshop/dashboard.html',
        registered_units=registered_units,
        in_workshop_units=in_workshop_units,
        parts_pending_units=parts_pending_units,
        completed_units=completed_units,
        received_units=received_units
    )

@app.route('/workshop/unit/<int:unit_id>', methods=['GET', 'POST'])
@login_required
def unit_details(unit_id):
    if current_user.department not in ['workshop', 'admin']:
        flash('Access denied. You do not have permission to view this page.', 'danger')
        return redirect(url_for('index'))
    
    unit = Unit.query.get_or_404(unit_id)
    status_form = UpdateStatusForm(obj=unit)
    status_form.unit_id.data = unit.id
    
    part_form = PartRequestForm()
    part_form.unit_id.data = unit.id
    
    # Get unit history and part requests
    history = StatusChange.query.filter_by(unit_id=unit.id).order_by(StatusChange.created_at.desc()).all()
    part_requests = PartRequest.query.filter_by(unit_id=unit.id).order_by(PartRequest.created_at.desc()).all()
    
    if request.method == 'POST':
        # Handle status update
        if 'submit' in request.form and status_form.validate_on_submit():
            old_status = unit.current_status
            unit.current_status = status_form.new_status.data
            
            # Record the status change
            status_change = StatusChange(
                unit=unit,
                old_status=old_status,
                new_status=unit.current_status,
                notes=status_form.notes.data,
                changed_by_id=current_user.id
            )
            db.session.add(status_change)
            db.session.commit()
            
            flash(f'Status for unit {unit.unit_number} has been updated to {unit.get_status_display()}!', 'success')
            return redirect(url_for('unit_details', unit_id=unit.id))
            
        # Handle part request
        elif part_form.validate_on_submit():
            part_request = PartRequest(
                unit_id=unit.id,
                part_name=part_form.part_name.data,
                quantity=part_form.quantity.data,
                notes=part_form.notes.data,
                requested_by_id=current_user.id
            )
            db.session.add(part_request)
            
            # Update unit status to waiting for parts if it wasn't already
            if unit.current_status != 'waiting_parts':
                old_status = unit.current_status
                unit.current_status = 'waiting_parts'
                
                # Record the status change
                status_change = StatusChange(
                    unit=unit,
                    old_status=old_status,
                    new_status='waiting_parts',
                    notes=f'Automatically changed due to part request for {part_form.part_name.data}',
                    changed_by_id=current_user.id
                )
                db.session.add(status_change)
            
            db.session.commit()
            flash(f'Part request for {part_form.part_name.data} has been submitted!', 'success')
            return redirect(url_for('unit_details', unit_id=unit.id))
    
    return render_template(
        'workshop/unit_details.html',
        unit=unit,
        status_form=status_form,
        part_form=part_form,
        history=history,
        part_requests=part_requests
    )

# Warehouse routes
@app.route('/warehouse/dashboard')
@login_required
def warehouse_dashboard():
    if current_user.department not in ['warehouse', 'admin']:
        flash('Access denied. You do not have permission to view this page.', 'danger')
        return redirect(url_for('index'))
    
    # Get all pending part requests
    pending_requests = PartRequest.query.filter_by(status='pending').order_by(PartRequest.created_at).all()
    available_requests = PartRequest.query.filter_by(status='available').order_by(PartRequest.created_at).all()
    
    return render_template(
        'warehouse/dashboard.html',
        pending_requests=pending_requests,
        available_requests=available_requests
    )

@app.route('/warehouse/parts_management/<int:request_id>', methods=['GET', 'POST'])
@login_required
def manage_part_request(request_id):
    if current_user.department not in ['warehouse', 'admin']:
        flash('Access denied. You do not have permission to view this page.', 'danger')
        return redirect(url_for('index'))
    
    part_request = PartRequest.query.get_or_404(request_id)
    unit = Unit.query.get(part_request.unit_id)
    
    form = UpdatePartRequestForm(obj=part_request)
    form.request_id.data = part_request.id
    
    if form.validate_on_submit():
        old_status = part_request.status
        part_request.status = form.status.data
        part_request.notes = f"{part_request.notes}\n\n{form.notes.data}" if part_request.notes else form.notes.data
        
        # If all part requests are fulfilled, update unit status
        if form.status.data == 'available':
            flash(f'Part request for {part_request.part_name} marked as available!', 'success')
        elif form.status.data == 'installed':
            flash(f'Part request for {part_request.part_name} marked as installed!', 'success')
            
            # Check if all parts for this unit are installed
            if not PartRequest.query.filter(
                PartRequest.unit_id == unit.id,
                PartRequest.status != 'installed'
            ).first():
                old_unit_status = unit.current_status
                unit.current_status = 'in_workshop'
                
                # Record the unit status change
                status_change = StatusChange(
                    unit=unit,
                    old_status=old_unit_status,
                    new_status='in_workshop',
                    notes='Automatically updated - all parts have been installed',
                    changed_by_id=current_user.id
                )
                db.session.add(status_change)
                flash(f'All parts for unit {unit.unit_number} have been installed. Unit status updated to In Workshop.', 'success')
        
        db.session.commit()
        return redirect(url_for('warehouse_dashboard'))
    
    return render_template(
        'warehouse/parts_management.html',
        form=form,
        part_request=part_request,
        unit=unit
    )

# Unit history route (accessible to all departments)
@app.route('/unit_history/<int:unit_id>')
@login_required
def unit_history(unit_id):
    unit = Unit.query.get_or_404(unit_id)
    
    # Get unit history and part requests
    status_changes = StatusChange.query.filter_by(unit_id=unit.id).order_by(StatusChange.created_at.desc()).all()
    part_requests = PartRequest.query.filter_by(unit_id=unit.id).order_by(PartRequest.created_at.desc()).all()
    
    return render_template(
        'unit_history.html',
        unit=unit,
        status_changes=status_changes,
        part_requests=part_requests
    )

# Historical records route (search and view all units)
@app.route('/historical_records')
@login_required
def historical_records():
    # Get search parameters from query string
    unit_number = request.args.get('unit_number', '')
    operator_name = request.args.get('operator_name', '')
    status = request.args.get('status', '')
    date_range = request.args.get('date_range', '')
    
    # Build query
    query = Unit.query
    
    # Apply filters if provided
    if unit_number:
        query = query.filter(Unit.unit_number.ilike(f'%{unit_number}%'))
    
    if operator_name:
        query = query.filter(Unit.operator_name.ilike(f'%{operator_name}%'))
    
    if status:
        query = query.filter(Unit.current_status == status)
    
    # Apply date filter
    if date_range:
        today = datetime.now().date()
        if date_range == 'today':
            query = query.filter(func.date(Unit.created_at) == today)
        elif date_range == 'week':
            start_of_week = today - timedelta(days=today.weekday())
            query = query.filter(func.date(Unit.created_at) >= start_of_week)
        elif date_range == 'month':
            start_of_month = today.replace(day=1)
            query = query.filter(func.date(Unit.created_at) >= start_of_month)
        elif date_range == 'year':
            start_of_year = today.replace(month=1, day=1)
            query = query.filter(func.date(Unit.created_at) >= start_of_year)
    
    # Get results
    units = query.order_by(Unit.created_at.desc()).all()
    
    return render_template('historical_records.html', units=units)

# Admin routes
@app.route('/admin/users', methods=['GET', 'POST'])
@login_required
def manage_users():
    if current_user.department != 'admin':
        flash('Access denied. You do not have permission to view this page.', 'danger')
        return redirect(url_for('index'))
    
    form = UserForm()
    
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data),
            department=form.department.data
        )
        db.session.add(user)
        db.session.commit()
        flash(f'User {user.username} has been created successfully!', 'success')
        return redirect(url_for('manage_users'))
    
    users = User.query.all()
    return render_template('admin/users.html', users=users, form=form)

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500
