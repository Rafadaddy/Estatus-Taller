from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, IntegerField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models import User, Unit

class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesión')

class RegisterUnitForm(FlaskForm):
    unit_number = StringField('Número de Unidad', validators=[DataRequired(), Length(min=2, max=50)])
    description = TextAreaField('Descripción', validators=[DataRequired(), Length(max=200)])
    operator_name = StringField('Nombre del Operador', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Registrar Unidad')
    
    def validate_unit_number(self, unit_number):
        unit = Unit.query.filter_by(unit_number=unit_number.data).first()
        if unit:
            raise ValidationError('Este número de unidad ya está registrado.')

class UpdateStatusForm(FlaskForm):
    unit_id = HiddenField('ID de Unidad', validators=[DataRequired()])
    new_status = SelectField('Nuevo Estado', choices=[
        ('registered', 'Registrada'),
        ('in_workshop', 'En Taller'),
        ('waiting_parts', 'Esperando Repuestos'),
        ('completed', 'Completada'),
        ('received', 'Recibida por Control')
    ], validators=[DataRequired()])
    notes = TextAreaField('Notas', validators=[Length(max=500)])
    submit = SubmitField('Confirmar Recepción')

class PartRequestForm(FlaskForm):
    unit_id = HiddenField('ID de Unidad', validators=[DataRequired()])
    part_name = StringField('Nombre de Pieza', validators=[DataRequired(), Length(max=100)])
    quantity = IntegerField('Cantidad', validators=[DataRequired()])
    notes = TextAreaField('Notas', validators=[Length(max=500)])
    submit = SubmitField('Solicitar Pieza')

class UpdatePartRequestForm(FlaskForm):
    request_id = HiddenField('ID de Solicitud', validators=[DataRequired()])
    status = SelectField('Estado', choices=[
        ('pending', 'Pendiente'),
        ('available', 'Disponible'),
        ('installed', 'Instalada')
    ], validators=[DataRequired()])
    notes = TextAreaField('Notas', validators=[Length(max=500)])
    submit = SubmitField('Actualizar Solicitud de Pieza')

class UserForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('password')])
    department = SelectField('Departamento', choices=[
        ('traffic_control', 'Control de Tráfico'),
        ('workshop', 'Taller'),
        ('warehouse', 'Almacén'),
        ('admin', 'Administrador')
    ], validators=[DataRequired()])
    submit = SubmitField('Crear Usuario')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Este nombre de usuario ya existe.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Este correo electrónico ya está en uso.')
