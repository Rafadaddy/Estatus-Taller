import os
from flask import Flask, render_template, flash, redirect, url_for, request, jsonify
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash
from datetime import datetime
import pandas as pd

# Crear la aplicación Flask
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "desarrollo-secreto")

# Configurar Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor inicia sesión para acceder a esta página'
login_manager.login_message_category = 'warning'

# Importar modelos y formularios
from excel_models import User, Unit, StatusChange, PartRequest, Notification, load_user
from forms import LoginForm, RegisterUnitForm, UpdateStatusForm, PartRequestForm, UpdatePartRequestForm, UserForm

# Configurar la función de carga de usuario para Flask-Login
login_manager.user_loader(load_user)

# Importar rutas
from routes import *

# Configurar manejo de errores
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)