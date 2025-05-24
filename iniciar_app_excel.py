from main_excel import app

if __name__ == '__main__':
    print("Iniciando Sistema de Gestión de Taller con Excel...")
    print("Usuario predeterminado: admin")
    print("Contraseña predeterminada: admin")
    print("Accede a http://localhost:5000 en tu navegador")
    app.run(host='0.0.0.0', port=5000, debug=True)