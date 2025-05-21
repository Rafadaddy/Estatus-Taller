from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, IntegerField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models import User, Unit

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterUnitForm(FlaskForm):
    unit_number = StringField('Unit Number', validators=[DataRequired(), Length(min=2, max=50)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(max=200)])
    operator_name = StringField('Operator Name', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Register Unit')
    
    def validate_unit_number(self, unit_number):
        unit = Unit.query.filter_by(unit_number=unit_number.data).first()
        if unit:
            raise ValidationError('This unit number is already registered.')

class UpdateStatusForm(FlaskForm):
    unit_id = HiddenField('Unit ID', validators=[DataRequired()])
    new_status = SelectField('New Status', choices=[
        ('registered', 'Registered'),
        ('in_workshop', 'In Workshop'),
        ('waiting_parts', 'Waiting for Parts'),
        ('completed', 'Completed')
    ], validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Length(max=500)])
    submit = SubmitField('Update Status')

class PartRequestForm(FlaskForm):
    unit_id = HiddenField('Unit ID', validators=[DataRequired()])
    part_name = StringField('Part Name', validators=[DataRequired(), Length(max=100)])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Length(max=500)])
    submit = SubmitField('Request Part')

class UpdatePartRequestForm(FlaskForm):
    request_id = HiddenField('Request ID', validators=[DataRequired()])
    status = SelectField('Status', choices=[
        ('pending', 'Pending'),
        ('available', 'Available'),
        ('installed', 'Installed')
    ], validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Length(max=500)])
    submit = SubmitField('Update Part Request')

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    department = SelectField('Department', choices=[
        ('traffic_control', 'Traffic Control'),
        ('workshop', 'Workshop'),
        ('warehouse', 'Warehouse'),
        ('admin', 'Admin')
    ], validators=[DataRequired()])
    submit = SubmitField('Create User')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already exists.')
