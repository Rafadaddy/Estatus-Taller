# Sistema de Gestión de Taller con Excel

Este sistema es una versión adaptada del Sistema de Gestión de Taller original, modificada para utilizar archivos Excel como almacenamiento de datos en lugar de una base de datos SQL.

## Características Principales

- Mismo sistema de gestión de taller con todas las funcionalidades originales
- Almacenamiento de datos en un archivo Excel local
- Posibilidad de sincronización con OneDrive
- Respaldos automáticos de los datos
- Sin necesidad de servidor de base de datos

## Estructura de Archivos

- `main_excel.py`: Archivo principal para iniciar la aplicación con Excel
- `excel_db.py`: Módulo para el acceso y manipulación de datos en Excel
- `excel_models.py`: Modelos adaptados para trabajar con Excel
- `routes_excel.py`: Rutas de la aplicación adaptadas para Excel
- `excel_sync.py`: Utilidades para sincronizar datos con OneDrive
- `workshop_database.xlsx`: Archivo Excel que contiene todos los datos

## Instalación y Configuración

1. Asegúrate de tener instalados todos los paquetes necesarios:
   ```
   pip install flask flask-login flask-wtf werkzeug pandas openpyxl xlsxwriter
   ```

2. Para ejecutar la aplicación con Excel:
   ```
   python main_excel.py
   ```

3. Para sincronizar con OneDrive, edita la ruta en `excel_sync.py` y ejecuta:
   ```
   python excel_sync.py
   ```

## Configuración para OneDrive

Para utilizar OneDrive como almacenamiento:

1. Configura la variable `onedrive_path` en `excel_sync.py` con la ruta a tu carpeta de OneDrive
2. Ejecuta la sincronización manual o programa sincronizaciones automáticas

## Respaldos

El sistema crea automáticamente respaldos de la base de datos Excel en la carpeta `backups` cuando:

1. Se realiza una sincronización con OneDrive
2. Se importa un archivo desde OneDrive

## Usuarios por Defecto

El sistema viene configurado con un usuario administrador por defecto:

- **Usuario**: admin
- **Contraseña**: admin
- **Departamento**: admin

## Notas Importantes

- Este sistema es ideal para entornos donde no se requiere un servidor de base de datos SQL
- Todos los datos se almacenan en un único archivo Excel
- Para entornos multiusuario, se recomienda establecer un proceso de sincronización
- Las operaciones pueden ser más lentas que con una base de datos SQL, especialmente con grandes volúmenes de datos